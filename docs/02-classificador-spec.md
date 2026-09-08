# 02 — Módulo Classificador (especificação)

> Status: **especificação para validação**. Ainda não é código final.
> Objetivo: decidir (a) o regime de cálculo e (b) a tese/modelo aplicável — e,
> principalmente, **saber quando não decidir**.

## 0. Princípio de projeto

Os dois eixos que o Classificador decide têm perfis de risco **opostos**, e por isso
não podem ter o mesmo tratamento:

| | Eixo A — regime de cálculo | Eixo B — tese aplicável |
|---|---|---|
| Natureza do sinal | Estrutural (existem ou não colunas de valor devido) | Jurídica (quem contratou, natureza da operadora, fatos do caso) |
| Erro é detectável depois? | **Sim** — o módulo 4 (Conferência) recalcula e compara | **Não** — sai peça inteira com fundamentação errada |
| Custo do erro | Retrabalho | Pior cenário do projeto |
| Postura | Pode decidir sozinho, registrando a evidência | **Nunca decide sozinho sem confirmação** |

Daí a regra estruturante: **o Eixo A é automático e verificável; o Eixo B é sempre
confirmado por humano antes de gerar.**

## 1. Contrato de entrada e saída

**Entrada:** lista de arquivos enviados no chat (`.xlsx`, `.csv`, `.pdf`, `.docx`,
`.txt`) + texto livre eventual da operadora.

**Saída:** um objeto `dossie` (JSON) + um **Espelho de Classificação** em português,
apresentado no chat para confirmação.

```jsonc
{
  "status": "PRONTO_PARA_GERAR | PRECISA_CONFIRMACAO | BLOQUEADO",
  "documentos": [ { "arquivo": "...", "papel": "CALCULO_PRONTO", "confianca": 0.0-1.0,
                    "evidencias": ["cabeçalho contém 'Valor Devido'"] } ],
  "eixo_a": { "regime": "CALCULO_PRONTO | FATURAMENTO_BRUTO | AUSENTE | AMBIGUO",
              "planilha_base": "...", "evidencias": [], "confianca": 0.0 },
  "eixo_b": { "tese": "EMPRESARIAL_FAMILIAR | COLETIVO_POR_ADESAO | CASSI_AUTOGESTAO |
                       INDIVIDUAL_COMUM | FORA_DO_PADRAO | INDEFINIDA",
              "modelo_docx": "...", "evidencias": [], "confianca": 0.0,
              "descartadas": [ { "tese": "...", "porque": "..." } ] },
  "fatos": { "F1": {"valor": "...", "fonte": "...", "citacao": "..."}, "...": {} },
  "subdecisoes": { "plano_status": "...", "restituicao": "...", "gratuidade": "...",
                   "foro": "...", "ordem_assinatura": "..." },
  "lacunas": ["..."],
  "perguntas": [ { "id": "Q1", "texto": "...", "opcoes": [], "bloqueante": true } ],
  "log": "trilha de auditoria da decisão"
}
```

Regra: **`lacunas` ou `perguntas` não vazias com `bloqueante: true` ⇒ `status` nunca
pode ser `PRONTO_PARA_GERAR`.** Essa é a única trava que impede geração no escuro.

## 2. Camada 1 — Triagem documental

Antes de qualquer decisão jurídica, descobrir **o que é cada arquivo**. O nome do
arquivo é dica, nunca prova.

```
PAPEIS = { CALCULO_PRONTO, FATURAMENTO_BRUTO, TRANSCRICAO, CONTRATO_SOCIAL,
           CONTRATO_PLANO, CARTEIRINHA, BOLETO, EXTRATO_BANCARIO,
           DOC_PESSOAL, INDEFINIDO }

para cada arquivo:
    texto, tabelas = extrair(arquivo)          # Python: openpyxl / pdf → texto / docx

    se tem_tabelas_com_cabecalho:
        papel = classificar_planilha(tabelas)   # → CALCULO_PRONTO | FATURAMENTO_BRUTO
    senao:
        papel = classificar_por_marcadores(texto)

    # marcadores determinísticos, não semânticos:
    #   CONTRATO_SOCIAL   : "contrato social", "cláusula", "capital social", CNPJ + "sócios"
    #   EXTRATO_BANCARIO  : "saldo disponível", "extrato", "agência/conta", "bloqueio judicial"
    #   TRANSCRICAO       : marcas de fala ("[00:", "Entrevistador:", turnos alternados)
    #   CARTEIRINHA       : "nº do beneficiário", "acomodação", "cobertura", "abrangência"
    #   BOLETO            : "vencimento", "nosso número", "cedente", linha digitável

    se papel == INDEFINIDO:
        registrar em lacunas  →  perguntar "o que é este arquivo?" (não descartar)
```

Arquivo não reconhecido **não é ignorado em silêncio** — vira pergunta. Um documento
de suporte não lido é uma prova que ficou fora da peça.

## 3. Camada 2 — Eixo A: regime de cálculo

### 3.1 Normalização de cabeçalho

```
normalizar(h) = minúsculas(sem_acento(colapsar_espaços(strip(h))))
```

Conjuntos (com sinônimos observados na prática — **completar com planilhas reais**,
ver pergunta A5):

```
COLS_DEVIDO = { "reajuste devido", "valor devido", "diferenca",
                "diferença mensal", "valor correto" }
COLS_BASE   = { "mes/ano", "mes ano", "competencia", "valor pago",
                "valor", "valor total", "referencia" }
COLS_RUIDO  = { "reajuste aplicado", "tipo de reajuste", "percentual aplicado" }
```

> **Armadilha crítica:** `"Reajuste Aplicado"` (o que a operadora cobrou) e
> `"Reajuste Devido"` (o que seria legal) diferem por uma palavra. Um `match` por
> substring em `"reajuste"` classificaria um faturamento bruto como cálculo pronto e
> a skill pularia o cálculo inteiro. **A comparação é sobre o cabeçalho normalizado
> inteiro, nunca por substring.**

### 3.2 Regra de decisão

```
d = |cabeçalhos ∩ COLS_DEVIDO|
b = |cabeçalhos ∩ COLS_BASE|
preenchimento = fração de linhas com valor numérico nas colunas de COLS_DEVIDO

se d >= 2 e preenchimento >= 0.6      → CALCULO_PRONTO      (ação: só formatar)
senão se d == 0 e b >= 2              → FATURAMENTO_BRUTO   (ação: calcular)
senão se d >= 1 e preenchimento < 0.6 → AMBIGUO  # planilha começada e não terminada
senão se d == 1                       → AMBIGUO  # cálculo parcial
senão                                 → AUSENTE  # nenhuma planilha de cálculo
```

Casos que forçam pergunta:

- **Mais de uma planilha com vereditos diferentes** → perguntar qual é a base de
  cálculo (não escolher a maior, nem a mais recente, nem a primeira).
- **`AMBIGUO`** → mostrar as colunas encontradas e perguntar se o cálculo está pronto
  ou deve ser refeito do zero.
- **`AUSENTE` com pedido de restituição** → faltam dados; bloquear.

### 3.3 Gancho para o módulo 4

Mesmo em `CALCULO_PRONTO`, o dossiê guarda os valores de origem célula a célula. A
Conferência recalcula por conta própria e compara — inclusive contra a planilha
"pronta", que também pode vir errada do cliente. *(Não implementar nesta fase.)*

## 4. Camada 3 — Eixo B: tese aplicável

### 4.1 Fatos discriminantes

Cada fato tem valor `SIM | NAO | DESCONHECIDO`, **fonte** (arquivo + local) e, quando
vier de narrativa, **citação literal**. Regra absoluta:

> **Ausência de sinal é `DESCONHECIDO`, jamais `NAO`.**
> Silêncio da transcrição sobre vínculo empregatício não prova que não existe vínculo.

| ID | Fato | Fonte preferencial |
|----|------|--------------------|
| F1 | Natureza jurídica da operadora ré (autogestão × comercial) | Cadastro `references/operadoras.md`, por CNPJ |
| F2 | Quem é o contratante (PJ / PF via associação-sindicato / PF direto) | Contrato do plano, carteirinha, boleto |
| F3 | A PJ tem atividade econômica real | Contrato social, transcrição, extrato |
| F4 | Beneficiários são exclusivamente do mesmo núcleo familiar | Carteirinha, transcrição |
| F5 | Há vínculo empregatício entre beneficiários e a PJ | Transcrição, contrato social |
| F6 | Plano ativo ou já cancelado pela parte autora | Transcrição, boletos recentes |
| F7 | Houve reajuste por faixa etária no período | Planilha (coluna "Tipo de Reajuste") |
| F8 | Comarca / domicílio do autor | Documento pessoal, contrato |

### 4.2 Árvore de decisão (discriminantes duros primeiro)

A tese **não é escolhida por pontuação**. Ela é escolhida por uma árvore de fatos; a
narrativa só *alimenta* fatos, nunca sobrepõe um discriminante duro.

```
se F1 == AUTOGESTAO:
    tese = CASSI_AUTOGESTAO
    # override total: autogestão não comporta falso coletivo empresarial;
    # Súmula 608/STJ exclui o CDC. F2..F5 não mudam esta conclusão.
    descartar(EMPRESARIAL_FAMILIAR, "operadora é autogestão — Súmula 608/STJ")

senão se F1 == DESCONHECIDO:
    BLOQUEAR("Operadora não identificada ou fora do cadastro. Sem saber se é
              autogestão, qualquer tese pode estar errada.")     # G4

senão se F2 == PJ:
    se F3 == NAO e F4 == SIM e F5 == NAO:  tese = EMPRESARIAL_FAMILIAR
    senão se F3 == SIM:                    tese = FORA_DO_PADRAO   # escalar
    senão:                                 AMBIGUO → perguntar F3/F4/F5 faltantes

senão se F2 == PF_VIA_ASSOCIACAO:  tese = COLETIVO_POR_ADESAO
senão se F2 == PF_DIRETO:          tese = INDIVIDUAL_COMUM
senão:                             AMBIGUO → perguntar F2
```

`FORA_DO_PADRAO` (PJ com atividade econômica real, funcionários de verdade) **não é
erro do sistema** — é caso que esta skill não cobre. Ela para e devolve à advogada.

### 4.3 Sinais de narrativa → fatos

A transcrição alimenta F3/F4/F5/F6 com **citação obrigatória**:

| Trecho (exemplo real do briefing) | Alimenta | Valor | Confiança |
|---|---|---|---|
| "não possui atividade comercial" | F3 | NAO | alta |
| "inativa há cerca de três a quatro anos" | F3 | NAO | alta |
| "os beneficiários são o pai, a mãe e os dois irmãos" | F4 | SIM | alta |
| "irmãos ex-sócios que saíram há mais de 10 anos" | F5 | NAO | média |
| "cancelei o plano em [data]" | F6 | CANCELADO | alta |

Confiança **média ou baixa em fato que sustenta a tese ⇒ vira pergunta**, mesmo que a
árvore já tenha convergido. O ônus de fundamentar o falso coletivo é do escritório; a
skill não pode inventar o fato que a peça vai afirmar em juízo.

### 4.4 Mapa tese → modelo → blocos obrigatórios

As quatro teses abaixo estão **confirmadas no escopo** desta fase (08/09/2026).

| Tese | Modelo DOCX | Blocos que a peça **tem** que ter |
|---|---|---|
| `EMPRESARIAL_FAMILIAR` | `PETIÇÃO INICIAL-MODELO APENAS RESTITUIÇÃO.docx` | CDC por equiparação (arts. 2º e 29) **+** reconhecimento do plano empresarial como familiar; equiparação a individual para fins de reajuste; sinistralidade sem prova atuarial do grupo; Tema 952/STJ; gratuidade fundamentada **para PJ** |
| `COLETIVO_POR_ADESAO` | `MODELO PETIÇÃO INICIAL COLETIVO POR ADESÃO.docx` | falso coletivo **por adesão** (PF via associação/sindicato); tutela de urgência para readequação |
| `CASSI_AUTOGESTAO` | a definir (ver pergunta B2) | **remover** falso coletivo e Súmula 608 como incidência automática; fundamentar por Lei 9.656/98, estatuto/regulamento, mutualismo e vedação ao enriquecimento sem causa; exigir ata de aprovação + estudo atuarial + comunicação prévia; Tema 952/STJ **permanece** |
| `INDIVIDUAL_COMUM` | a definir (ver pergunta B2) | revisional individual comum |

Blocos que valem em **todas** as teses (nunca remover): Tema 952/STJ (faixa etária),
Tema 610/STJ (prescrição trienal), gratuidade, dispensa de audiência de conciliação,
processo 100% digital, correção (Súmula 362) e juros (Súmula 54).

## 5. Gate de segurança

Bloqueiam a geração:

| ID | Condição | O que a skill faz |
|----|----------|-------------------|
| G1 | Fato de que a tese escolhida depende está `DESCONHECIDO` | Pergunta o fato, citando qual documento resolveria |
| G2 | Sinais **conflitantes** (ex.: transcrição diz "empresa inativa", contrato social mostra faturamento) | Mostra os dois lados com citação e pergunta qual prevalece |
| G3 | Árvore cai em `AMBIGUO` ou empate entre teses | Múltipla escolha com a evidência de cada opção |
| G4 | Operadora não identificada / fora do cadastro | Bloqueia — sem F1 não há tese confiável |
| G5 | Eixo A `AMBIGUO`, ou várias planilhas divergentes | Pergunta qual é a base de cálculo |
| G6 | Tese = `FORA_DO_PADRAO` | Para e devolve à advogada com o motivo |
| G7 | Pedido é de outro tipo de peça (réplica, recurso…) | Recusa por escopo e indica a skill correta |
| G8 | **Toda geração, sempre** | Exige confirmação explícita do Espelho (ver §7) |

### Sub-decisões que nunca são automáticas

Mesmo com a tese confirmada, estas ficam marcadas como **decisão humana** no dossiê:

- **Restituição simples × em dobro** (art. 42, § único, CDC × art. 876, CC) — e, na
  tese CASSI, se o CDC sequer incide, a dobra perde base direta.
- **Rescisão indireta × tutela de urgência** — depende de F6. Com F6 conhecido a
  skill *propõe*; com F6 desconhecido, **pergunta**.
- **Fundamentação da gratuidade** — PJ e PF têm fundamentações diferentes; para PJ não
  serve a hipossuficiência genérica.
- **Valor da causa** (ver pergunta A6).

## 6. Formato das perguntas (a operadora não é técnica)

Toda pergunta bloqueante segue esta forma:

```
[O que preciso saber, em português simples — sem jargão de sistema]

Encontrei isto:
  • "<citação literal>" — <arquivo>, <onde>

Opções:
  1) <opção em linguagem leiga>  → o que muda na peça
  2) <opção em linguagem leiga>  → o que muda na peça
  3) Não sei / vou verificar     → paro aqui e não gero nada
```

A opção 3 existe sempre. "Não sei" tem que ser uma resposta legítima e sem atrito —
senão a operadora chuta para destravar o sistema, e o chute vira tese na peça.

## 7. Espelho de Classificação

Artefato apresentado **antes** de gerar qualquer coisa:

```
ESPELHO DE CLASSIFICAÇÃO — <cliente>

Documentos reconhecidos
  planilha_faturamento.xlsx → faturamento bruto (sem colunas de valor devido)
  reuniao_onboarding.txt    → transcrição
  extrato.pdf               → extrato bancário (saldo R$ 12,43 + bloqueio judicial)

Cálculo:  PRECISA SER CALCULADO — a planilha não traz reajuste devido nem diferença.

Tese:     FALSO COLETIVO EMPRESARIAL
  porque  contratante é PJ (CNPJ ...), beneficiários são só a família
          ("o pai, a mãe e os dois irmãos"), empresa "inativa há três a quatro anos"
  descartei  CASSI (operadora é comercial) · coletivo por adesão (não há associação)

A decidir com você
  • Plano ativo ou cancelado? → define rescisão indireta × tutela de urgência
  • Restituição simples ou em dobro?
  • Gratuidade: uso o saldo de R$ 12,43 do extrato como prova? (autora é PJ)

Confirma a tese acima para eu gerar a peça? (sim / corrigir)
```

O espelho é gravado junto com o `.docx` gerado. Se uma peça sair com tese errada, dá
para auditar **qual evidência** levou até lá — e corrigir a regra, não só o documento.

## 8. Anti-regras

O Classificador **nunca**:

1. deduz a tese só pela operadora (Unimed ≠ automaticamente falso coletivo);
2. trata ausência de evidência como evidência em contrário;
3. usa nome de arquivo como base única de classificação;
4. gera peça com confirmação parcial ("sim" a uma pergunta ≠ "sim" ao espelho);
5. escolhe entre planilhas divergentes por conta própria;
6. preenche fato do caso concreto com fórmula genérica para completar o bloco da tese;
7. classifica ou gera peça que não seja **petição inicial** (escopo desta fase);
8. inventa lei, súmula, tema ou julgado — nem "provisoriamente".

## 9. Cobertura de teste mínima antes de virar código final

- 1 fixture por tese (4) × regime de cálculo pronto e bruto;
- 1 fixture de `AMBIGUO` no Eixo A (planilha com cálculo pela metade);
- 1 fixture com **`"Reajuste Aplicado"` sem `"Reajuste Devido"`** (a armadilha do §3.1);
- 1 fixture de sinais conflitantes (G2);
- 1 fixture de PJ com atividade real (`FORA_DO_PADRAO`, G6);
- 1 fixture de operadora fora do cadastro (G4);
- 1 fixture de transcrição silenciosa sobre vínculo empregatício → tem que perguntar,
  não concluir.
