---
name: elaborador-inicial
description: >
  Skill da BM Advocacia que recebe os documentos de um caso de saúde suplementar
  (planilha de cálculo, faturamento ou demonstrativo da operadora, transcrição de
  reunião com o cliente, documentos de suporte) e produz a PETIÇÃO INICIAL em DOCX no
  padrão do escritório, pronta para revisão humana antes do protocolo. Use SEMPRE que
  pedirem para "elaborar inicial", "montar a inicial", "gerar petição inicial" de plano
  de saúde, ou quando enviarem a pasta de documentos de um cliente novo de saúde
  suplementar. Cobre as quatro teses do escritório: falso coletivo empresarial, falso
  coletivo por adesão, autogestão (CASSI, ASSEFAZ, GEAP) e revisional individual. NÃO
  use para réplica, recurso, apelação, embargos, contrarrazões ou cumprimento de
  sentença — há skills separadas para esses.
---

# Elaborador de Petição Inicial — BM Advocacia

> **Estado atual: apenas o módulo 1 (Classificador) está implementado.** Os módulos de
> cálculo, geração de DOCX e conferência ainda não existem. Enquanto isso, a skill
> classifica o caso e apresenta o Espelho, mas **não gera a peça**.

## Escopo

Só **petição inicial**. Se pedirem réplica, recurso inominado, apelação, embargos,
contrarrazões ou cumprimento de sentença, recuse por escopo e indique a skill do
escritório correspondente.

## Fluxo

1. **Extrair** — `python3 scripts/extrair_evidencias.py <arquivos...>` devolve, para
   cada arquivo: o papel do documento, a origem do texto (nativo × digitalizado) e as
   planilhas encontradas. Um arquivo pode conter mais de um documento; o script
   segmenta por página.

2. **Levantar os fatos discriminantes.** O script não interpreta narrativa — isso é
   leitura sua, da transcrição e dos documentos. Preencha os fatos `F1` a `F10`
   (`references/classificador.md`), cada um com **fonte e citação literal**.
   Regra absoluta: **ausência de sinal é `DESCONHECIDO`, nunca `NAO`.**

3. **Classificar** — `python3 scripts/classificar.py evidencias.json` devolve o
   Espelho de Classificação e o dossiê.

4. **Apresentar o Espelho** à operadora e **esperar confirmação explícita**. Mesmo com
   confiança alta, a tese nunca é assumida em silêncio: peça errada protocolada é o
   pior cenário deste projeto.

5. **Responder as perguntas bloqueantes.** Toda pergunta oferece "Não sei / vou
   verificar", e essa resposta **para o processo**. Não insista, não reformule para
   obter um palpite.

## Regras que não se negociam

- **Nunca decida a tese sozinha em caso de dúvida.** Bloqueio é o comportamento
  correto, não uma falha.
- **Nunca trate silêncio como prova.** Se a transcrição não fala de vínculo
  empregatício, isso não significa que não há vínculo.
- **Nunca invente** lei, súmula, tema, julgado ou fato do caso concreto.
- **Nunca infira a tese pela operadora** — a natureza jurídica dela (autogestão ×
  comercial) é um fato a confirmar em `references/operadoras.md`, e o resto vem dos
  documentos.
- **CNPJ, endereço e razão social da ré saem do documento do caso**, nunca de cadastro.
- **Documento que você não identificou vira pergunta**, jamais é descartado em silêncio.
- **Fato lido de documento digitalizado sempre volta para confirmação.**

## Quando a geração existir

- O DOCX tem que ser **nativo e 100% editável**: sem proteção, sem content control, sem
  tabela em imagem. A operadora precisa conseguir corrigir qualquer valor no Word.
- As tabelas mantêm a aparência atual do escritório, mas como `w:tbl` — a paleta está
  em `references/estilo-tabelas.md`.
- O timbre vem das imagens do DOCX-modelo original; nunca montar o arquivo do zero.

## Referências

| Arquivo | Para quê |
|---|---|
| `references/classificador.md` | fatos discriminantes, árvore de decisão, gates |
| `references/operadoras.md` | autogestão × comercial (fato `F1`) |
| `references/estilo-tabelas.md` | paleta e layout das tabelas em formato nativo |
