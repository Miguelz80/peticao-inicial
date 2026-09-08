# 03 — Perguntas abertas antes de escrever código

Organizadas por bloqueio real. **Bloco A** trava o Classificador e o Calculador —
sem isso não dá para escrever código de verdade. **Bloco B** trava o Gerador.
**Bloco C** são definições de projeto que podem esperar mais um pouco.

---

## Bloco A — Bloqueiam o código dos módulos 1 e 2

**A1. Tabela de índices ANS, ano a ano.**
Preciso da tabela completa que o escritório usa. Três definições dentro dela:
- (a) o índice é o **teto de reajuste anual autorizado pela ANS para planos
  individuais/familiares**, certo? Desde que ano preciso ter na tabela?
- (b) o período ANS vai de **maio a abril**. Quando o aniversário do contrato cai em
  outro mês, aplico o índice do período em que o aniversário cai — confirma?
- (c) o índice do ano incide sobre o **valor devido do ano anterior** (base já
  corrigida, capitalizando), não sobre o valor pago. Confirma?

**A2. Faixa etária entra no cálculo do "devido"?**
Se, no período, houve reajuste por faixa etária **legítimo** (previsão contratual +
Tema 952/1016), o valor devido deve incorporá-lo, ou o devido é sempre só ANS e a
faixa etária é discutida à parte? Isso muda a fórmula do módulo 2 inteira.

**A3. Cadastro de operadoras.**
Lista das operadoras já mapeadas com **CNPJ, sede e natureza jurídica** (comercial ×
autogestão). O Classificador usa isso como discriminante duro F1 — sem cadastro, ele
bloqueia todo caso. Além da CASSI, quais autogestões já apareceram (GEAP, Camed,
Petrobras/AMS, Fusex...)?

**A4. Existe uma quinta tese?** — ✅ **RESPONDIDA (08/09/2026): sim, as quatro
teses estão no escopo** — `EMPRESARIAL_FAMILIAR`, `COLETIVO_POR_ADESAO`,
`CASSI_AUTOGESTAO` e `INDIVIDUAL_COMUM`. A árvore de decisão do §4.2 da spec já as
cobre. Consequência: **B2 vira bloqueio de primeira ordem** — metade das teses do
escopo (CASSI e individual comum) não tem modelo DOCX mapeado.

**A5. Planilhas reais, Tipo 1 e Tipo 2.** — 🟡 **PARCIAL:** o caso CASSI trouxe um
insumo que não é planilha (demonstrativo BEN120 em PDF digitalizado). Continuo
precisando de `.xlsx` reais dos Tipos 1 e 2 — o caso recebido não cobre nenhum dos dois.

_(pedido original)_
Preciso de 2–3 arquivos reais de cada tipo (podem vir anonimizados) para ver os
cabeçalhos **como eles realmente aparecem**: variações de grafia, linhas de título
antes do cabeçalho, células mescladas, abas múltiplas, totalizadores no meio da tabela.
A detecção do Eixo A é feita sobre esses cabeçalhos — hoje ela está escrita sobre os
nomes idealizados do seu exemplo.

**A6. Valor da causa.**
Qual é a fórmula do escritório? (restituição total? restituição + 12× diferença
mensal? proveito econômico pretendido?) O Classificador precisa saber quais dados são
obrigatórios para fechar o dossiê.

**A7. Corte dos 3 anos (Tema 610).**
O marco é a **data de distribuição** (que ainda não existe quando a peça é gerada), a
data de geração da peça, ou uma data que a operadora informa? E o mês de corte é
inclusivo ou exclusivo?

**A8. Restituição simples × dobro — padrão do escritório.**
A skill empresarial-familiar diz que a dobra é a regra salvo engano justificável. A
skill pode **pré-marcar** a dobra e pedir confirmação, ou tem que deixar em branco
sempre? (Hoje especifiquei como decisão humana obrigatória.)

---

## Bloco B — Bloqueiam o Gerador (módulo 3)

**B1. Os DOCX-modelo.** — 🟡 **PARCIAL:** recebi a peça CASSI real em `.docx`, com
timbre (`image1/image2.png`), margens e `sectPr` conferidos. Faltam os dois modelos
do escritório citados nas skills.

_(pedido original)_
Preciso dos arquivos reais para `assets/modelos/`:
`PETIÇÃO INICIAL-MODELO APENAS RESTITUIÇÃO.docx` e
`MODELO PETIÇÃO INICIAL COLETIVO POR ADESÃO.docx`. São as versões atuais?

**B2. Falta modelo para duas teses.** — 🟢 **CASSI RESOLVIDA:** a peça recebida serve
de base (estrutura em `docs/04-achados-caso-cassi.md` §6). Falta só o modelo do
**revisional individual comum**.

_(pergunta original)_
Não há modelo específico mapeado para **CASSI** nem para **revisional individual
comum**. Adapto a partir de qual base, ou existe arquivo próprio que eu não vi?

**B3. Cabeçalho #2E4057 × timbre em imagem.**
A skill `tatiana-pecas-processuais` diz que o timbre real do escritório **está nas
imagens** do DOCX (logo no cabeçalho, contatos no rodapé), e que o `.docx` nunca deve
ser montado do zero. Já o seu briefing fixa "cabeçalho azul-escuro #2E4057". São a
mesma coisa (a cor é do texto/faixa que acompanha a imagem) ou é um padrão novo que
substitui o timbre em imagem?

**B4. Como a tabela de cálculo entra na peça.** — 🔴 **RESPONDIDA PELA PRÁTICA, no
sentido oposto ao requisito:** hoje as duas tabelas centrais vão como **imagem PNG**.
Ver D5.

_(pergunta original)_
Tabela completa mês a mês no corpo da petição, resumo no corpo + tabela completa em
anexo, ou planilha separada? (A tabela é `w:tbl` editável em qualquer caso — a
pergunta é de layout, não de formato.)

**B5. Gratuidade é sempre pedida?**
Em toda inicial, ou só quando há prova de hipossuficiência? E qual o critério para
citar o saldo bancário na peça (existe um teto de valor)?

**B6. Foro / endereçamento.**
Sempre domicílio do autor? Na tese CASSI, a skill de referência alerta que, não
incidindo o CDC, a regra de competência pode ser outra — a skill decide ou pergunta?

**B7. Ordem de assinatura — "na Bahia" significa o quê?**
Comarca onde a ação será distribuída, domicílio do cliente, ou sede do escritório?
Determina se Tatiana ou Gabriel assina primeiro.

---

## Bloco C — Definições de projeto

**C1. Dados reais no repositório.**
Já bloqueei `.xlsx/.pdf/.docx` no `.gitignore`. Confirma que **nenhum** documento de
caso real pode ser versionado, e que as fixtures de teste serão anonimizadas (nome,
CPF/CNPJ, valores alterados)? Sem corpus de teste o Classificador não tem como ser
validado — precisamos combinar como anonimizar.

**C2. Entrega no Claude Desktop.**
A colega vai enviar **todos** os documentos de uma vez no início da conversa, ou aos
poucos? Muda se o Classificador roda uma vez ou reavalia a cada arquivo novo.

**C3. Confirmação obrigatória sempre (G8) — você aceita?**
Especifiquei que o Espelho de Classificação exige "confirmo" **em toda geração**,
mesmo com confiança alta. Custa uma mensagem a mais no chat e elimina a classe inteira
de erro "gerou peça com tese errada sem ninguém olhar". Alternativa é confirmar só
quando ambíguo. **Recomendo a confirmação sempre** — a pergunta é se você concorda.

**C4. O que a skill entrega quando bloqueia.**
Só a lista de perguntas, ou também um rascunho parcial (fatos + cálculo já feito) para
a operadora adiantar? Risco: rascunho parcial vira peça protocolada por engano.

**C5. Nome e instalação da skill.**
`elaborador-inicial` fica no repositório em `skills/elaborador-inicial/`. Como ela
chega no Claude Desktop da colega — pelo mesmo caminho das skills atuais do escritório?


---

## Bloco D — Novas, vindas do caso CASSI real

**D1. CNPJ da CASSI — qual está certo?** 🔴 *urgente*
O demonstrativo emitido pela própria CASSI e a petição protocolada dizem
**33.719.485/0001-27**. A skill `corretor-inicial-cassi-revisional` registra
**33.594.914/0001-24**. Como a skill é a fonte que alimenta a qualificação da ré, se o
número dela estiver errado, todas as peças CASSI futuras saem com CNPJ errado. Você
confirma qual é o correto?

**D2. Ordem de assinatura — a regra está invertida?** 🔴
A peça real é de **saúde**, comarca de **Salvador/BA**, e está assinada por **Gabriel
primeiro, Tatiana depois**. O briefing diz "Tatiana antes de Gabriel em saúde/consumidor
na Bahia". Uma das duas está errada: ou a regra, ou essa peça. Qual?

**D3. Valor da causa = 2 × restituição?**
Na peça real, R$ 43.041,98 é exatamente o dobro da restituição estimada de
R$ 21.520,99 — mas o texto justifica como "restituição + 12 meses de diferença", que
daria R$ 34.114,99. Qual é a fórmula que o escritório usa de verdade?

**D4. Documentos digitalizados: quem faz o OCR?**
Metade dos PDFs do caso não tem camada de texto (extrato bancário e documentação
pessoal inclusive). Duas saídas: (a) a skill lê essas páginas como imagem, aceitando
confiança menor e sempre confirmando o dado extraído; ou (b) a operadora passa a enviar
os arquivos já pesquisáveis. **Recomendo (a)** — não dá para depender de disciplina de
digitalização. Você concorda?

**D5. Tabelas como imagem — confirma a mudança?**
Hoje o histórico de reajustes e a tabela da tutela vão como PNG. Isso é o oposto do
requisito não negociável do projeto, e no caso real as duas imagens traziam percentuais
divergentes entre si (12,79% × 12,88% para o mesmo reajuste) sem que ninguém pudesse
corrigir no Word. No `elaborador-inicial` elas passam a ser tabela nativa editável —
confirma? Muda a aparência da peça em relação ao que o escritório vem protocolando.

**D6. Divergências do caso já protocolado — quer que eu faça alguma coisa?**
Além das duas tabelas, a tutela pede limitação a R$ 2.526,89, valor que não aparece na
tabela de histórico da própria peça (2.238,77 · 2.525,09 · 2.886,98 · 3.576,39). Esse
processo já foi distribuído. Isso é aproveitável numa emenda, ou é só insumo para o
módulo 4?

**D7. Blocos condicionais.**
A peça tem um capítulo inteiro de **reajuizamento** (desistência anterior + competência
concorrente) e um de **prioridade de idoso**. Nenhum dos dois decorre da tese —
disparam por fato processual e por idade. Confirma que o gerador deve tratá-los como
blocos condicionais, e existem outros do gênero (doença grave, tutela já indeferida)?

**D8. Em CASSI o módulo 2 roda?**
A peça real não calcula reajuste devido por índice ANS: remete à liquidação de sentença
e pede exibição de documentos. Confirma que, na tese de autogestão, o Calculador
**não** aplica índices ANS — e que o valor da tutela é o patamar histórico anterior?
