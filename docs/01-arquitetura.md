# 01 — Estrutura de pastas e arquitetura

## Estrutura proposta

```
peticao-inicial/
├── README.md
├── .gitignore                          # bloqueia dados reais de caso (LGPD/sigilo)
│
├── docs/                               # documentação de PROJETO (não vai para a skill)
│   ├── 01-arquitetura.md
│   ├── 02-classificador-spec.md
│   └── 03-perguntas-abertas.md
│
├── skills/
│   └── elaborador-inicial/             # ← isto é o que a colega instala/usa no chat
│       ├── SKILL.md                    # ponto de entrada; curto, só orquestra
│       ├── references/                 # lidos sob demanda pelo modelo
│       │   ├── classificador.md        # árvore de decisão + roteiro de perguntas
│       │   ├── teses.md                # tese → modelo DOCX → blocos obrigatórios
│       │   ├── indices-ans.md          # tabela de índices ANS por ano/período
│       │   ├── operadoras.md           # cadastro: CNPJ, sede, natureza (autogestão?)
│       │   ├── estilo-docx.md          # Segoe UI, A4, margens, #2E4057, assinaturas
│       │   └── espelho.md              # formato do Espelho de Classificação
│       ├── assets/
│       │   ├── modelos/                # DOCX-modelo reais do escritório
│       │   └── timbre/                 # imagens de cabeçalho/rodapé extraídas
│       └── scripts/                    # trabalho determinístico (Python)
│           ├── extrair_evidencias.py   # módulo 1 — leitura de xlsx/pdf/docx → JSON
│           ├── classificar.py          # módulo 1 — eixo A + árvore do eixo B
│           ├── calcular_reajuste.py    # módulo 2
│           ├── gerar_peticao.py        # módulo 3
│           └── conferir.py             # módulo 4
│
└── tests/
    └── fixtures/
        ├── casos/                      # casos reais ANONIMIZADOS (dossiê esperado)
        └── planilhas/                  # variações de cabeçalho Tipo 1 e Tipo 2
```

### Por que assim

- **`skills/elaborador-inicial/` isolado do resto.** O que a colega usa no Claude
  Desktop é só essa pasta. `docs/` e `tests/` são do desenvolvimento e não poluem o
  contexto da skill em produção.
- **`SKILL.md` curto, `references/` sob demanda.** O `SKILL.md` carrega em toda
  conversa; as tabelas grandes (índices ANS, cadastro de operadoras, catálogo de teses)
  só são lidas quando necessárias. Isso mantém o contexto barato e, mais importante,
  faz com que atualizar um índice ANS seja editar uma linha de tabela — não caçar um
  número dentro de um prompt.
- **`references/` versus `scripts/`.** Regra é dado, não código: os índices ANS e a
  natureza jurídica de cada operadora ficam em Markdown editável, nunca hardcoded em
  `.py`. Quem mantém isso é advogado, não desenvolvedor.
- **`assets/modelos/` com os DOCX reais.** O timbre do escritório vive dentro das
  imagens do `.docx` original — o gerador tem que partir do arquivo real do escritório
  e substituir o conteúdo, nunca montar um `.docx` do zero (regra já consolidada na
  skill `tatiana-pecas-processuais`). Isso também é o que garante o DOCX nativo e
  100% editável.
- **`tests/fixtures/`.** Um classificador sem corpus de casos reais é opinião. Cada
  caso já resolvido vira uma fixture: entrada anonimizada + dossiê esperado. É o que
  permite mexer na árvore de decisão sem medo depois.

## Fronteira Python × modelo (decisão de arquitetura)

O Classificador é **híbrido**, e a divisão não é estética — é de risco:

| Camada | Quem faz | Por quê |
|---|---|---|
| Extrair evidência (cabeçalhos de planilha, CNPJ, datas, valores, saldo do extrato) | **Python** | Determinístico, auditável, reprodutível. O modelo não deve "olhar" uma planilha e estimar números. |
| Interpretar narrativa (transcrição de reunião → sinais de falso coletivo) | **Modelo** | Exige leitura de linguagem natural, com citação literal obrigatória do trecho. |
| Aplicar a árvore de decisão sobre fatos discriminantes | **Python** | A regra é fechada e precisa dar sempre a mesma resposta para os mesmos fatos. |
| Perguntar à operadora e receber a confirmação | **Modelo** | É conversa no chat. |
| Decidir sozinho quando a evidência falta | **Ninguém** | Bloqueia e pergunta. |

O script nunca decide *sozinho* a tese: ele emite **fatos + evidências + veredito
proposto**; o modelo apresenta isso à operadora e só segue com confirmação explícita.

## Restrições de formato já fixadas (para o módulo 3, não implementar ainda)

Registradas aqui para não se perderem entre fases:

- Fonte **Segoe UI**, corpo 12pt (`w:sz 24`), entrelinha `360`, `after 140`,
  justificado, recuo de primeira linha `1417`.
- A4 `11906×16838`; margens sup. `2037`, dir. `1562`, inf. `1560`, esq. `1560`.
- Cabeçalho azul-escuro **#2E4057**.
- Ordem de assinatura: **Tatiana antes de Gabriel** em saúde/consumidor na Bahia;
  **Gabriel primeiro** fora da Bahia. (Ver pergunta B7 em `03-perguntas-abertas.md`:
  "na Bahia" = comarca da ação ou domicílio do cliente?)
- Tabela de cálculo como `w:tbl` nativa, células com texto editável — nunca imagem.
- Sem `w:documentProtection`, sem content controls, sem campos travados.
