# Instalar o Elaborador de Petição Inicial no Claude

Escrito para quem **não mexe com código**. São três etapas, uma vez só. Depois disso, o
uso é conversa normal.

---

## Etapa 1 — Pegar o arquivo da skill

O arquivo chama **`elaborador-inicial.zip`**. Salve no computador, em qualquer pasta.
Não precisa descompactar.

> Se ele não estiver com você, quem cuida do repositório gera com `./empacotar.sh`.

---

## Etapa 2 — Instalar no Claude

1. Abra o **Claude** (aplicativo no computador ou `claude.ai` no navegador).
2. Vá em **Configurações** (o ícone de engrenagem, ou seu nome no canto).
3. Procure a seção de **Recursos / Capabilities**, e dentro dela **Skills**.
4. Clique em **enviar** ou **adicionar skill** e escolha o `elaborador-inicial.zip`.
5. Confirme que **"Elaborador de Petição Inicial"** aparece na lista e está **ligada**.

Ainda nas configurações, deixe **ligada a execução de código** (pode aparecer como
*análise de dados*, *code execution* ou *criação e análise de arquivos*). A skill faz o
cálculo e monta o DOCX rodando um programa — sem isso ela não funciona.

> Os nomes dos menus mudam de versão para versão. Se algum não estiver escrito
> exatamente assim, procure o mais parecido. O que importa é: **Skills → enviar o zip**,
> e **execução de código ligada**.

---

## Etapa 3 — Preparar o papel timbrado (uma vez só)

A petição sai no timbre do escritório, e o timbre vem de um **DOCX do próprio
escritório** — não é montado do zero. Você precisa de um arquivo modelo: uma petição em
branco, só com o timbre.

**Se você já tem** o papel timbrado em `.docx`, pronto. Guarde onde souber achar.

**Se você só tem petições já protocoladas**, peça ao Claude, no chat:

> Prepara um modelo timbrado a partir desta peça — (anexa uma petição `.docx` do
> escritório)

Ele devolve o arquivo com o corpo vazio, o timbre intacto e os dados do cliente
retirados. **Abra no Word e confira o cabeçalho e o rodapé** antes de usar: se o timbre
do escritório trouxer algo do caso, continua lá — o programa avisa, mas quem confirma é
você.

Esse modelo **fica na sua máquina**. Não vai para o repositório, porque saiu de peça de
cliente.

---

## Como usar, no dia a dia

Abra uma conversa nova e escreva:

> **Elabora a inicial deste caso** — (anexa os documentos)

Só isso. A skill conduz o resto e pergunta uma coisa de cada vez.

### O que anexar

| | |
|---|---|
| **demonstrativo de pagamento da operadora** ou a **planilha de cálculo** | é daqui que saem as mensalidades mês a mês — **sem isso não há cálculo** |
| **carteirinha** do plano | plano, abrangência, acomodação, início de vigência |
| **contrato** ou proposta de adesão | natureza da contratação |
| **documento pessoal** | nome, CPF, idade |
| o **modelo timbrado** da Etapa 3 | de onde sai o timbre |
| comprovante de residência, procuração, holerite, extrato | se tiver |

Pode mandar tudo junto, do jeito que estiver. O que faltar, ela pede.

### O que ela vai te perguntar

1. **"Confirma a tese?"** — mostra o raciocínio e o que descartou. **Sempre pergunta**,
   mesmo quando é óbvio. É a última barreira antes de uma tese errada ir a protocolo.
2. **"Em que mês cai o aniversário do contrato?"**
3. **Se houver reajuste fora do mês de aniversário** — pergunta, um a um, se aquela
   faixa etária é legítima.
4. **"Qual o valor da causa?"** — enquanto a fórmula do escritório não estiver fechada.

Toda pergunta aceita **"não sei / vou verificar"**. Essa resposta **para o processo**, e
está certo que pare: é melhor do que chutar. Não tem problema nenhum responder isso.

### Quando ela travar

Travar é o comportamento certo, não defeito. Ela para quando falta um dado que mudaria a
peça — índice de um ano, mensalidade ilegível, tese em dúvida. A mensagem diz o que
falta. Se você não tiver a informação, diga "não sei" e leve à advogada.

### No fim

Ela entrega o **DOCX** e uma lista de **avisos** — coisas que não travam mas precisam de
olho humano. Leia os avisos.

O documento é **editável no Word, inteiro**: sem senha, sem campo travado, sem tabela em
imagem. Se um valor estiver errado, corrija direto no arquivo. **A skill erra, e a
revisão é sempre sua.**

---

## Duas coisas que você precisa saber antes do primeiro uso

**Duas das quatro teses ainda não foram lidas por advogado.** *Empresarial familiar* e
*individual comum* têm texto redigido a partir dos fundamentos, sem peça de referência, e
não citam nenhum julgado. Geram petição completa, com aviso. As outras duas — *autogestão*
e *coletivo por adesão* — saíram de peças reais do escritório.

**Demonstrativo escaneado dá trabalho.** Se o PDF for foto de papel, as colunas
embaralham e a skill não consegue parear mês com valor. Ela avisa e para, em vez de
chutar. Quando der, peça o demonstrativo em planilha ou em PDF de texto.

---

## Se algo der errado

| O que aparece | O que fazer |
|---|---|
| A skill não é acionada sozinha | Escreva "usa a skill elaborador-inicial" no começo |
| "não consegui ler competência e valor pago" | O demonstrativo veio escaneado. Peça um legível, ou passe os valores na conversa |
| "documento não liberado, corrija os bloqueios" | A conferência achou divergência entre a peça e o cálculo. A mensagem diz qual — não force |
| A petição sai sem timbre | Faltou anexar o modelo da Etapa 3 |
| Erro de biblioteca ao ler PDF | Anexe o documento na conversa mesmo assim: o Claude lê o anexo direto e segue |
