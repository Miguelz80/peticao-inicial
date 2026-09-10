# Catálogo de teses — roteiro da peça

Este arquivo é **dado, não código**: quem ajusta a redação é a advogada, editando aqui.
O `scripts/roteiro.py` lê este catálogo e monta os blocos do Gerador.

## Formato

```
## TESE: NOME_DA_TESE
### BLOCO: <numeral> | <título>
@condicao: sempre | fato==valor
@fundamentos: o que este bloco tem que sustentar
@pendente: motivo            ← quando não há texto do escritório
Parágrafo. Campos entre chaves são preenchidos: {autor}, {re}, {restituicao}.

Outro parágrafo. **Negrito** com asteriscos duplos.
```

Regras de segurança do preenchimento:

- **Campo sem valor não vira branco.** Placeholder não resolvido interrompe a geração.
  Peça com `{restituicao}` literal ou `R$ ___` no meio do texto é pior que peça nenhuma.
- **Bloco `@pendente` bloqueia a entrega.** Vira marcador visível no DOCX e a Conferência
  não libera. Nunca redigir fundamentação jurídica de improviso para tapar buraco.
- **Nada de lei, súmula, tema ou julgado inventado**, nem provisoriamente.

---

## TESE: CASSI_AUTOGESTAO

Texto extraído de peça real do escritório, protocolada. Vale para qualquer autogestão —
muda a qualificação da ré e o estatuto citado.

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: vínculo longo, reajustes sucessivos, opacidade da metodologia
A parte Autora mantém vínculo contratual com a Ré, sendo beneficiária do plano **{plano}** desde {inicio_contrato}. Durante todo esse período, confiou na regularidade da cobrança das mensalidades, partindo da legítima expectativa de que os reajustes aplicados teriam suporte contratual, técnico e atuarial adequado.

Entretanto, a mensalidade passou a sofrer majorações sucessivas e expressivas, alcançando o valor de **{valor_pago_atual}**, que se mostra incompatível com a capacidade econômica da Autora.

A Ré não apresentou de forma clara e acessível a metodologia utilizada para os reajustes, tampouco disponibilizou memória de cálculo, histórico completo de mensalidades, índices aplicados, demonstração atuarial, base de sinistralidade ou variação de custos médico-hospitalares que permitam aferir a legalidade das cobranças.

Em outras palavras, a Autora é obrigada a pagar, mas não consegue compreender tecnicamente o que está pagando, por que está pagando e se os reajustes efetivamente correspondem a uma necessidade legítima de equilíbrio do contrato.

### BLOCO: II | Da regularidade do reajuizamento e da competência concorrente deste Juízo
@condicao: F10==SIM
@fundamentos: art. 485, VIII e §4º, CPC; art. 53, III, "d", CPC; dever de informação (arts. 5º e 77, CPC)
Em atenção ao dever de informação e boa-fé processual (art. 5º e art. 77, caput e inciso I, do CPC), a Autora expõe o histórico processual que precede o ajuizamento da presente demanda, evitando qualquer omissão apta a comprometer a lisura do processo.

A pretensão foi originalmente deduzida nos autos do processo nº {processo_anterior}, distribuído perante a Comarca de {comarca_anterior}, com pedido expresso de tutela de urgência.

Diante da ausência de apreciação do pedido de urgência, a Autora requereu a desistência da ação anteriormente distribuída, com fundamento no art. 485, VIII, do CPC. Até a desistência não houve citação da parte Ré, tampouco decisão de natureza decisória, de modo que a desistência independeu de anuência da parte contrária e não acarretou qualquer prejuízo processual, material ou probatório.

A Autora é domiciliada em {comarca}, circunstância que autoriza a propositura da demanda perante este Juízo, com fundamento no art. 53, III, "d", do Código de Processo Civil.

### BLOCO: III | Do regime jurídico aplicável aos planos de autogestão
@condicao: sempre
@fundamentos: Súmula 608/STJ (exclusão do CDC); Lei 9.656/98; arts. 113, 187, 421, 421-A e 422 do CC
A presente demanda envolve plano de saúde administrado por entidade de autogestão. Por essa razão, a controvérsia exige tratamento técnico adequado, sem simplificações indevidas.

É certo que o Superior Tribunal de Justiça possui entendimento no sentido de que, em regra, não incide o Código de Defesa do Consumidor sobre os contratos de plano de saúde administrados por entidades de autogestão, em razão das peculiaridades do modelo assistencial, da ausência de finalidade lucrativa típica das operadoras comerciais e da lógica de mutualismo interno entre seus participantes.

Todavia, essa premissa não conduz à conclusão de que os reajustes praticados por entidades de autogestão estariam imunes ao controle judicial. A não incidência automática do CDC não significa autorização para cobrança arbitrária, imposição de reajustes inverificáveis ou dispensa do dever de informação.

O contrato de plano de saúde, ainda quando administrado por autogestão, permanece submetido ao Código Civil, à Lei nº 9.656/98, à regulação da Agência Nacional de Saúde Suplementar, aos princípios da boa-fé objetiva, da função social do contrato e da vedação ao abuso de direito.

O art. 113 do Código Civil impõe que os negócios jurídicos sejam interpretados conforme a boa-fé. O art. 421 estabelece que a liberdade contratual deve ser exercida nos limites da função social do contrato. O art. 422 impõe aos contratantes o dever de guardar, na conclusão e na execução do contrato, os princípios de probidade e boa-fé. E o art. 187 considera ilícito o exercício de direito que exceda manifestamente os limites impostos pelo seu fim econômico ou social.

Assim, ainda que a Ré possua previsão contratual para reajustar a mensalidade, tal prerrogativa não pode ser exercida de forma opaca, desproporcional, imprevisível e economicamente expulsiva.

### BLOCO: IV | Do dever de transparência qualificada
@condicao: sempre
@fundamentos: boa-fé objetiva como cláusula geral de conduta; dever anexo de informação
A controvérsia central desta demanda está diretamente relacionada à ausência de transparência na aplicação dos reajustes.

Não foram apresentados à Autora, de maneira clara e pormenorizada, os índices aplicados, as variáveis consideradas, a memória de cálculo, o histórico completo de evolução dos valores, a base atuarial ou os elementos técnicos que justificariam o atual patamar da cobrança.

Não basta afirmar genericamente que os reajustes decorrem de equilíbrio econômico-financeiro, variação de custos médico-hospitalares, sinistralidade ou necessidade atuarial. Tais expressões, isoladamente consideradas, não comprovam nada: são categorias técnicas que precisam ser demonstradas por documentos, cálculos e relatórios concretos.

### BLOCO: V | Da exibição de documentos e da distribuição dinâmica do ônus da prova
@condicao: sempre
@fundamentos: arts. 396 a 404 do CPC; art. 373, §1º, do CPC; assimetria informacional
A presente ação possui nítido caráter instrutório, pois a Ré detém todos os documentos indispensáveis à apuração da regularidade dos reajustes.

Trata-se de típica hipótese de assimetria informacional. A Autora sabe quanto paga; a Ré sabe por que cobra. A beneficiária consegue demonstrar o valor exigido e o impacto da cobrança sobre sua renda, mas não possui meios técnicos ou documentais para reconstruir a metodologia interna utilizada pela entidade de autogestão.

Impõe-se, portanto, a aplicação dos arts. 396 a 404 do CPC, a fim de determinar que a Ré exiba os documentos necessários ao esclarecimento da controvérsia, bem como a distribuição dinâmica do ônus da prova, nos termos do art. 373, §1º, do CPC, uma vez que a prova da regularidade dos reajustes é de produção muito mais fácil para a Ré.

Não seria razoável impor à Autora o ônus de provar a irregularidade de cálculos que jamais lhe foram apresentados. Tal exigência equivaleria a negar, na prática, o acesso à revisão judicial.

### BLOCO: VI | Da abusividade concreta dos reajustes
@condicao: sempre
@fundamentos: comparação com os índices ANS; boa-fé objetiva; função social do contrato
@tabela: reajuste
Os reajustes aplicados são abusivos não apenas por serem elevados, mas por serem extraordinários, abruptos, imprevisíveis e desacompanhados de justificativa técnica adequada. Vejamos a evolução da mensalidade e o valor que seria devido com a aplicação dos índices autorizados pela ANS:

A mensalidade atual de **{valor_pago_atual}** contrasta com o valor devido de **{valor_devido_atual}**, apurado com a aplicação dos índices da ANS ano a ano — uma diferença mensal de **{diferenca_mensal}**.

A imposição de reajustes dessa ordem, sem demonstração técnica acessível, viola a boa-fé objetiva e a função social do contrato, pois submete a beneficiária a uma escolha materialmente injusta: pagar prestação excessiva e comprometer sua subsistência ou deixar de pagar e correr o risco de perder cobertura assistencial construída ao longo de anos.

A lógica de mutualismo das autogestões não autoriza que o custo seja repassado de maneira incontrolável ao beneficiário. O mutualismo pressupõe equilíbrio, solidariedade e repartição racional de riscos, não imposição unilateral de reajuste ininteligível.

### BLOCO: VII | Do direito à restituição dos valores pagos a maior
@condicao: sempre
@fundamentos: arts. 876 e 884 do CC; Tema 610/STJ (prescrição trienal). NÃO usar art. 42, § único, do CDC — sem incidência do CDC, a dobra perde base direta
Reconhecida a abusividade dos reajustes aplicados, impõe-se a restituição dos valores pagos a maior, sob pena de permitir que a entidade retenha quantias recebidas sem justificativa jurídica legítima.

A restituição encontra respaldo direto no artigo 876 do Código Civil, que estipula que quem recebeu valores indevidos deve restituí-los. De forma análoga, a manutenção de valores cobrados sem a devida comprovação técnica configura enriquecimento sem causa, conforme o artigo 884 do Código Civil.

Observada a prescrição trienal (Tema 610 do STJ), a restituição alcança os valores pagos a maior nos últimos três anos, no montante de **{restituicao}**, apurado na tabela anexa e sujeito a conferência em liquidação.

### BLOCO: VIII | Da tutela de urgência
@condicao: F6==ATIVO
@fundamentos: art. 300 do CPC; probabilidade do direito e perigo de dano; reversibilidade
@tabela: tutela
A concessão da tutela de urgência é fundamentada no artigo 300 do Código de Processo Civil, diante da presença simultânea da probabilidade do direito e do perigo de dano.

A medida é reversível, pois qualquer diferença poderá ser ajustada ao final, após perícia atuarial ou liquidação de sentença. A ausência de tutela, por outro lado, acarretaria danos de difícil reparação, incluindo a perda da cobertura médica e o comprometimento da subsistência da Autora.

Requer-se, assim, a limitação provisória da mensalidade ao patamar de **{valor_devido_atual}**, valor apurado com a aplicação dos índices da ANS.

### BLOCO: IX | Da gratuidade de justiça
@condicao: sempre
@fundamentos: arts. 98 e 99 do CPC; presunção do art. 99, §3º; distinguir renda de liquidez
A Autora requer a concessão dos benefícios da gratuidade da justiça, nos termos dos arts. 98 e 99 do Código de Processo Civil, por não possuir condições de arcar com as custas processuais, despesas judiciais, honorários periciais e demais encargos do processo sem prejuízo de sua própria subsistência.

A mensalidade de **{valor_pago_atual}** representa, sozinha, parcela expressiva da renda da Autora. Trata-se de gasto indispensável, vinculado à preservação da saúde e à continuidade assistencial, não podendo ser tratado como despesa supérflua.

A gratuidade não deve ser indeferida com base apenas na existência de renda formal. O que se deve analisar é se a parte possui efetiva disponibilidade financeira para custear o processo sem comprometer sua manutenção digna. Nos termos do art. 99, §3º, do CPC, presume-se verdadeira a alegação de insuficiência deduzida por pessoa natural.

### BLOCO: X | Da prioridade de tramitação
@condicao: F9>=60
@fundamentos: art. 71 da Lei 10.741/2003; art. 1.048, I, do CPC
A Autora, contando com {idade} anos de idade, faz jus à prioridade de tramitação, nos termos do art. 71 da Lei nº 10.741/2003 (Estatuto da Pessoa Idosa) c/c art. 1.048, inciso I, do Código de Processo Civil.

### BLOCO: XI | Do processo 100% digital
@condicao: sempre
@fundamentos: padrão do escritório
A parte Autora manifesta expressa concordância com a tramitação do feito em formato 100% digital.

---

## TESE: EMPRESARIAL_FAMILIAR
@pendente: falta o texto do escritório. O modelo `PETIÇÃO INICIAL-MODELO APENAS RESTITUIÇÃO.docx` não foi disponibilizado, e a redação dos blocos jurídicos não pode ser improvisada.

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: qualificação da PJ autora representada pelo sócio; contratação do plano; reajustes sucessivos
@pendente: texto do escritório

### BLOCO: II | Da aplicabilidade do CDC por equiparação
@condicao: sempre
@fundamentos: arts. 2º e 29 do CDC — consumidor por equiparação, porque a PJ foi criada para viabilizar o plano familiar. Não substituir pela Súmula 608 isoladamente: os dois argumentos coexistem
@pendente: texto do escritório

### BLOCO: III | Do reconhecimento do plano empresarial como familiar
@condicao: sempre
@fundamentos: bloco central. Demonstrar com fatos do caso concreto — empresa sem movimentação ou atividade real; beneficiários exclusivamente do mesmo núcleo familiar; inexistência de vínculo empregatício; empresa constituída para viabilizar o plano
@pendente: texto do escritório

### BLOCO: IV | Da equiparação a plano individual para fins de reajuste
@condicao: sempre
@fundamentos: consequência do falso coletivo — aplicação dos índices ANS de planos individuais, e não redução genérica de mensalidade
@pendente: texto do escritório

### BLOCO: V | Do reajuste por sinistralidade
@condicao: sempre
@fundamentos: exigir comprovação técnica e atuarial do próprio grupo de beneficiários; na ausência, abusividade e substituição pelos índices ANS
@pendente: texto do escritório

### BLOCO: VI | Do reajuste por faixa etária
@condicao: F7==SIM
@fundamentos: Tema 952/STJ e Tema 1016/STJ — previsão contratual expressa, observância das normas da ANS, ausência de percentuais desarrazoados
@pendente: texto do escritório

### BLOCO: VII | Da rescisão indireta por onerosidade excessiva
@condicao: F6==CANCELADO
@fundamentos: usar somente se o plano já foi cancelado pela parte autora
@pendente: texto do escritório

### BLOCO: VIII | Da tutela de urgência para readequação
@condicao: F6==ATIVO
@fundamentos: art. 300 do CPC — caminho alternativo ao anterior, quando o plano segue ativo
@pendente: texto do escritório

### BLOCO: IX | Da restituição dos valores pagos a maior
@condicao: sempre
@fundamentos: art. 42, parágrafo único, do CDC (dobro) ou art. 876 do CC (simples) — decisão humana; Tema 610/STJ
@pendente: texto do escritório

### BLOCO: X | Da gratuidade de justiça da pessoa jurídica
@condicao: sempre
@fundamentos: não serve a hipossuficiência genérica de pessoa física — explicar que a empresa foi constituída apenas para sustentar o plano, sem receita relevante
@pendente: texto do escritório

---

## TESE: COLETIVO_POR_ADESAO
@pendente: falta o texto do escritório. O modelo `MODELO PETIÇÃO INICIAL COLETIVO POR ADESÃO.docx` não foi disponibilizado.

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: pessoa física aderente via associação ou sindicato
@pendente: texto do escritório

### BLOCO: II | Do falso coletivo por adesão
@condicao: sempre
@fundamentos: ausência de vínculo associativo real; equiparação a individual para fins de reajuste. NÃO confundir com falso coletivo empresarial
@pendente: texto do escritório

### BLOCO: III | Da tutela de urgência para readequação
@condicao: F6==ATIVO
@fundamentos: art. 300 do CPC
@pendente: texto do escritório

---

## TESE: INDIVIDUAL_COMUM
@pendente: falta o modelo DOCX do revisional individual comum (pergunta B2) e o texto correspondente.

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: contratação direta com a operadora; reajustes acima do teto ANS
@pendente: texto do escritório

### BLOCO: II | Da abusividade do reajuste acima do teto ANS
@condicao: sempre
@fundamentos: plano individual já é regulado pela ANS — o reajuste acima do teto é abusivo por si
@pendente: texto do escritório
