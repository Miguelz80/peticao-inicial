# Estilo das tabelas — reproduzir a aparência atual em tabela nativa

**Regra da decisão D5:** a aparência do que o escritório já protocola **não muda**; o
que muda é que as tabelas deixam de ser imagem PNG e passam a ser `w:tbl` nativa do
Word, com cada célula editável.

Não é simplificação de layout. É a mesma tabela, feita de outro jeito. Este arquivo
existe para que o Gerador consiga reproduzir o visual sem ter a imagem original.

Paleta extraída pixel a pixel das duas imagens da peça CASSI de referência.

---

## Tabela 1 — Histórico de reajustes

Título: `HISTÓRICO DE REAJUSTES – PLANO <NOME DO PLANO>`, caixa alta, negrito,
`#1A1A2E`, com filete inferior.

### Caixa "RESUMO" (acima da tabela)

| Elemento | Valor |
|---|---|
| Fundo | `#EEF5FB` |
| Rótulo `RESUMO` | `#1A5FA8`, caixa alta, negrito, corpo menor |
| Texto | `#1A1A2E` |
| Conteúdo | `Plano:` · `Beneficiária:` · `Período analisado:` na mesma linha, rótulos em negrito; abaixo, um parágrafo curto dizendo de onde vieram os dados |

### Corpo da tabela

Sete colunas: `N°` · `Mês/Ano do Reajuste` · `Competência` · `Valor Anterior (R$)` ·
`Novo Valor (R$)` · `Diferença (R$)` · `Percentual de Aumento (%)` · `Observações`.

| Linha | Fundo | Texto |
|---|---|---|
| Cabeçalho | `#2C3E6B` | branco, negrito, centralizado |
| Linhas ímpares | `#FFFFFF` | `#1A1A2E` |
| Linhas pares (zebra) | `#F5F8FB` | `#1A1A2E` |
| Linha do reajuste vigente | `#FFF8E1` (âmbar claro) | destaque em tom âmbar/ouro |
| Linha `TOTAL ACUMULADO` | `#EEF2F8` | `#1A1A1A`, negrito |

Colunas **Diferença (R$)** e **Percentual de Aumento (%)**: texto em **`#C0392B`**
(vermelho), negrito. É o realce que dá a leitura da peça — manter.

Linha de total: rótulo `TOTAL ACUMULADO (<período>)` com a nota
`(Soma das diferenças — linhas 1 a N)` em corpo menor logo abaixo, na mesma célula.
Preenche só as colunas Diferença, Percentual e Observações.

### Caixa "ANÁLISE RESUMIDA DOS REAJUSTES" (abaixo da tabela)

Fundo `#EEF5FB`; rótulo `#1A5FA8` em caixa alta e negrito. Lista com marcadores, uma
linha por reajuste, valores em negrito. Fecha com linha de fonte em corpo menor,
itálico, indicando o documento de origem.

---

## Tabela 2 — Requisitos da tutela de urgência

Duas linhas, duas colunas. Coluna esquerda estreita (~25%) com o rótulo centralizado
verticalmente; coluna direita com os itens.

| Linha | Fundo da célula esquerda | Texto do rótulo |
|---|---|---|
| `Verossimilhança:` | `#F1F1F1` | `#111111`, negrito |
| `Perigo na demora:` | `#2A2A2A` | **branco**, negrito |

Célula direita: fundo branco, itens separados por parágrafo, cada um iniciado por `✓`.
Valores, percentuais, datas e dispositivos legais em negrito.

---

## Observações de implementação

- **Tudo em `w:tbl`.** Nada de `w:drawing`, nada de PNG. Toda célula digitável.
- **Zebra manual.** Aplicar `w:shd` por linha; não depender de estilo de tabela do Word,
  que o usuário pode não ter.
- **Larguras fixas** em `w:tblGrid`, com `w:tblW` em `pct` para caber na margem A4 do
  escritório (`1560`/`1562` laterais).
- **Fonte Segoe UI** também dentro das tabelas, inclusive no cabeçalho.
- **Não usar `w:documentProtection`.**
- As caixas RESUMO e ANÁLISE podem ser tabelas de uma célula com `w:shd` — mais fiel e
  mais fácil de editar do que parágrafo com sombreamento.

## Divergência de cor a confirmar

O briefing do projeto fixa cabeçalho azul-escuro **`#2E4057`**. O cabeçalho real medido
na peça é **`#2C3E6B`** — próximos, mas não iguais. Como a decisão D5 é "não mudar a
aparência", o Gerador usa **`#2C3E6B`**, o que está no documento. Ver pergunta D9.
