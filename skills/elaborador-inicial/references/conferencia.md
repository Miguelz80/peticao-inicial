# Conferência — catálogo de verificações

Última barreira antes de liberar a peça. **Cada verificação existe porque um erro real
passou**: as duas peças protocoladas analisadas em `docs/04` e `docs/05` reprovam aqui.

`BLOQUEIA` impede a liberação do documento. Não existe "avisar e seguir".

## Consistência do cálculo

| | O que verifica | De onde veio |
|---|---|---|
| **C3** | total pago − total devido fecha com o total da coluna Diferença | planilha real: 133.776,67 − 80.153,61 = 53.623,06, mas o total dizia 36.738,93 |
| **C4** | a janela da restituição termina na última competência da série | planilha real: janela congelada dois meses antes; a peça saiu desatualizada |
| **C11** | toda competência com reajuste fora do aniversário tem decisão humana | planilha real: abril/2018 (9,10%) e janeiro/2021 (21,72%) sem tipo declarado |
| **C13** | o cálculo não terminou bloqueado (ex.: ano sem índice ANS) | — |

## A peça contra os valores de origem

| | O que verifica | De onde veio |
|---|---|---|
| **C6** | cada valor nomeado na peça bate com o cálculo (restituição, diferença mensal, valor pago e devido atuais) | requisito central do módulo |
| **C2** | o mesmo reajuste não aparece com percentuais divergentes em pontos diferentes | peça CASSI: 12,79% numa tabela, 12,88% em outra |
| **C1** | valor pedido como patamar/limite existe na série calculada | peça CASSI: tutela pedia R$ 2.526,89, ausente da própria tabela |
| **C5** | valor da causa confere com a fórmula que a peça declara | peça CASSI: era 2× a restituição, mas o texto dizia restituição + 12 meses |

C2 agrupa percentuais que diferem por menos de 0,3 ponto — perto demais para serem
reajustes distintos, longe demais para serem o mesmo número.

## O DOCX cumpre o requisito de edição

| | O que verifica | Observação |
|---|---|---|
| **C8** | imagem grande no corpo (>60 KB) — quase sempre tabela renderizada | peça CASSI: PNG de 151 KB e 134 KB. O timbre (44 KB) fica abaixo do corte |
| **C9** | `w:documentProtection` **com atributos** | o elemento vazio da peça CASSI é inofensivo e não bloqueia |
| **C10** | content control **travado** (`w:lock`) | as duas peças reais têm `w:sdt` sem trava — são editáveis; bloquear por `w:sdt` reprovaria todo documento do escritório |
| **C14** | fonte fora de Segoe UI (alerta) | peça CASSI: Quattrocento Sans; SulAmérica: Arial Unicode MS, Arimo |

## Uso

```python
from conferir import conferir
c = conferir(resultado_do_calculo,
             texto_peca=texto, caminho_docx=caminho,
             declarados={"restituicao": "R$ 38.576,42"},
             formula_valor_da_causa="restituicao+12x_diferenca",
             valor_da_causa="R$ 62.837,06")
print(c.relatorio())
if not c.liberado:
    ...   # não entrega o documento
```
