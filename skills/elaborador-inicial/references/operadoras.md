# Cadastro de operadoras

Alimenta o fato discriminante **F1** (natureza jurídica) do Classificador. F1 é o
primeiro nó da árvore de decisão do Eixo B: sem entrada aqui, o Classificador
**bloqueia** o caso em vez de chutar a tese.

Chave de busca: CNPJ. Nome comercial é dica, nunca prova.

| Operadora | CNPJ | Natureza | Sede | Tese padrão |
|---|---|---|---|---|
| CASSI — Caixa de Assistência dos Funcionários do Banco do Brasil | 33.719.485/0001-27 ⚠️ | **Autogestão** | SAS Q. 03, Bloco E, Ed. CASSI, Brasília/DF, CEP 70070-030 | `CASSI_AUTOGESTAO` |

⚠️ **CNPJ da CASSI pendente de confirmação.** Dois documentos reais (demonstrativo
BEN120 emitido pela CASSI e petição protocolada em 07/2026) trazem
`33.719.485/0001-27`. A skill `corretor-inicial-cassi-revisional` registra
`33.594.914/0001-24`. Enquanto não houver decisão da advogada, o Classificador
reconhece **os dois** como CASSI, e o Gerador **pergunta** antes de qualificar a ré.
Ver pergunta D1.

## Regras de uso

- Operadora ausente deste cadastro ⇒ gate **G4**: bloqueia e pergunta. Não inferir
  natureza por nome ("Unimed", "Amil") nem por semelhança.
- Autogestão ⇒ override total no Eixo B: a tese é a de autogestão independentemente de
  quem contratou (Súmula 608/STJ exclui o CDC; não há falso coletivo empresarial).
- Uma linha nova aqui só entra com **fonte documental** — CNPJ lido de documento da
  própria operadora ou de peça já protocolada, indicando qual.

## A completar

Autogestões que ainda precisam ser mapeadas (pergunta A3): GEAP, CAMED, Petrobras/AMS,
Fusex, Real Grandeza, entre outras. Operadoras comerciais recorrentes do escritório
também: Unimed (por federação/singular, cada uma com CNPJ próprio), Amil, Bradesco
Saúde, SulAmérica, Hapvida/NDI.
