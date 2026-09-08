# Cadastro de operadoras

Este cadastro serve a **uma única pergunta**: a operadora é de **autogestão** ou
**comercial**? É o fato discriminante `F1`, primeiro nó da árvore de decisão do Eixo B.

## O que este cadastro NÃO faz

Ele **não** é fonte de CNPJ, endereço ou razão social para a qualificação da ré.
Esses dados são **extraídos dos documentos do próprio caso** (demonstrativo, boleto,
carteira, contrato) e vão para a peça exatamente como constam ali.

Motivo: cadastro desatualizado é erro silencioso que se propaga para toda peça futura.
O documento do caso é a fonte, e ele sempre acompanha o caso.

| Operadora | Natureza | Como reconhecer | Tese |
|---|---|---|---|
| CASSI — Caixa de Assistência dos Funcionários do Banco do Brasil | **Autogestão** | CNPJ `33.719.485/0001-27` ou `33.594.914/0001-24`; menção a "Caixa de Assistência dos Funcionários do Banco do Brasil" | `CASSI_AUTOGESTAO` |

> Os dois CNPJs acima são reconhecidos como CASSI. Não é preciso decidir qual é o
> "certo": o que entra na peça é o que estiver no documento do caso.

## Regras de uso

- Operadora não reconhecida ⇒ gate **G4**: bloqueia e pergunta se é autogestão. Não
  inferir natureza por nome comercial ("Unimed", "Amil") nem por semelhança.
- Autogestão ⇒ override total no Eixo B: a tese é a de autogestão independentemente de
  quem contratou (Súmula 608/STJ afasta o CDC; não há falso coletivo empresarial).
- Reconhecimento por **CNPJ raiz** (8 primeiros dígitos) além do CNPJ completo — filial
  e matriz da mesma operadora têm a mesma natureza jurídica.
- Linha nova só entra com fonte documental indicada.

## A completar (pergunta A3)

Autogestões: GEAP, CAMED, Petrobras/AMS, Fusex, Real Grandeza.
Comerciais recorrentes: Unimed (cada singular/federação com CNPJ próprio), Amil,
Bradesco Saúde, SulAmérica, Hapvida/NDI.
