# Fluxo ponta a ponta — caso de autogestão (anonimizado)

Rodada completa do orquestrador sobre os 10 documentos de um caso real de autogestão,
do PDF ao DOCX. Registra o que a rodada encontrou — os defeitos abaixo **não**
apareceram em nenhum teste de módulo, só ao rodar contra arquivo de verdade.

## O que a rodada exercitou

| Fase | Resultado |
|---|---|
| TRIAGEM | 13 segmentos em 10 arquivos; 6 digitalizados, sem camada de texto |
| CONFIRMACAO | Tese AUTOGESTÃO; descartou FALSO COLETIVO EMPRESARIAL |
| CALCULO | 48 competências, aniversário em maio, 4 reajustes anuais |
| REDACAO | 12 capítulos, numeração I–XII sem salto |
| GERACAO | DOCX nativo, 2 tabelas `w:tbl`, 0 imagem no corpo |
| CONFERENCIA | nada a apontar; documento liberado |

A carteirinha declara **"Tipo Contratação: COLETIVO EMPRESARIAL"** e nomeia uma pessoa
jurídica contratante. O classificador ignorou o rótulo porque a operadora é autogestão —
é exatamente o sinal que levaria um classificador ingênuo à tese errada.

Conferência independente do total: a soma da coluna "Valor Pago" bateu com o campo Total
impresso no próprio demonstrativo, até os centavos. É a confirmação de que a série foi
lida certo.

## Defeitos encontrados e corrigidos

**1. Proposta de honorários passava como planilha de cálculo.**
A proposta do escritório diz "valor pago", "valor devido" e "diferença" em prosa corrida,
no resumo do diagnóstico preliminar. Três nomes de coluna bastavam para o arquivo ser
rotulado `CALCULO_PRONTO`. Agora só é cálculo se o texto também tiver **linhas de
competência legíveis** — nome de coluna solto não é tabela.

**2. O aviso que explicava a falha de leitura era descartado.**
Quando nenhuma competência era lida da planilha, os avisos da leitura ("154 linhas com
competência mas sem valor legível") eram jogados fora junto. Quem operava via o cálculo
não acontecer e não tinha como saber por quê.

**3. Regime que exige cálculo, sem série legível, caía na redação.**
O demonstrativo veio digitalizado e com as colunas embaralhadas na extração — competência
e valor saem em blocos separados, sem alinhamento de linha. Sem série, o orquestrador
seguia para a REDACAO e pedia à operadora que **digitasse** restituição e diferença
mensal: justamente os números que esta skill existe para calcular e conferir. Agora
bloqueia na fase CALCULO, dizendo o que houve e como fornecer a série.

**4. `restituicao_corrente()` somava as competências negativas.**
`restituicao()` soma só as competências pagas a maior; `restituicao_corrente()` — que é a
referência usada pela Conferência — somava tudo. Os dois caminhos divergiam sempre que a
série tinha alguma competência paga a menor, e a Conferência **reprovava em C6 uma peça
correta**: R$ 5.103,24 escrito na peça contra R$ 2.829,34 esperados. Regressão coberta em
`tests/test_calcular.py`.

**5. Aviso de competência negativa repetido cinco vezes.**
A sentinela de deduplicação procurava um texto ("pagou menos") que a própria mensagem
não contém ("pagas ABAIXO"). O aviso saía uma vez por chamada de `restituicao()`.

## O que ficou para a advogada

**Pergunta A10** (nova, em `03-perguntas-abertas.md`): a operadora aplicou 6,76% num ano
em que o teto ANS era 15,50%. Aplicando o teto cheio, o devido passa acima do que se
pagou e 16 competências ficam negativas. Muda R$ 227 na diferença mensal. Não mudei a
fórmula por conta própria — como está, só reduz o pedido.

**Pergunta A7** (janela da restituição) continua aberta e aqui também pesa: a janela saiu
`janeiro/2023 a dezembro/2025`, contada da última competência do demonstrativo, que é de
dezembro/2025 — anterior à data em que se calcula.

**Pergunta A6** (valor da causa) segue sem fórmula; o campo entrou como texto livre e a
verificação C5 continua desligada.

## Sobre a proposta de honorários do caso

Os números do diagnóstico preliminar não fecham com o cálculo, e um deles não fecha
consigo mesmo: a "restituição (últimos 3 anos)" declarada é **exatamente 12 ×** a
diferença mensal declarada. É projeção de doze meses com rótulo de três anos.
