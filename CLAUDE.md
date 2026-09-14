# Orientações para trabalhar neste repositório

Skill que gera **petição inicial** de saúde suplementar para a BM Advocacia. O
documento sai daqui e vai a protocolo — as regras abaixo não são estilo, são o que
impede uma peça errada de ser assinada.

## As regras que não se negociam

**Nunca inventar lei, súmula, tema ou julgado.** Nem provisoriamente, nem "para
completar o bloco". Duas das quatro teses têm texto redigido a partir dos fundamentos
documentados, sem peça de referência, e por isso **não citam nenhum julgado**: escolher
jurisprudência é da advogada. Elas estão marcadas com `@revisar` em
`references/teses.md`; ao receber uma peça real dessas teses, substitua o texto e
remova a marca.

**Ausência de sinal é `DESCONHECIDO`, jamais `NÃO`.** Silêncio da transcrição sobre
vínculo empregatício não prova que não existe vínculo.

**Bloquear é o comportamento correto, não uma falha.** Quando falta dado, o certo é
parar e perguntar. Toda pergunta oferece "Não sei / vou verificar", e essa resposta
para o processo — se "não sei" tiver atrito, quem opera chuta para destravar, e o
chute vira tese na peça.

**Regra é dado, não código.** Índices ANS, natureza das operadoras, texto das teses e
paleta das tabelas ficam em `skills/elaborador-inicial/references/`, editáveis pela
advogada. Nada disso é hardcoded em `.py`.

**Nunca versionar documento de caso real.** O `.gitignore` bloqueia `.pdf`, `.docx` e
`.xlsx`. Antes de commitar, confira que não vazou nome, CPF, CNPJ, empregador ou valor
de renda. Análises de caso vão para `docs/` **anonimizadas**.

**O DOCX entregue é nativo e 100% editável.** Sem proteção, sem content control
travado, sem tabela em imagem. O gerador se recusa a escrever qualquer um dos três. A
skill erra, e quem opera precisa poder corrigir no Word na hora.

## Como as coisas funcionam aqui

- **Precisão cheia por dentro, arredondamento só na exibição.** Arredondar entre os
  anos erra centavos que se acumulam ao longo da década.
- **Ano sem índice ANS bloqueia o caso**, em vez de pular o ano ou estimar.
- **O cálculo roda também em `CALCULO_PRONTO`** e é comparado linha a linha com a
  planilha importada. Recontar é a única verificação independente que existe, e as
  duas peças reais analisadas mostraram que planilha pronta também chega errada.
- **Tabela de reajuste é `w:tbl` nativa**, reproduzindo a aparência medida da peça real
  (`references/estilo-tabelas.md`). A aparência não muda; a técnica, sim.
- **O gerador parte do DOCX real do escritório** e reaproveita o `sectPr` original — é
  ele que carrega as referências de cabeçalho e rodapé onde vive o timbre. Montar do
  zero perde o timbre.

## Rodar

```
for f in tests/test_*.py; do python3 "$f"; done
```

Sem dependências para a lógica de decisão. Extração de PDF/XLSX/DOCX usa `pypdf`,
`openpyxl` e `python-docx`; faltando alguma, o arquivo é reportado como ilegível em
vez de derrubar a execução.

`tests/test_suite.py` guarda a própria suíte: teste definido **depois** do bloco
`if __name__ == "__main__"` nunca roda, e isso já passou despercebido três vezes.

## Ao mexer no código

- Rode o fluxo de verdade, não só os testes. Quase todo defeito sério desta sessão
  apareceu ao rodar contra arquivo real — deadlock no orquestrador, planilha que não
  virava competência, numeração de capítulo pulando, tabela em imagem sobrevivendo à
  geração. Nenhum deles apareceu em teste de módulo.
- Ao acrescentar tese ou capítulo, confira que **pedido e capítulo andam juntos**:
  pedido sem o capítulo que o sustenta é incoerência que o leitor nota.
- Ao mexer em unidade (percentual × fração), teste ponta a ponta. `"10,50"` já entrou
  como 1050% e multiplicou a mensalidade por onze, com teste verde cobrindo o erro.

## O que ainda depende da advogada

Em `docs/03-perguntas-abertas.md`. As que mais pesam: **A7** (janela da restituição —
varia mais de R$ 2.600 no pedido), **A9** (critério de faixa etária legítima), a série
de índices ANS anterior a 2015, e as peças reais de **empresarial familiar** e
**individual comum** para substituir o texto redigido.
