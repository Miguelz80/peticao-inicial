# 05 — Achados do segundo caso real (SulAmérica, coletivo)

Dossiê de 20 documentos, incluindo pela primeira vez uma **planilha de cálculo pronta**
(entrada Tipo 1) e um segundo dossiê separado só de gratuidade. Anonimizado; nenhum
arquivo do caso foi versionado.

## 1. A entrada Tipo 1 finalmente apareceu (fecha A5)

O arquivo `CÁLCULO DE REAJUSTE` traz exatamente as colunas que o briefing descrevia:

```
Mês/Ano | Valor Pago | Reajuste Aplicado | Tipo de Reajuste |
Reajuste Devido | Valor Devido | Diferença
```

mais o resumo lateral com `Valor Pago (Atual)`, `Valor Devido`, `Diferença (Mensal)` e
`Restituição (Últimos 3 anos)`. Os conjuntos de cabeçalho do Classificador estavam
certos — inclusive a distinção entre **"Reajuste Aplicado"** (o que a operadora cobrou)
e **"Reajuste Devido"** (o que seria legal), que aparecem lado a lado na planilha real.
A armadilha do §3.1 da spec não era hipotética.

Um detalhe a tratar: o arquivo chega em **PDF**, não em `.xlsx`. É Tipo 1 de conteúdo
e demonstrativo de forma. A detecção precisa reconhecer as colunas no texto extraído,
não só num grid de planilha.

## 2. A fórmula do valor devido está confirmada

A cadeia de 9 anos foi reproduzida **exatamente**, nos 9 passos:

```
devido[n] = devido[n-1] × (1 + índice ANS do ano do aniversário)
```

Aniversário do contrato em julho; aplica-se o índice do período ANS iniciado em maio do
mesmo ano. Base inicial = valor pago na primeira competência com valor real.

| | calculado | planilha |
|---|---|---|
| julho/2018 (10,00%) | 666,00 | 666,00 |
| julho/2019 (7,35%) | 714,95 | 714,95 |
| julho/2020 (8,14%) | 773,14 | 773,14 |
| julho/2021 (−8,19%) | 709,82 | 709,82 |
| julho/2022 (15,50%) | 819,84 | 819,84 |
| julho/2023 (9,63%) | 898,80 | 898,80 |
| julho/2024 (6,91%) | 960,90 | 960,90 |
| julho/2025 (6,06%) | 1.019,13 | 1.019,13 |
| julho/2026 (5,11%) | 1.071,21 | 1.071,21 |

**Não se arredonda a cada passo.** Arredondando ano a ano a cadeia erra 1 a 2 centavos;
carregando precisão cheia e arredondando só na exibição, bate nos nove.

## 3. Achado de conferência: a linha "Total" não fecha consigo mesma

A linha de totais imprime três números que não se reconciliam entre si:

| | |
|---|---|
| Total Valor Pago | R$ 133.776,67 |
| Total Valor Devido | R$ 80.153,61 |
| Total Diferença | R$ 36.738,93 |

`133.776,67 − 80.153,61 = 53.623,06`, não `36.738,93`. A verificação não depende de
reler a planilha: os próprios três totais impressos se contradizem.

Somando a coluna Diferença mês a mês chega-se a cerca de **R$ 57 mil**. Já
R$ 36.738,93 é o valor que a planilha também exibe como **"Restituição (últimos 3
anos)"** — e uma soma dos últimos 36 meses dá ordem de grandeza compatível (~R$ 36,2
mil). A explicação provável é que a célula de total da coluna Diferença aponta para a
restituição trienal em vez de somar a coluna.

**Não contaminou a peça.** A petição pede `R$ 36.738,93` como restituição simples dos
últimos três anos, que é o uso correto desse número. O risco existia e não se
materializou aqui — mas é exatamente o que o módulo 4 precisa acusar.

## 4. Reajustes fora do aniversário não entraram no devido

Duas competências têm reajuste aplicado fora do mês de aniversário, com a coluna
"Tipo de Reajuste" **em branco**:

| Competência | Reajuste aplicado | Entrou no devido? |
|---|---|---|
| abril/2018 | 9,10% | não |
| janeiro/2021 | 21,72% | não |

Se algum deles for **faixa etária legítima**, deveria ter entrado no valor devido
(resposta A2). Se for reajuste sem previsão, está correto ficar de fora — é justamente
o que se impugna. A planilha não distingue: deixa a coluna vazia.

É a pergunta **A9** aparecendo em dado real. O Calculador vai precisar sinalizar toda
competência com reajuste fora do aniversário e perguntar, uma a uma.

## 5. Esta peça usa tabelas nativas

Ao contrário da peça CASSI, esta tem **10 tabelas nativas** (`w:tbl`) e só imagens
pequenas (timbre e ícones, de 70 B a 44 KB) — nenhuma tabela em PNG.

Ou seja, a prática do escritório **não é uniforme**: tabela em imagem é característica
de algumas peças, não do padrão. Isso torna a decisão D5 menos disruptiva do que
parecia — gerar tabela nativa aproxima o `elaborador-inicial` do que boa parte das
peças já faz.

## 6. Dossiê de gratuidade muito mais rico que o previsto

O segundo zip é só de prova de hipossuficiência: extratos bancários, IRPF (declaração e
recibo), comprovantes de aluguel, gastos, curso preparatório e ajuda de terceiro no
pagamento do plano. Mais um **laudo médico** no primeiro zip.

A spec tratava gratuidade como "extrair o saldo do extrato". É bem mais: um conjunto de
documentos que compõe renda × despesa. E o laudo médico sugere um bloco condicional
novo — prioridade por doença grave —, que a tabela de requerimentos preliminares da
peça CASSI já listava.

## 7. Consequências para o desenho

- `references/indices-ans.md` criado com a série 2015–2026 (§ procedência lá).
- Eixo A: `CALCULO_PRONTO` precisa ser detectável em PDF, não só em grade de planilha.
- Módulo 2: fórmula confirmada; não arredondar entre anos; sinalizar reajuste fora do
  aniversário.
- Módulo 4: comparar `Total Pago − Total Devido` com `Total Diferença`, e a soma da
  coluna com o total impresso. Este caso reprova nas duas.
- Novo fato **F11 — doença grave** (laudo médico), para prioridade de tramitação.


## 8. A janela da restituição da planilha foi identificada (pergunta A7)

Reconstruindo a série no Calculador, **todos os valores mensais reproduzem a planilha
exatamente**. Só a restituição diverge:

| | |
|---|---|
| 36 meses até a última competência (julho/2026) | R$ 38.576,42 |
| **37 competências, maio/2023 a maio/2026** | **R$ 36.738,93** — bate com a planilha |

Duas coisas explicam a diferença, e as duas são a pergunta A7:

1. **O marco está dois meses atrás do fim da série.** A janela termina em maio/2026, mas
   a planilha vai até julho/2026. Parece marco congelado na data em que se calculou, com
   a série estendida depois sem atualizar a restituição — **a peça saiu com a restituição
   desatualizada em dois meses**.
2. **São 37 competências, não 36.** Contar do mesmo mês três anos antes incluindo as duas
   pontas dá 37. É o off-by-one clássico.

Entre as convenções possíveis o pedido varia de R$ 36.554,70 a R$ 39.176,48 — **mais de
R$ 2.600**. Por isso `restituicao()` recebe `meses` e `ate` como parâmetros, com 36 e
"última competência" por padrão, e a autoconferência acusa quando o marco não coincide
com o fim da série.
