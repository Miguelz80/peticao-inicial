# Cadastro de operadoras

Este cadastro serve a **uma única pergunta**: a operadora é de **autogestão** ou
**comercial**? É o fato discriminante `F1`, primeiro nó da árvore de decisão do Eixo B.

## O que este cadastro NÃO faz

Ele **não** é fonte de CNPJ, endereço ou razão social para a qualificação da ré.
Esses dados são **extraídos dos documentos do próprio caso** (demonstrativo, boleto,
carteira, contrato) e vão para a peça exatamente como constam ali.

Motivo: cadastro desatualizado é erro silencioso que se propaga para toda peça futura.
O documento do caso é a fonte, e ele sempre acompanha o caso.

## Autogestões mapeadas

As mais frequentes no escritório. **A lista não é exaustiva** — o escritório trabalha
com diversas outras.

| Operadora | Natureza | Como reconhecer | Tese |
|---|---|---|---|
| CASSI — Caixa de Assistência dos Funcionários do Banco do Brasil | Autogestão | CNPJ `33.719.485/0001-27` ou `33.594.914/0001-24`; menção a "Caixa de Assistência dos Funcionários do Banco do Brasil" | `CASSI_AUTOGESTAO` |
| ASSEFAZ — Fundação Assefaz | Autogestão | menção a "Assefaz" ou "Fundação Assefaz" | `CASSI_AUTOGESTAO` |
| GEAP — GEAP Autogestão em Saúde | Autogestão | menção a "GEAP" | `CASSI_AUTOGESTAO` |

> Os dois CNPJs da CASSI são reconhecidos como a mesma operadora. Não é preciso decidir
> qual é o "certo": o que entra na peça é o que estiver no documento do caso.

> A tese `CASSI_AUTOGESTAO` vale para **qualquer** autogestão, não só a CASSI — o nome
> é histórico. O que muda entre elas é a qualificação da ré (extraída do documento) e o
> estatuto/regulamento citado.

## Operadora fora da lista — sinais de autogestão

A lista nunca vai estar completa, então o Classificador não pode tratar "não está no
cadastro" como "é comercial". Antes de acionar o gate G4, procurar nos documentos do
caso estes sinais, que costumam aparecer nos papéis da própria operadora:

- as palavras **"autogestão"**, "entidade de autogestão", "plano de autogestão";
- razão social do tipo **"Caixa de Assistência"**, "Fundação", "Instituto",
  "Associação de Beneficência", "Fundo de Assistência";
- vínculo a um **patrocinador/mantenedor** (banco, estatal, órgão público, categoria
  profissional) como condição de elegibilidade;
- beneficiários chamados de **"participantes"**, "associados", "assistidos" em vez de
  "segurados"/"clientes";
- reajuste aprovado por **assembleia, conselho deliberativo ou conselho de
  administração**, e não simplesmente "comunicado" ao beneficiário;
- ausência de finalidade lucrativa declarada no estatuto.

Encontrando sinais, o Classificador **propõe** autogestão com a citação literal do
trecho e pede confirmação. Não encontrando nada, dispara G4 e pergunta direto.

Confirmada uma operadora nova, ela entra na tabela acima com a fonte documental
indicada — o cadastro cresce com o uso.

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
