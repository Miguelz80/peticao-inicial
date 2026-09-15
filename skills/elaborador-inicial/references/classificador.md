# Classificador — regras de decisão

Referência de uso. A especificação completa está em `docs/02-classificador-spec.md`
do repositório; a implementação, em `scripts/classificar.py`.

## Os dois eixos

**Eixo A — regime de cálculo.** Estrutural e verificável; o módulo de conferência
recalcula depois. Pode ser decidido pelo script.

| Regime | Sinal | Ação |
|---|---|---|
| `CALCULO_PRONTO` | ≥2 colunas de valor devido, preenchidas em ≥60% das linhas | só formatar |
| `FATURAMENTO_BRUTO` | colunas de base, nenhuma de valor devido | calcular do zero |
| `DEMONSTRATIVO_OPERADORA` | "Demonstrativo de Pagamento", "Data Baixa", "Tipo Lançamento" | calcular do zero |
| `AMBIGUO` | cálculo pela metade, uma só coluna de devido, cabeçalho desconhecido, planilhas divergentes | **perguntar** |
| `AUSENTE` | nada disso | **perguntar** |

> `Reajuste Aplicado` é o que a operadora cobrou. `Reajuste Devido` é o que seria
> legal. A comparação é sobre o cabeçalho inteiro, nunca por pedaço da palavra.

**Eixo B — tese.** Jurídico e irreversível. Nunca decidido sem confirmação humana.

## Fatos discriminantes

Cada um com valor, **fonte** e **citação literal**. Ausência de sinal é `DESCONHECIDO`.

| ID | Fato | Valores |
|----|------|---------|
| F1 | natureza da operadora | `AUTOGESTAO` · `COMERCIAL` |
| F2 | quem contratou | `PJ` · `PF_VIA_ASSOCIACAO` · `PF_DIRETO` |
| F3 | a PJ tem atividade econômica real | `SIM` · `NAO` |
| F4 | beneficiários são o mesmo núcleo familiar | `SIM` · `NAO` |
| F5 | há vínculo empregatício com a PJ | `SIM` · `NAO` |
| F6 | plano ativo ou cancelado | `ATIVO` · `CANCELADO` |
| F7 | houve reajuste por faixa etária no período | `SIM` · `NAO` |
| F8 | comarca / domicílio do autor | texto |
| F9 | idade do autor | número |
| F10 | houve ação anterior desistida | `SIM` · `NAO` |

## Árvore

```
F1 = AUTOGESTAO            → CASSI_AUTOGESTAO      (override: F2..F5 não mudam nada)
F1 = DESCONHECIDO          → BLOQUEIA (G4)
F2 = PJ  e F3=NAO,F4=SIM,F5=NAO  → EMPRESARIAL_FAMILIAR
F2 = PJ  e F3=SIM                → FORA_DO_PADRAO — devolve à advogada (G6)
F2 = PJ  e algum desconhecido    → BLOQUEIA (G1)
F2 = PF_VIA_ASSOCIACAO     → COLETIVO_POR_ADESAO
F2 = PF_DIRETO             → INDIVIDUAL_COMUM
F2 = DESCONHECIDO          → BLOQUEIA (G3)
```

## Sinais de narrativa

Alimentam F3/F4/F5/F6 **com citação obrigatória**. Confiança média ou baixa em fato que
sustenta a tese vira pergunta, mesmo que a árvore já tenha convergido.

| Trecho | Alimenta | Valor |
|---|---|---|
| "não possui atividade comercial" | F3 | NAO |
| "inativa há três/quatro anos" | F3 | NAO |
| "os beneficiários são o pai, a mãe e os irmãos" | F4 | SIM |
| "ex-sócios que saíram há mais de 10 anos" | F5 | NAO |
| "cancelei o plano em [data]" | F6 | CANCELADO |

## Gates

| Gate | Dispara quando |
|---|---|
| G1 | fato de que a tese depende está desconhecido |
| G2 | sinais conflitantes — mostra os dois lados, não escolhe |
| G3 | árvore ambígua |
| G4 | operadora não identificada |
| G5 | base de cálculo indefinida ou ausente |
| G6 | PJ com atividade real |
| G7 | pedido de outro tipo de peça (fora do escopo) |
| G8 | **sempre** — confirmação do Espelho antes de gerar |

## Sub-decisões que nunca são automáticas

Restituição simples × dobro · rescisão indireta × tutela de urgência · fundamentação da
gratuidade (PJ e PF diferem) · valor da causa · **quais reajustes de faixa etária são
legítimos** e portanto entram no valor devido (Temas 952 e 1016 do STJ).
