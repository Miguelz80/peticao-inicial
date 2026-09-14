# Índices ANS — reajuste anual de planos individuais/familiares

Teto de reajuste autorizado pela ANS. Cada índice vale para o período **maio de um ano
a abril do seguinte**; aplica-se o índice do período em que cai o **mês de aniversário
do contrato**.

## Como o índice entra no cálculo

```
devido[n] = devido[n-1] × (1 + índice_ans[ano do aniversário]) × (1 + faixa_etária)
```

Sobre a base já corrigida do ano anterior — capitaliza. **Sem arredondar a cada passo**:
arredonde só na exibição. Arredondar ano a ano introduz erro de centavos que cresce ao
longo de uma década (conferido contra planilha real do escritório: a cadeia de 9 anos
bate nos 9 passos sem arredondamento intermediário, e erra em 1 a 2 centavos com ele).

Faixa etária: só entra a **legítima** (Temas 952 e 1016 do STJ). Cada competência com
reajuste fora do mês de aniversário é confirmada uma a uma antes de entrar no devido —
incluir no devido um aumento que a peça vai impugnar apagaria o próprio pedido.

## Tabela

| Período (aniversário) | Índice |
|---|---|
| maio/2015 – abril/2016 | **13,55%** |
| maio/2016 – abril/2017 | **13,57%** |
| maio/2017 – abril/2018 | **13,55%** |
| maio/2018 – abril/2019 | **10,00%** |
| maio/2019 – abril/2020 | **7,35%** |
| maio/2020 – abril/2021 | **8,14%** |
| maio/2021 – abril/2022 | **−8,19%** (único negativo da série) |
| maio/2022 – abril/2023 | **15,50%** |
| maio/2023 – abril/2024 | **9,63%** |
| maio/2024 – abril/2025 | **6,91%** |
| maio/2025 – abril/2026 | **6,06%** |
| maio/2026 – abril/2027 | **5,11%** |

Série **conferida com a advogada em 11/09/2026**: os doze valores batem exatamente com
a tabela do escritório, e os conjuntos são idênticos — nenhum ano a mais nem a menos.

### Anteriores a 2015

O escritório trabalha com a série a partir de 2015. Caso cujo histórico alcance antes
disso **não trava**: a cadeia do valor devido recomeça no primeiro aniversário com
índice conhecido, a partir da mensalidade efetivamente paga, e o Calculador avisa. Ver
a seção seguinte.

Não preencher por estimativa. Índice errado contamina toda a cadeia e é invisível na
revisão da peça. Enquanto um ano estiver pendente, o Calculador **bloqueia** o caso cujo
histórico o alcance, em vez de pular o ano ou chutar.

## Procedência desta tabela

Os valores vieram da **planilha de cálculo do próprio escritório** (coluna "Índices
ANS" do arquivo `CÁLCULO DE REAJUSTE`), foram corroborados em publicações da ANS para
sete dos doze anos, e a série inteira foi **conferida com a advogada**, que enviou a
tabela do escritório: os doze valores coincidem, sem ano a mais nem a menos.

Nenhum valor foi escrito de memória ou estimado.

## Atenção ao ano de referência

Um erro fácil: notícia publicada em 2021 anunciando **−8,19%** se refere ao período
**maio/2021–abril/2022**, não a 2020. O índice de maio/2020–abril/2021 foi **8,14%**,
aplicado com atraso por causa da suspensão de reajustes na pandemia. Buscas na internet
confundem as duas coisas; a planilha do escritório está correta.
