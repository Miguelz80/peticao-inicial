# 03 — Perguntas abertas antes de escrever código

Organizadas por bloqueio real. **Bloco A** trava o Classificador e o Calculador —
sem isso não dá para escrever código de verdade. **Bloco B** trava o Gerador.
**Bloco C** são definições de projeto que podem esperar mais um pouco.

---

## Bloco A — Bloqueiam o código dos módulos 1 e 2

**A1/A2. Índices ANS e faixa etária.** — ✅ **RESOLVIDA.** Série 2015–2026 montada em
`references/indices-ans.md`, a partir da coluna "Índices ANS" da planilha do escritório,
com sete anos corroborados em publicações da ANS. A fórmula foi confirmada contra a
planilha real: a cadeia de 9 anos bate nos 9 passos. Pendente só a série anterior a 2015
— e `gov.br`/`ans.gov.br` estão **bloqueados pela política de egresso desta sessão**, então
a página da ANS não pôde ser lida direto. Baixando o `.xlsx` da série histórica da ANS e
enviando aqui, fecha com procedência oficial direta.

**A3. Cadastro de operadoras.** — ✅ **RESOLVIDA:** autogestões mais comuns são
**CASSI, ASSEFAZ e GEAP**, e a lista não é exaustiva. Registrado em
`references/operadoras.md`, junto com uma lista de **sinais textuais de autogestão**
para as operadoras fora do cadastro (razão social do tipo "Caixa de Assistência" ou
"Fundação", vínculo a patrocinador, "participantes" em vez de "segurados", reajuste
aprovado em assembleia). Sem sinal nenhum, o gate G4 pergunta.

**A4. Existe uma quinta tese?** — ✅ **RESPONDIDA (08/09/2026): sim, as quatro
teses estão no escopo** — `EMPRESARIAL_FAMILIAR`, `COLETIVO_POR_ADESAO`,
`CASSI_AUTOGESTAO` e `INDIVIDUAL_COMUM`. A árvore de decisão do §4.2 da spec já as
cobre. Consequência: **B2 vira bloqueio de primeira ordem** — metade das teses do
escopo (CASSI e individual comum) não tem modelo DOCX mapeado.

**A5. Planilhas reais, Tipo 1 e Tipo 2.** — ✅ **TIPO 1 RESOLVIDO.** O caso SulAmérica
trouxe o cálculo pronto com as colunas exatas do briefing, incluindo "Reajuste Aplicado"
e "Reajuste Devido" lado a lado. Os conjuntos de cabeçalho do Classificador estavam
certos. Falta ainda uma amostra de **Tipo 2** (faturamento bruto em planilha).

**A6. Valor da causa.**
Qual é a fórmula do escritório? (restituição total? restituição + 12× diferença
mensal? proveito econômico pretendido?) O Classificador precisa saber quais dados são
obrigatórios para fechar o dossiê.

**A7. Corte dos 3 anos (Tema 610).** 🔴 *agora vale mais de R$ 2.600 no pedido*
Identifiquei a convenção da planilha real: **37 competências, maio/2023 a maio/2026** —
que reproduz exatamente o R$ 36.738,93 pedido na peça. Duas questões saem daí:
- o marco terminou **dois meses antes** do fim da série (julho/2026), ou seja, a peça foi
  protocolada com a restituição desatualizada. O marco é a data do cálculo, a da
  distribuição, ou a última competência paga?
- são **37 competências**, não 36 — contar do mesmo mês três anos antes incluindo as duas
  pontas. É proposital ou é off-by-one?

Dependendo da convenção o pedido vai de R$ 36.554,70 a R$ 39.176,48.

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

**B7. Ordem de assinatura.** — ✅ **RESOLVIDA (ver D2): não importa.** Sem regra
condicional; mantém-se a ordem do modelo de base.

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

**D1. CNPJ da CASSI.** — ✅ **RESOLVIDA:** não importa qual dos dois é o "certo".
O CNPJ, o endereço e a razão social da ré são **extraídos do documento do caso** e vão
para a peça como constam ali. O cadastro `references/operadoras.md` deixa de ser fonte
desses dados e passa a responder só a `F1` (autogestão × comercial), reconhecendo os
dois CNPJs como CASSI.

**D2. Ordem de assinatura.** — ✅ **RESOLVIDA: não importa.** Some a regra
condicional; o Gerador mantém a ordem que estiver no modelo DOCX de base, sem lógica
para decidir quem assina primeiro. (Encerra também a pergunta B7.)

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

**D5. Tabelas como imagem.** — ✅ **RESOLVIDA:** a **aparência não muda**; muda só a
técnica. As tabelas passam a ser `w:tbl` nativa reproduzindo o mesmo visual — paleta
extraída pixel a pixel da peça real e registrada em `references/estilo-tabelas.md`
(cabeçalho `#2C3E6B`, zebra `#F5F8FB`, linha vigente `#FFF8E1`, realce de diferença e
percentual em `#C0392B`, caixas RESUMO/ANÁLISE em `#EEF5FB`). Cada célula editável.

_(pergunta original)_
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

**D8. Em CASSI o módulo 2 roda?** — ✅ **RESOLVIDA: roda.** O Calculador aplica índices
ANS em **todas** as teses, autogestão inclusive. A peça CASSI gerada passará a ter uma
tabela de reajuste devido que a peça atual não tem. Ver §10.4 da spec.


**A9. Faixa etária legítima × abusiva — quem decide?** 🔴 *agora com caso concreto*
Na planilha real há duas competências com reajuste fora do mês de aniversário e a coluna
"Tipo de Reajuste" **em branco**: abril/2018 (9,10%) e janeiro/2021 (21,72%). Nenhuma
entrou no valor devido. Se alguma for faixa etária legítima, deveria ter entrado.
Se a faixa etária entra no valor devido, só pode entrar a **legítima** (Temas 952 e 1016
do STJ). Incluir no devido um aumento de faixa etária que a peça vai impugnar como
abusivo apagaria o próprio pedido. Especifiquei que o Calculador **identifica** as
competências com faixa etária e **pergunta** caso a caso antes de incluir. Existe algum
critério objetivo do escritório que permita decidir sem perguntar (ex.: faixa etária
após os 60 anos é sempre impugnada), ou pergunta sempre?

**D9. Cor do cabeçalho: `#2E4057` ou `#2C3E6B`?**
O briefing fixa `#2E4057`; a tabela da peça real usa `#2C3E6B`. São próximos, mas
diferentes. Como a decisão D5 foi "não mudar a aparência", estou usando `#2C3E6B`.
Confirma, ou o padrão do escritório é mesmo `#2E4057` e a peça é que saiu fora?
