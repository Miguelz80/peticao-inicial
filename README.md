# elaborador-inicial

Skill da **BM Advocacia** (Borges Macedo Advocacia e Consultoria — Salvador/BA) que
recebe os documentos de um caso de saúde suplementar e devolve uma **petição inicial
em DOCX**, no padrão do escritório, pronta para revisão humana antes do protocolo.

## Escopo desta fase

**Apenas petições iniciais.** Réplica, recurso inominado, apelação, embargos,
contrarrazões e cumprimento de sentença estão **fora do escopo** — já são tratados por
skills separadas do escritório. Se uma regra daqui parecer reaproveitável para outro
tipo de peça, isso deve ser apenas **mencionado**, nunca implementado neste repositório.

## Os quatro módulos

| # | Módulo | Papel | Status |
|---|--------|-------|--------|
| 1 | **Classificador** | Decide o regime de cálculo (pronto × bruto) e a tese/modelo aplicável; pergunta quando houver dúvida | **Implementado** — `skills/elaborador-inicial/scripts/`, 31 testes |
| 2 | **Calculador atuarial** | Monta a tabela de reajuste devido aplicando os índices ANS ano a ano | **Implementado** — `scripts/calcular_reajuste.py`, 17 testes |
| 3 | **Gerador de petição** | Preenche o modelo DOCX certo com os dados do caso | **Implementado** — `scripts/gerar_peticao.py` + `scripts/roteiro.py`, 38 testes |
| 4 | **Conferência** | Compara os valores da peça final com os valores de origem antes de liberar | **Implementado** — `scripts/conferir.py`, 22 testes |

A ordem é deliberada: o Classificador é o módulo de maior risco (uma tese errada numa
peça protocolada é o pior cenário do projeto) e é validado primeiro.

O texto jurídico de cada tese fica em `skills/elaborador-inicial/references/teses.md` —
editável pela advogada, sem tocar em código. Hoje as teses de **autogestão** e de
**coletivo por adesão** têm o texto do escritório, extraído de peças reais; as outras
duas têm o roteiro de capítulos e os fundamentos, mas geram peça com marcador de
pendência até que uma peça ou modelo dessas teses chegue.

## Requisito não negociável: DOCX 100% editável

O documento entregue tem que ser um `.docx` nativo do Word, **integralmente editável à
mão** por quem opera: texto, tabelas, valores e assinaturas. É proibido:

- proteção de documento, restrição de edição ou seções somente-leitura;
- content controls / campos travados;
- qualquer trecho renderizado como imagem (tabela de cálculo inclusive);
- estruturas que só a IA consiga reescrever.

Motivo: o sistema **vai errar** — classificação, valor, redação — e a colega que opera
precisa conseguir abrir o arquivo e corrigir na hora, sem rodar a skill de novo.
A tabela de reajuste é `w:tbl` de verdade, com números digitáveis célula a célula.

## Quem opera

Uma colega do setor processual, via **chat comum (Claude Desktop)** — sem acesso a
código, git ou linha de comando. Todo o produto final desta fase precisa funcionar
inteiramente por chat.

## Documentação

- `docs/01-arquitetura.md` — estrutura de pastas e fronteira Python × modelo
- `docs/02-classificador-spec.md` — especificação do Classificador (pseudocódigo)
- `docs/03-perguntas-abertas.md` — o que precisa ser respondido antes de escrever código


## Rodar os testes

```
python3 tests/test_classificar.py
python3 tests/test_extrair.py
python3 tests/test_calcular.py
python3 tests/test_conferir.py
python3 tests/test_gerar.py
python3 tests/test_roteiro.py
```

Sem dependências para a lógica de decisão. A extração completa (PDF, XLSX, DOCX) usa
`pypdf`, `openpyxl` e `python-docx` — faltando alguma, o arquivo é reportado como
ilegível em vez de derrubar a execução.
