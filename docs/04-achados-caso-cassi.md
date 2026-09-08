# 04 — Achados do primeiro caso real (CASSI)

Dossiê completo de um caso CASSI já protocolado (11 arquivos + petição inicial em
DOCX). **Anonimizado:** nome, CPF, endereço, matrícula e número de processo foram
omitidos deste documento; os arquivos originais ficaram fora do repositório.

Serve a dois propósitos: é o corpus que faltava (perguntas A5 e B2) e é o primeiro
teste de realidade da spec do Classificador. **A spec não sobreviveu intacta.**

---

## 1. O que a spec errou

### 1.1 O Eixo A não previu o formato que realmente chegou

A spec assume que o insumo de cálculo é planilha (`.xlsx`/`.csv`) e decide por
cabeçalho de coluna. **Neste caso não havia planilha nenhuma.** O insumo foi um PDF
"BEN120 – Demonstrativo de Pagamento de Faturas", digitalizado, com OCR de qualidade
ruim: colunas embaralhadas, valores soltos do seu mês, `2.097.01` no lugar de
`2.097,01`, `2.526,8S9`, `08/08:2023`.

Pela regra atual o Classificador cairia em `AUSENTE` e bloquearia um caso
perfeitamente trabalhável.

> **Correção necessária:** o Eixo A precisa de um terceiro regime,
> `DEMONSTRATIVO_OPERADORA`, e de um caminho para PDF sem camada de texto.

### 1.2 Metade dos documentos não tem texto extraível

| Documento | Camada de texto |
|---|---|
| demonstrativo + regulamento | ✅ texto |
| carteira do plano | ✅ texto |
| proposta de adesão | ✅ texto |
| petição inicial | ✅ texto |
| **extrato bancário** | ❌ digitalizado |
| **documentação pessoal** | ❌ digitalizado |
| **procuração** | ❌ digitalizado |
| **comprovante de residência** | ❌ digitalizado |
| **contrato de honorários** | ❌ digitalizado |
| **comprovante de protocolo** | ❌ digitalizado |

Cinco de dez. O extrato bancário — que a spec usa para fundamentar gratuidade — é um
deles. Extração de texto não resolve; é necessário caminho de leitura por imagem, com
**penalidade de confiança** para todo fato que venha daí.

### 1.3 Um arquivo pode conter vários documentos

`DEMONSTRATIVO E CONTRATO.pdf` são **dois documentos**: páginas 1–3 o demonstrativo de
pagamento (digitalizado), páginas 4–13 o regulamento da CASSI (nativo digital). A
triagem da spec assume um papel por arquivo. Precisa segmentar por página.

### 1.4 Os dois eixos não são independentes

Foi a suposição mais errada da spec. Nesta peça **não existe tabela de reajuste devido
calculada pelos índices ANS**. A tese de autogestão pede exibição de documentos e
distribuição dinâmica do ônus da prova, e remete a apuração à liquidação de
sentença/perícia. A tutela pede limitação a um **valor histórico anterior**, não a um
valor calculado por índice.

> **Correção necessária:** o regime de cálculo é função da tese, não só do formato de
> entrada. Em `CASSI_AUTOGESTAO` o módulo 2 provavelmente **não roda** o cálculo ANS.

### 1.5 Fatos que faltavam na árvore

- **F9 — idade do autor.** 81 anos acionou prioridade de tramitação (art. 71 do
  Estatuto da Pessoa Idosa + art. 1.048, I, CPC), bloco obrigatório que a spec não tinha.
- **F10 — reajuizamento.** A peça tem um capítulo inteiro sobre desistência de ação
  anterior em outra comarca e competência concorrente. É bloco condicional, dispara
  por fato processual, não pela tese.

### 1.6 O extrato não virou prova de gratuidade

O briefing (Exemplo Tipo 4) prevê extrair o saldo e vincular ao pedido de gratuidade.
**Não foi o que a peça fez.** A gratuidade foi fundamentada pelo peso da mensalidade
sobre a aposentadoria e pela presunção do art. 99, §3º, CPC — sem citar saldo nenhum.
O extrato foi só juntado.

---

## 2. Divergências numéricas dentro da peça protocolada

Achados de Conferência (módulo 4) sobre um documento que **já foi a protocolo**.

### 2.1 As duas tabelas da peça informam percentuais diferentes para o mesmo reajuste

| Reajuste | Tabela de histórico (imagem 1) | Tabela da tutela (imagem 2) |
|---|---|---|
| 2023 | **12,79%** | **12,88%** |
| 2024 | **14,33%** | **14,26%** |
| 2025 | 23,88% | 23,88% |

Causa raiz: as duas partiram de valores diferentes para a mensalidade de 03/2023 —
**R$ 2.525,09** numa, **R$ 2.526,89** na outra. O corpo do texto repete os percentuais
da primeira tabela.

### 2.2 A tutela pede um valor que não existe em nenhuma tabela

O pedido de tutela requer limitar a mensalidade a **R$ 2.526,89**. A tabela de
histórico da própria peça lista apenas 2.238,77 · 2.525,09 · 2.886,98 · 3.576,39.
O valor pedido não é nenhum deles.

### 2.3 O valor da causa não bate com a justificativa que a própria peça dá

- Valor da causa: **R$ 43.041,98**
- Restituição estimada: **R$ 21.520,99**
- Relação: exatamente **2 ×** a restituição.

Mas o texto justifica o valor como "restituição + projeção da diferença mensal para os
próximos 12 meses". Diferença mensal (3.576,39 − 2.526,89) = 1.049,50; × 12 =
12.594,00; somada à restituição daria **R$ 34.114,99**, não 43.041,98.

Ou a fórmula é outra, ou a justificativa está desatualizada. **Pergunta A6 continua
aberta, e agora com urgência** — é o módulo 4 pegando exatamente o tipo de erro que
justifica sua existência.

### 2.4 O que confere

Aumento acumulado de R$ 1.337,62 e 59,75% conferem (3.576,39 − 2.238,77, e a soma das
três diferenças). A tabela de histórico é internamente consistente.

> Os valores do demonstrativo digitalizado **não** foram usados como contraprova: o OCR
> daquele arquivo é ruim demais para servir de referência.

---

## 3. O achado mais importante: as tabelas são imagens

As duas tabelas centrais da peça — o **histórico de reajustes** e os **requisitos da
tutela de urgência** — estão embutidas como PNG (`image4.png`, `image5.png`). A própria
peça admite: *"conforme tabela demonstrativa anexa, elaborada em formato de imagem para
facilitar a visualização"*.

Isso é a colisão frontal com o requisito não negociável do projeto. Se um valor da
tabela estiver errado — e o §2.1 mostra que **estava** —, a colega que opera não
consegue corrigir: teria que regerar a imagem.

> **Decisão de projeto:** no `elaborador-inicial` essas duas tabelas nascem como `w:tbl`
> nativa, célula editável. É requisito, não preferência. (Ver pergunta B4, agora
> respondida pela prática — e respondida no sentido oposto ao desejado.)

---

## 4. Formatação: o que o DOCX real confirma e o que contraria

| Item | Esperado (skill `tatiana-pecas-processuais`) | Real |
|---|---|---|
| A4 `11906×16838` | ✅ | ✅ confere |
| Margens `2037/1562/1560/1560` | ✅ | ✅ confere |
| Fonte Segoe UI | única permitida | **826 runs Segoe UI + 113 runs `Quattrocento Sans`** |
| Timbre em imagem | obrigatório | ✅ `image1.png` (44 KB) e `image2.png` (60 KB), 3 headers + 3 footers |
| Proteção de documento | proibida | `<w:documentProtection />` **vazio** — elemento sem atributos, não trava nada. Inofensivo, mas o gerador não deve reproduzi-lo |

A presença de `Quattrocento Sans` em 113 runs contraria a regra "nunca usar fonte que
não seja Segoe UI". Provavelmente resíduo de colagem.

---

## 5. Dados de referência confirmados

**CASSI** — Caixa de Assistência dos Funcionários do Banco do Brasil
- CNPJ: **33.719.485/0001-27** — assim no demonstrativo emitido pela própria CASSI *e*
  na petição protocolada, dois documentos independentes.
- Sede: Setor de Autarquias Sul (SAS), Quadra 03, Bloco E, Edifício CASSI,
  Brasília/DF, CEP 70070-030.
- Natureza: autogestão → `F1 = AUTOGESTAO` → tese `CASSI_AUTOGESTAO`.

> ⚠️ **Divergência a resolver.** A skill `corretor-inicial-cassi-revisional` registra o
> CNPJ **33.594.914/0001-24**. Os dois documentos reais dizem **33.719.485/0001-27**.
> Um dos dois está errado, e o da skill é o que vai para a qualificação da ré em toda
> peça futura. Ver pergunta D1.

**Plano:** CASSI Família II, registro ANS nº 34665-9. Cancelamento após 60 dias de
inadimplência (Cláusula 22ª do Contrato de Adesão) — fundamento do *periculum in mora*.

---

## 6. Estrutura da peça CASSI (base para o modelo)

Confirmada como modelo para a tese `CASSI_AUTOGESTAO`:

```
I.    DOS FATOS
II.   DA REGULARIDADE DO REAJUIZAMENTO E DA COMPETÊNCIA CONCORRENTE   [condicional]
III.  DO DIREITO
      A. Regime jurídico dos planos de autogestão e controle judicial dos reajustes
      B. Dever de transparência qualificada e extrato pormenorizado do reajuste
      C. Exibição de documentos e distribuição dinâmica do ônus da prova (arts. 396-404
         e 373, §1º, CPC) — com rol de 10 documentos a exibir
      D. Abusividade concreta dos reajustes            [tabela — HOJE IMAGEM]
      E. Restituição dos valores pagos a maior (arts. 876 e 884, CC) — SIMPLES
IV.   DA TUTELA DE URGÊNCIA (art. 300 CPC)             [tabela — HOJE IMAGEM]
V.    DA GRATUIDADE DE JUSTIÇA (arts. 98-99 CPC; presunção do art. 99, §3º)
VI.   PRIORIDADE DE TRAMITAÇÃO                          [condicional: idade ≥ 60]
VII.  DOS PEDIDOS (15 itens)
VIII. DO VALOR DA CAUSA (art. 292, §3º, CPC — por estimativa)
```

Confirma o desenho da tese CASSI na spec: **restituição simples** (arts. 876/884 do CC,
sem art. 42 do CDC), CDC afastado com fundamentação própria, Súmula 608 tratada de
frente, e nenhuma menção a falso coletivo. Sinistralidade/VCMH aparece como **objeto de
exibição de documentos**, não como tese de abusividade autônoma.

Fundamentos usados que não estavam mapeados: arts. 113, 187, 421, 421-A e 422 do CC.

**Ordem de assinatura:** Gabriel primeiro, Tatiana em segundo — em ação de **saúde**,
comarca de **Salvador/BA**. Contraria a regra do briefing ("Tatiana antes de Gabriel em
saúde/consumidor na Bahia"). Ver pergunta D2.
