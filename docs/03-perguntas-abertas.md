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

**A5. Planilhas reais, Tipo 1 e Tipo 2.**
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

**B1. Os DOCX-modelo.**
Preciso dos arquivos reais para `assets/modelos/`:
`PETIÇÃO INICIAL-MODELO APENAS RESTITUIÇÃO.docx` e
`MODELO PETIÇÃO INICIAL COLETIVO POR ADESÃO.docx`. São as versões atuais?

**B2. Falta modelo para duas teses.**
Não há modelo específico mapeado para **CASSI** nem para **revisional individual
comum**. Adapto a partir de qual base, ou existe arquivo próprio que eu não vi?

**B3. Cabeçalho #2E4057 × timbre em imagem.**
A skill `tatiana-pecas-processuais` diz que o timbre real do escritório **está nas
imagens** do DOCX (logo no cabeçalho, contatos no rodapé), e que o `.docx` nunca deve
ser montado do zero. Já o seu briefing fixa "cabeçalho azul-escuro #2E4057". São a
mesma coisa (a cor é do texto/faixa que acompanha a imagem) ou é um padrão novo que
substitui o timbre em imagem?

**B4. Como a tabela de cálculo entra na peça.**
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
