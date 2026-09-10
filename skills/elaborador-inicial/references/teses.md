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
@revisar: texto redigido a partir dos fundamentos documentados na skill `corretor-inicial-empresarial-familiar`, NÃO extraído de peça real do escritório. Gera peça completa, mas precisa de leitura da advogada antes do primeiro protocolo. Substituir assim que houver uma peça dessa tese.

Contratante é pessoa jurídica sem atividade econômica real, criada para viabilizar o
plano da família. A **autora é a PJ**, representada pelo sócio administrador — conferir
que a qualificação não foi trocada pela da pessoa física.

Sem ementas: citar julgado exige escolher julgado, e essa escolha é da advogada. Os
capítulos indicam onde a jurisprudência entra.

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: qualificação da PJ autora representada pelo sócio; contratação do plano para o núcleo familiar; reajustes sucessivos
A Autora, pessoa jurídica qualificada na epígrafe, representada por seu sócio administrador, é titular do contrato coletivo empresarial de plano de saúde **{plano}**, celebrado com a Ré em {inicio_contrato}.

A contratação, embora formalmente empresarial, teve por finalidade exclusiva viabilizar a assistência à saúde dos membros de um mesmo núcleo familiar, únicos beneficiários do plano desde a adesão.

Ao longo da contratualidade, a mensalidade sofreu majorações sucessivas e expressivas, alcançando **{valor_pago_atual}** em {competencia_atual}, sem que fosse apresentada qualquer demonstração técnica ou atuarial que justificasse os percentuais aplicados.

### BLOCO: II | Da aplicabilidade do Código de Defesa do Consumidor por equiparação
@condicao: sempre
@fundamentos: arts. 2º e 29 do CDC — consumidor por equiparação. A incidência NÃO decorre diretamente da Súmula 608, que trata do consumidor pessoa física; os dois argumentos coexistem
@revisar: jurisprudência sobre consumidor por equiparação a incluir
A relação jurídica em exame submete-se ao Código de Defesa do Consumidor. Ainda que a contratante seja pessoa jurídica, sua posição no contrato é de destinatária final do serviço, sem qualquer finalidade de incremento de atividade econômica.

O art. 2º do Código de Defesa do Consumidor define consumidor como toda pessoa física ou jurídica que adquire ou utiliza produto ou serviço como destinatário final. O art. 29, por sua vez, equipara a consumidor todas as pessoas, determináveis ou não, expostas às práticas nele previstas.

A empresa contratante não explora atividade econômica relevante e foi constituída, em caráter predominante, para viabilizar a contratação do plano de saúde dos membros da família. Não há, portanto, a vulnerabilidade mitigada que caracteriza a contratação empresarial genuína, mas a mesma hipossuficiência técnica e informacional que o Código protege.

### BLOCO: III | Do reconhecimento do plano empresarial na modalidade familiar
@condicao: sempre
@fundamentos: bloco central da tese. Os quatro elementos fáticos têm que vir do caso concreto, não de fórmula genérica — se faltarem, a peça não se sustenta
@revisar: jurisprudência sobre falso coletivo empresarial a incluir
O contrato em exame, embora formalmente classificado como coletivo empresarial, funciona na prática como plano individual ou familiar, o que impõe seu reconhecimento como tal para fins de controle de reajuste.

Quatro elementos, demonstrados pela documentação anexa, sustentam essa conclusão: a empresa estipulante não possui movimentação financeira relevante nem atividade econômica efetiva; os beneficiários do plano são exclusivamente membros de um mesmo núcleo familiar; inexiste vínculo empregatício entre os beneficiários e a pessoa jurídica; e a constituição da empresa teve por propósito predominante viabilizar a contratação do plano de saúde.

A prevalecer a forma sobre a substância, o resultado prático seria permitir que a operadora se subtraia aos limites de reajuste fixados pela Agência Nacional de Saúde Suplementar para os planos individuais, submetendo um grupo familiar a majorações sem teto e sem controle — exatamente o que a qualificação empresarial, nesse contexto, encobre.

### BLOCO: IV | Da equiparação a plano individual para fins de reajuste
@condicao: sempre
@fundamentos: consequência do reconhecimento — aplicação dos índices ANS de planos individuais. O pedido tem que estar entrelaçado com a causa de pedir, não pedir "redução genérica"
@tabela: reajuste
Reconhecida a natureza familiar do contrato, impõe-se a aplicação, como parâmetro de razoabilidade, dos índices máximos de reajuste anual divulgados pela Agência Nacional de Saúde Suplementar para os planos individuais e familiares.

A tabela a seguir demonstra a evolução da mensalidade efetivamente cobrada e o valor que seria devido caso os reajustes tivessem observado os índices da ANS ano a ano:

A mensalidade atual de **{valor_pago_atual}** contrasta com o valor devido de **{valor_devido_atual}** — diferença mensal de **{diferenca_mensal}** suportada indevidamente pela Autora.

### BLOCO: V | Da abusividade dos reajustes por sinistralidade e VCMH
@condicao: sempre
@fundamentos: art. 17-A, §2º, II, da Lei 9.656/98; arts. 6º, III e V, e 51 do CDC. Exige base atuarial do próprio grupo, não da carteira
@revisar: jurisprudência sobre ausência de comprovação atuarial a incluir
Ainda que se admita, em tese, o reajuste fundado em sinistralidade ou em variação de custos médico-hospitalares, sua validade depende da demonstração técnica específica da base atuarial utilizada, com dados concretos e individualizados referentes ao grupo de beneficiários do próprio contrato.

Relatórios genéricos, referentes a outras coletividades ou à carteira da operadora como um todo, não suprem essa exigência: impedem a aferição da necessidade e da razoabilidade dos percentuais e transferem ao consumidor o risco inerente à atividade econômica da operadora.

A ausência dessa comprovação caracteriza abusividade, por impor desvantagem excessiva e impedir o controle da onerosidade contratual, em afronta aos arts. 6º, III e V, e 51 do Código de Defesa do Consumidor.

### BLOCO: VI | Da abusividade do reajuste por faixa etária
@condicao: F7==SIM
@fundamentos: Temas 952 e 1016 do STJ — requisitos cumulativos: previsão contratual expressa, observância das normas da ANS, ausência de percentuais desarrazoados sem base atuarial idônea
@revisar: jurisprudência sobre faixa etária a incluir
O reajuste por mudança de faixa etária somente é válido quando cumpridos, cumulativamente, três requisitos: previsão contratual expressa do percentual aplicável; observância das normas expedidas pelos órgãos governamentais reguladores; e ausência de percentuais desarrazoados ou aleatórios que, sem base atuarial idônea, onerem excessivamente o consumidor ou discriminem o idoso.

Na hipótese, a Ré não apresentou o percentual contratualmente previsto para a faixa etária aplicada, tampouco a base atuarial que o sustentaria, o que impede o controle jurisdicional de sua razoabilidade e caracteriza violação ao dever de informação adequada.

### BLOCO: VII | Da rescisão indireta por onerosidade excessiva
@condicao: F6==CANCELADO
@fundamentos: usar SOMENTE quando o plano já foi cancelado pela parte autora em razão dos reajustes. Excludente do capítulo de tutela de urgência
@revisar: confirmar com a advogada a redação deste caminho
A Autora viu-se compelida a cancelar o plano de saúde em razão da onerosidade excessiva decorrente dos reajustes impugnados, o que caracteriza rescisão motivada pela conduta da Ré e não afasta o direito à restituição dos valores pagos a maior durante a vigência do contrato.

### BLOCO: VIII | Da tutela de urgência
@condicao: F6==ATIVO
@fundamentos: art. 300 do CPC; probabilidade do direito e perigo da demora; reversibilidade da medida
A concessão da tutela de urgência encontra fundamento no art. 300 do Código de Processo Civil, diante da presença simultânea da probabilidade do direito e do perigo de dano.

A probabilidade do direito decorre da documentação anexa, que demonstra a natureza familiar da contratação e a aplicação de reajustes desacompanhados de justificativa técnica. O perigo da demora reside no risco concreto de inadimplência e consequente cancelamento do plano, com perda da cobertura assistencial construída ao longo da contratualidade.

A medida é reversível, pois eventual diferença poderá ser ajustada ao final. Requer-se, assim, a limitação provisória da mensalidade ao patamar de **{valor_devido_atual}**, apurado com a aplicação dos índices da ANS.

### BLOCO: IX | Da exibição de documentos e da distribuição dinâmica do ônus da prova
@condicao: sempre
@fundamentos: arts. 396 a 404 e art. 400 do CPC; art. 373, §1º, do CPC; art. 6º, VIII, do CDC
A Autora não detém os documentos indispensáveis à apuração da regularidade dos reajustes, que permanecem sob guarda exclusiva da Ré: memória de cálculo, relatórios de sinistralidade do grupo, premissas atuariais e histórico completo de mensalidades.

Impõe-se, por isso, a exibição documental nos termos dos arts. 396 a 404 do Código de Processo Civil e do art. 6º, VIII, do Código de Defesa do Consumidor, sob pena de aplicação do art. 400 do mesmo diploma, bem como a distribuição dinâmica do ônus da prova (art. 373, §1º, do CPC), por ser a prova da regularidade dos reajustes de produção muito mais fácil para a Ré.

### BLOCO: X | Do direito à restituição dos valores pagos a maior
@condicao: sempre
@fundamentos: art. 42, parágrafo único, do CDC (dobro) OU art. 876 do CC (simples) — a escolha é decisão humana, o Classificador não decide; Tema 610/STJ para a prescrição trienal
Reconhecida a abusividade dos reajustes, surge o direito à restituição dos valores pagos a maior, sob pena de enriquecimento sem causa da Ré.

Observada a prescrição trienal firmada no Tema 610 do Superior Tribunal de Justiça, a restituição alcança os valores pagos a maior nos três anos anteriores ao ajuizamento, no montante de **{restituicao}**, apurado na tabela anexa e sujeito a conferência em liquidação, acrescido de correção monetária desde cada desembolso e juros de mora a partir da citação.

### BLOCO: XI | Da gratuidade de justiça da pessoa jurídica
@condicao: sempre
@fundamentos: arts. 98 e 99 do CPC. A fundamentação NÃO pode ser a hipossuficiência genérica de pessoa física — a presunção do art. 99, §3º não alcança a PJ, que precisa demonstrar a insuficiência
@revisar: confirmar se a gratuidade é pedida em todos os casos de PJ
A Autora requer a concessão dos benefícios da gratuidade de justiça, nos termos dos arts. 98 e 99 do Código de Processo Civil.

Tratando-se de pessoa jurídica, a Autora não se vale da presunção do art. 99, §3º, do Código de Processo Civil, e demonstra concretamente sua insuficiência de recursos: a empresa não possui receita relevante além do necessário à manutenção do próprio plano de saúde, cujos custos consomem os recursos disponíveis, não restando margem para o recolhimento de custas, despesas processuais e eventuais honorários periciais.

{narrativa_hipossuficiencia}

### BLOCO: XII | Do processo 100% digital
@condicao: sempre
@fundamentos: padrão do escritório
A parte Autora manifesta expressa concordância com a tramitação do feito em formato 100% digital.

---

## TESE: COLETIVO_POR_ADESAO

Texto extraído de peça real do escritório, protocolada — pessoa física aderente a plano
coletivo por adesão via administradora de benefícios. As ementas vêm da própria peça;
o que começa com `>` sai recuado e em itálico, no padrão do escritório para julgados.

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: adesão ao plano, ausência de poder de negociação, reajustes sucessivos
A parte Autora é beneficiária do plano **{plano}** desde {inicio_contrato}, tendo aderido a contrato formalmente classificado como coletivo por adesão, intermediado por administradora de benefícios.

Ao longo da contratualidade, a mensalidade sofreu majorações sucessivas e expressivas, alcançando **{valor_pago_atual}** em {competencia_atual}, valor incompatível com a capacidade econômica da Autora e com os parâmetros de reajuste autorizados pela ANS para planos individuais.

A Autora jamais recebeu memória de cálculo, demonstração atuarial, relatório de sinistralidade do seu grupo ou qualquer elemento técnico que permitisse aferir a legalidade dos percentuais aplicados.

### BLOCO: II | Da aplicabilidade do CDC e da natureza de falso coletivo
@condicao: sempre
@fundamentos: Súmula 608/STJ; adesão sem poder de negociação; equiparação a individual para fins de reajuste. NÃO confundir com falso coletivo empresarial (PJ contratante)

A relação jurídica entre as partes é inequivocamente de consumo, atraindo a incidência do Código de Defesa do Consumidor (CDC), conforme pacificado pela Súmula 608 do STJ:

STJ Aplica-se o Código de Defesa do Consumidor aos contratos de plano de saúde, salvo os administrados por entidades de autogestão.

O contrato em tela, embora formalmente classificado como "coletivo por adesão", na prática, funciona como um plano individual. A Autora aderiu ao plano, sem qualquer poder de negociação sobre as cláusulas contratuais, caracterizando-se como um contrato "falso coletivo". Tal artifício é frequentemente utilizado pelas operadoras para se esquivar da fiscalização da ANS, que estabelece tetos para os reajustes de planos individuais.

A jurisprudência pátria é uníssona em reconhecer a abusividade dessa prática, determinando que tais contratos sejam equiparados aos planos individuais para fins de reajuste, aplicando-se, por analogia, os índices anuais fixados pela ANS.

### BLOCO: III | Da abusividade dos reajustes
@condicao: sempre
@fundamentos: arts. 6º, III e V, e 51 do CDC; ausência de comprovação atuarial do grupo; substituição pelos índices ANS
@tabela: reajuste

Conforme demonstrado pelos documentos anexados, as Rés vêm aplicando sucessivos reajustes nas mensalidades do plano de saúde da parte autora sem apresentar qualquer comprovação técnica idônea que justifique os percentuais adotados, o que revela evidente abusividade na execução do contrato.

Embora a Agência Nacional de Saúde Suplementar – ANS não estabeleça limites objetivos para os reajustes aplicáveis aos planos coletivos, tal circunstância não autoriza a majoração unilateral e desarrazoada das mensalidades pelas operadoras, sobretudo quando inexistem elementos técnicos que comprovem a efetiva variação de custos ou de sinistralidade do grupo de beneficiários.

Isso porque, nos termos da Súmula 608 do Superior Tribunal de Justiça, os contratos de plano de saúde coletivo submetem-se às normas do Código de Defesa do Consumidor, impondo-se a observância dos princípios da boa-fé objetiva, da transparência e do equilíbrio contratual.

Assim, ainda que seja admitida, em tese, a aplicação de reajustes com base na sinistralidade ou na variação dos custos médico-hospitalares, a validade desses aumentos depende da demonstração técnica específica da base atuarial utilizada, com dados concretos e individualizados referentes ao grupo de beneficiários do contrato.

A ausência dessa comprovação caracteriza manifesta abusividade, pois impede o controle da razoabilidade dos percentuais aplicados e impõe ao consumidor desvantagem excessiva, em afronta aos arts. 6º, III e V, e 51 do Código de Defesa do Consumidor.

Nesse sentido, a jurisprudência tem reconhecido que, na ausência de comprovação técnica idônea da necessidade dos reajustes, mostra-se legítima a substituição dos índices aplicados pelos percentuais divulgados pela ANS para planos individuais, utilizados como parâmetro de razoabilidade e controle da abusividade contratual.

Legislação e jurisprudência:

> DIREITO CIVIL E DO CONSUMIDOR. PLANO DE SAÚDE COLETIVO POR ADESÃO. REAJUSTES ANUAIS POR SINISTRALIDADE E VCMH. AUSÊNCIA DE TRANSPARÊNCIA E DE COMPROVAÇÃO ATUARIAL ESPECÍFICA. ABUSIVIDADE RECONHECIDA. SUBSTITUIÇÃO PELOS ÍNDICES DA ANS. RESPONSABILIDADE SOLIDÁRIA DA ADMINISTRADORA DE BENEFÍCIOS. RECURSOS DESPROVIDOS. (...) III. RAZÕES DE DECIDIR 3- A administradora de benefícios integra a cadeia de fornecimento do serviço e responde solidariamente por eventuais abusividades contratuais, nos termos do art . 7º, parágrafo único, do Código de Defesa do Consumidor (CDC). Sua atuação não é meramente intermediária, pois participa ativamente da negociação, comunicação e execução dos reajustes aplicados aos beneficiários. 4- A relação jurídica de plano de saúde coletivo por adesão está sujeita às normas do CDC, conforme a Súmula nº 608 do Superior Tribunal de Justiça, impondo a aplicação dos princípios da boa-fé objetiva, transparência e informação adequada ao consumidor. 5- Embora o reajuste por sinistralidade e VCMH seja admitido em contratos coletivos (art . 17-A, § 2º, II, da Lei nº 9.656/98), sua validade depende da comprovação técnica específica da base atuarial utilizada, com dados referentes ao grupo de beneficiários efetivo do contrato. 6- As rés não comprovaram, por meio de documentação idônea e individualizada, que os índices aplicados entre 2020 e 2023 correspondiam à variação real da sinistralidade e dos custos do grupo da autora (UNE). Os relatórios apresentados referiam-se a outras coletividades, inviabilizando a aferição da necessidade e razoabilidade dos percentuais. 7- A falta de transparência e de prova atuarial específica caracteriza abusividade, por violar os arts. 6º, III e V, e 47 do CDC, impondo desvantagem excessiva ao consumidor e impedindo o controle da onerosidade contratual. 8- A substituição dos índices aplicados pelos percentuais divulgados pela ANS para planos individuais não equipara juridicamente as modalidades contratuais, mas funciona como parâmetro de razoabilidade e sanção pela falta de transparência do fornecedor, conforme consolidado na jurisprudência do TJSP. 9- A manutenção da sentença assegura o equilíbrio contratual, protege o consumidor hipossuficiente e respeita a boa-fé e a função social do contrato de saúde suplementar. IV. DISPOSITIVO E TESE 10- Recursos desprovidos. Sentença mantida. Tese de julgamento: 1- A administradora de benefícios integra a cadeia de consumo e responde solidariamente por abusividades na execução do contrato de plano de saúde coletivo por adesão. 2- É abusivo o reajuste anual por sinistralidade e VCMH quando a operadora não comprova, de forma clara e por meio de documentação atuarial idônea, a variação de custos e a frequência de utilização que justificaram os percentuais aplicados. 3- Na ausência de prova técnica específica, é legítima a substituição dos reajustes pelos índices anuais máximos divulgados pela ANS para planos individuais, como parâmetro de controle de razoabilidade e transparência. (...) (TJ-SP - Apelação Cível: 10271919720238260001 São Paulo, Relator.: Marcio Bonetti, Data de Julgamento: 27/11/2025, Núcleo de Justiça 4.0 em Segundo Grau – Turma II (Direito Privado 1), Data de Publicação: 27/11/2025) (Grifo nosso).

> DIREITO DO CONSUMIDOR. PLANO DE SAÚDE COLETIVO POR ADESÃO. REAJUSTE POR SINISTRALIDADE. ABUSIVIDADE. AUSÊNCIA DE COMPROVAÇÃO DA NECESSIDADE E RAZOABILIDADE DOS AUMENTOS. SUBSTITUIÇÃO PELOS ÍNDICES AUTORIZADOS PELA ANS. DEVOLUÇÃO DOS VALORES PAGOS A MAIOR. RECURSO PROVIDO. (...) III. Razões de decidir A aplicação do Código de Defesa do Consumidor aos contratos de plano de saúde, conforme entendimento consolidado pelo STJ (Súmula 608), exige transparência e justificativa adequada para os reajustes praticados. A operadora não apresentou provas idôneas da necessidade dos reajustes, limitando-se a argumentar a legalidade dos aumentos sem respaldo documental. A jurisprudência majoritária reconhece que, na ausência de comprovação objetiva dos reajustes, os aumentos devem ser limitados aos índices da ANS. Impõe-se a devolução dos valores pagos a maior, de forma simples, nos últimos três anos, corrigidos pelo IPCA-E e acrescidos de juros de mora de 1% ao mês. (...) (TJ-PE - APELAÇÃO CÍVEL: 00665466320248172001, Relator.: AIRTON MOZART VALADARES VIEIRA PIRES, Data de Julgamento: 03/07/2025, 8ª Câmara Cível Especializada - 3º (8CCE-3º)) (Grifo nosso).

Dessa forma, resta evidente que os reajustes aplicados no contrato da parte autora foram realizados sem transparência e sem comprovação técnica adequada, transferindo indevidamente ao consumidor o risco inerente à atividade econômica exercida pelas operadoras de plano de saúde.

Assim, requer o reconhecimento da abusividade dos reajustes aplicados, com a consequente revisão das mensalidades mediante a aplicação dos índices autorizados pela ANS, bem como a restituição dos valores pagos a maior pela parte autora.

### BLOCO: IV | Da abusividade do reajuste de faixa etária
@condicao: F7==SIM
@fundamentos: Temas 952 e 1016/STJ — previsão contratual expressa, normas da ANS, ausência de percentuais desarrazoados; exibição do instrumento contratual

Conforme é cediço, a apresentação do instrumento contratual é imprescindível para versar sobre a aplicabilidade correta dos índices a título de reajuste por faixa etária.

Diante dessa omissão, impõe-se que as Rés apresentem expressamente o percentual contratual previsto para o reajuste por faixa etária aplicável ao contrato da Autora, a fim de que este Juízo possa aferir a legalidade e a razoabilidade do índice eventualmente utilizado. A ausência dessa informação impede o controle jurisdicional da abusividade e caracteriza violação ao dever de transparência e informação adequada previsto no Código de Defesa do Consumidor.

Assim se extrai de trecho extraído do site da ANS, onde percebe-se que a normativa é taxativa, uma vez que versa, expressamente, sobre a necessidade de estar disposto em contrato. Assim vejamos:

Isso acontece porque, em geral, por questões naturais, quanto mais idosa a pessoa, mais necessários e mais frequentes se tornam os cuidados com a saúde. As faixas etárias variam conforme a data de contratação do plano e os percentuais de variação precisam estar expressos no contrato.

As faixas etárias para correção variam conforme a data de contratação do plano, sendo que os percentuais de variação têm que estar expressos no contrato.

Ato contínuo, chama atenção para o entendimento do STJ, em relação ao quanto aludido nesta exordial, senão vejamos:

(I) haja previsão contratual,

(II) sejam observadas as normas expedidas pelos órgãos governamentais reguladores e

(III) não sejam aplicados percentuais desarrazoados ou aleatórios que, concretamente e sem base atuarial idônea, onerem excessivamente o consumidor ou discriminem o idoso.

Em questões semelhantes à aqui tratada, a jurisprudência pátria tem entendimento consolidado no sentido de que os referidos reajustes podem ser retirados da base de cálculo, tendo em vista a sua abusividade, quando as seguradoras não apresentam a informação devidamente. Nesse sentido:

> DIREITO CIVIL. APELAÇÃO. PLANO DE SAÚDE. REAJUSTE POR FAIXA ETÁRIA . ABUSIVIDADE RECONHECIDA. (...) III. Razões de Decidir: 3. O recurso não comporta conhecimento com relação à existência e legalidade dos reajustes em razão a idade do contratante, pois tais questões restaram decididas em decisão pregressa desta C. Câmara, já transitada em julgado. 4 . Na parte conhecida, o apelo comporta acolhimento, pois a operadora não apresentou a documentação atuarial necessária para verificar a razoabilidade dos reajustes, conforme exigido pelo acórdão anterior. 5. A falta de base atuarial impede a aplicação dos reajustes, conforme precedentes do TJSP, reconhecendo a abusividade dos aumentos. IV . Dispositivo e Tese 6. Recurso provido em sua parte conhecida para declarar a abusividade dos reajustes por faixa etária, com devolução simples dos valores pagos a maior nos três anos anteriores ao ajuizamento da ação. Tese de julgamento: 1. A ausência de documentação atuarial impede a aplicação de reajustes por faixa etária, sendo reconhecida a abusividade dos reajustes . (TJ-SP - Apelação Cível: 10887395420228260100 São Paulo, Relator.: Lucilia Alcione Prata, Data de Julgamento: 16/04/2025, 6ª Câmara de Direito Privado, Data de Publicação: 16/04/2025) (Grifo nosso).

Assim sendo, é imprescindível a apresentação do referido instrumento devidamente outorgado pelas partes a fim de constatar os fatores aplicados ao plano de saúde da parte autora, pelo que se requer.

### BLOCO: V | Da abusividade dos reajustes por sinistralidade e VCMH
@condicao: sempre
@fundamentos: art. 17-A, §2º, II, da Lei 9.656/98; art. 51, IV e X, do CDC; exige base atuarial do grupo, não da carteira

O Superior Tribunal de Justiça pacificou o entendimento de que os reajustes por sinistralidade ou VCMH em planos coletivos não podem ser aplicados de forma arbitrária ou por meros relatórios genéricos da carteira. Exige-se das operadoras a comprovação técnica e idônea da base atuarial específica do grupo do contratante.

Na hipótese em tela, as Réus aplicaram reajustes exorbitantes de até {maior_reajuste} ao ano sem apresentar os demonstrativos analíticos de cálculo atuarial, nem os relatórios de sinistralidade individualizados do grupo em questão. Tal postura configura flagrante violação aos princípios da boa-fé objetiva, transparência e ao art. 51, IV e X, do CDC.  Nesse sentido, vejamos jurisprudência:

> APELAÇÃO CÍVEL. DIREITO DO CONSUMIDOR. PLANO DE SAÚDE COLETIVO. SENTENÇA QUE JULGOU PROCEDENTE O PEDIDO PARA DECLARAR A ABUSIVIDADE E A NULIDADE DO AUMENTO DE SINISTRALIDADE EM 43,64% APLICADO NO ANO DE 2020, NA MENSALIDADE DE 03 .2020; CONDENAR A RÉ A PROCEDER AOS REAJUSTES NOS ÍNDICES FIXADOS PELA ANS, SENDO DE 10% (DEZ POR CENTO) O PERCENTUAL PARA O ANO DE 2020; CONDENAR A RÉ A DEVOLVER A QUANTIA PAGA A MAIS, EM DOBRO, NA FORMA DO ART. 42, PARÁGRAFO ÚNICO, DO CDC; E CONDENAR A RÉ A PAGAR INDENIZAÇÃO POR DANOS MORAIS NO VALOR DE R$ 2.000,00 (DOIS MIL REAIS). REAJUSTE EM PERCENTUAL ABUSIVO À LUZ DO CDC . DESEQUILÍBRIO DO CONTRATO. ONEROSIDADE EXCESSIVA. OPERADORA DO PLANO DE SAÚDE QUE NÃO PROVOU A LEGALIDADE DOS AUMENTOS. ÔNUS QUE COMPETE AO REU, NA FORMA DO ARTIGO 373, II, DO CPC . FALHA NA PRESTAÇÃO DE SERVIÇO CONFIGURADA. DEVOLUÇÃO EM DOBRO ANTE À VIOLAÇÃO À BOA-FÉ OBJETIVA. DANO MORAL CONFIGURADO. VERBA FIXADA QUE ESTÁ ATÉ MESMO ABAIXO DA NORMALMENTE ARBITRADA NO TJRJ . RECURSO CONHECIDO A QUE SE NEGA PROVIMENTO. (TJ-RJ - APELAÇÃO: 01742301820208190001, Relator.: Des(a). LUCIA HELENA DO PASSO, Data de Julgamento: 17/03/2022, DECIMA PRIMEIRA CAMARA DE DIREITO PRIVADO (ANTIGA 27ª CÂMARA CÍVEL), Data de Publicação: 22/03/2022) (Grifo nosso)

Diante da ausência de demonstração cabal do cálculo atuarial pelas Rés, impõe-se a declaração de abusividade dos reajustes aplicados e a substituição dos percentuais pelos índices oficiais fixados pela ANS para os contratos individuais/familiares

### BLOCO: VI | Do direito à restituição dos valores pagos a maior
@condicao: sempre
@fundamentos: art. 876 do CC; Tema 610/STJ (prescrição trienal); restituição simples ou em dobro é decisão humana

Uma vez reconhecida a abusividade dos reajustes (tanto anuais quanto por faixa etária), surge para a Autora o direito à devolução dos valores pagos a maior ao longo de toda a contratualidade, nos termos do art. 876 do Código Civil.

Conforme demonstrado nas linhas acima, a parte Autora efetuou o pagamento de valores indevidamente em razão do reajuste abusivo das mensalidades.

Sendo assim, observa-se que a Autora pagou o total de {restituicao}, a mais do que realmente era devido, nos últimos 3 anos, uma grande quantia a ser cobrada de forma indevida e ilegal.

Considerando o princípio da razoabilidade e a celeridade processual, a Autora requer a restituição dos valores, devidamente corrigida monetariamente desde cada desembolso e acrescida de juros de mora a partir da citação.

### BLOCO: VII | Da tutela de urgência
@condicao: F6==ATIVO
@fundamentos: art. 300 do CPC; probabilidade do direito e perigo da demora; risco de cancelamento por inadimplência

A probabilidade do direito encontra-se demonstrada pelos documentos anexados, que comprovam a existência da relação contratual entre as partes, bem como a aplicação de reajustes manifestamente excessivos nas mensalidades do plano de saúde.

Tais aumentos mostram-se desproporcionais e incompatíveis com os parâmetros de razoabilidade adotados pela jurisprudência e pelos princípios que regem as relações de consumo, notadamente a boa-fé objetiva e o equilíbrio contratual, previstos no Código de Defesa do Consumidor.

Assim, os elementos constantes nos autos evidenciam, em sede de cognição sumária, a plausibilidade do direito invocado pela parte autora.

O perigo da demora igualmente se faz presente, uma vez que a manutenção das cobranças em valores abusivos compromete significativamente a capacidade financeira da parte autora, expondo-a ao risco concreto de inadimplência e consequente cancelamento do plano de saúde.

Considerando tratar-se de serviço essencial, cuja continuidade é indispensável para a preservação da assistência médica, eventual interrupção da cobertura pode gerar prejuízos graves e de difícil reparação, além de esvaziar o resultado útil do processo caso a autora seja compelida a suportar os valores excessivos até o julgamento final da demanda.

Diante do exposto, requer a concessão da tutela de urgência, inaudita altera pars, para determinar que as Rés emitam o próximo boleto de cobrança da Autora recalculando a mensalidade, expurgando os reajustes por faixa etária e aplicando apenas os reajustes anuais autorizados pela ANS, o que resultará em um valor a ser apurado por cálculo contábil, mas que se estima em torno de {valor_devido_atual}.

A interrupção da assistência médica em decorrência de aumentos ilegítimos na mensalidade representaria risco iminente à sua saúde e ao seu bem-estar, configurando situação de periculum in mora que justifica, com sobras, a imperiosa necessidade de preservação do contrato nas condições devidas.

Assim, estando presentes os requisitos da probabilidade do direito e do perigo da demora, resta plenamente justificada a intervenção jurisdicional imediata.

### BLOCO: VIII | Da exibição de documentos
@condicao: sempre
@fundamentos: arts. 396 a 404 do CPC; art. 6º, VIII, do CDC; art. 400 do CPC; Tema 610/STJ

A Parte Autora não possui acesso integral aos documentos necessários à apuração da evolução das mensalidades, dos índices de reajuste aplicados e da composição das cobranças realizadas pela Ré, os quais permanecem sob guarda exclusiva da operadora.

Trata-se de evidente assimetria informacional, própria da relação de consumo, razão pela qual se impõe a exibição documental pela Ré, nos termos dos arts. 396 a 404 do CPC e do art. 6º, VIII, do CDC.

Além disso, o Superior Tribunal de Justiça, no julgamento do Tema 610, firmou entendimento de que, na vigência dos contratos de plano ou seguro de assistência à saúde, a pretensão condenatória decorrente da declaração de nulidade de cláusula de reajuste prescreve em 20 anos ou em 3 anos, conforme o regime jurídico aplicável, observada a regra de transição do art. 2.028 do Código Civil.

Assim, a apresentação do histórico de cobranças e reajustes é indispensável para permitir a correta análise da abusividade alegada, a identificação da mensalidade efetivamente devida e a apuração dos valores eventualmente cobrados a maior.

Diante disso, requer  a intimação da parte Ré para apresentar os extratos mensais de cobrança e do histórico de reajustes aplicados desde o início da vigência contratual, com indicação dos índices utilizados em cada período, sob pena de aplicação do art. 400 do CPC.

### BLOCO: IX | Da gratuidade de justiça
@condicao: sempre
@fundamentos: art. 5º, LXXIV, da CF; arts. 98 e 99 do CPC; presunção do art. 99, §3º; advogado particular não obsta (§4º); miserabilidade não é requisito. A narrativa concreta de renda e despesa é do caso, não do modelo
A Autora requer a concessão dos benefícios da gratuidade de justiça, nos termos do art. 5º, LXXIV, da Constituição Federal e dos arts. 98 e 99 do Código de Processo Civil, uma vez que, consideradas as particularidades concretas de sua situação econômico-financeira, o recolhimento das custas e despesas processuais importará comprometimento relevante dos recursos destinados à sua subsistência, à manutenção de sua saúde e ao cumprimento de obrigações familiares essenciais.

Com efeito, o art. 98 do Código de Processo Civil assegura a gratuidade à pessoa natural que não disponha de recursos suficientes para arcar com as custas, despesas processuais e honorários advocatícios. Por sua vez, o art. 99, § 3º, estabelece presunção de veracidade da alegação de insuficiência formulada por pessoa natural, sendo certo, ainda, que a contratação de advogado particular não constitui óbice à concessão do benefício, conforme expressamente dispõe o § 4º do mesmo dispositivo.

Importante registrar que a concessão do benefício não pressupõe estado de miserabilidade ou absoluta ausência de patrimônio, exigindo-se, efetivamente, a demonstração de insuficiência de recursos para suportar os encargos do processo. O Superior Tribunal de Justiça já assentou que a miserabilidade não constitui requisito legal para a concessão da gratuidade, sendo suficiente a insuficiência econômica prevista no art. 98 do CPC.

{narrativa_hipossuficiencia}

Soma-se a isso o custo do plano de saúde da própria Autora, cuja mensalidade alcançou **{valor_pago_atual}** em {competencia_atual}.

### BLOCO: X | Do processo 100% digital
@condicao: sempre
@fundamentos: padrão do escritório
A parte Autora manifesta expressa concordância com a tramitação do feito em formato 100% digital.

---

## TESE: INDIVIDUAL_COMUM
@revisar: texto redigido a partir dos fundamentos documentados, NÃO extraído de peça real do escritório. Gera peça completa, mas precisa de leitura da advogada antes do primeiro protocolo. Substituir assim que houver uma peça dessa tese.

Plano individual ou familiar contratado diretamente com a operadora. É a tese mais
simples das quatro: o plano já é regulado, o teto da ANS já se aplica por direito
próprio, e o reajuste acima dele é abusivo sem necessidade de equiparação.

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: contratação direta; reajustes acima do teto ANS
A parte Autora é titular do plano de saúde individual **{plano}**, contratado diretamente com a Ré em {inicio_contrato}.

Ao longo da contratualidade, a mensalidade sofreu majorações sucessivas, alcançando **{valor_pago_atual}** em {competencia_atual}, em percentuais superiores aos índices máximos autorizados pela Agência Nacional de Saúde Suplementar para a modalidade.

### BLOCO: II | Da aplicabilidade do Código de Defesa do Consumidor
@condicao: sempre
@fundamentos: Súmula 608/STJ — incidência direta, por não se tratar de autogestão
A relação jurídica entre as partes é de consumo, atraindo a incidência do Código de Defesa do Consumidor, conforme a Súmula 608 do Superior Tribunal de Justiça, segundo a qual se aplica o Código de Defesa do Consumidor aos contratos de plano de saúde, salvo os administrados por entidades de autogestão.

### BLOCO: III | Da abusividade do reajuste acima do teto da ANS
@condicao: sempre
@fundamentos: os planos individuais têm teto anual fixado pela ANS — o reajuste que o supera é abusivo por si, sem necessidade de equiparação. Arts. 6º, III e V, e 51 do CDC
@tabela: reajuste
Diferentemente dos contratos coletivos, os planos individuais e familiares submetem-se a teto de reajuste anual fixado pela Agência Nacional de Saúde Suplementar. O percentual autorizado é público, divulgado anualmente e vinculante para a operadora.

O reajuste aplicado em percentual superior ao teto autorizado é, por isso, abusivo em si, independentemente de qualquer discussão sobre sinistralidade ou variação de custos: a operadora não dispõe de margem para majorar a mensalidade além do limite regulatório.

A tabela a seguir confronta os percentuais efetivamente aplicados com os índices autorizados pela ANS em cada período, e demonstra o valor que seria devido:

A mensalidade atual de **{valor_pago_atual}** contrasta com o valor devido de **{valor_devido_atual}** — diferença mensal de **{diferenca_mensal}**.

### BLOCO: IV | Da abusividade do reajuste por faixa etária
@condicao: F7==SIM
@fundamentos: Temas 952 e 1016 do STJ — requisitos cumulativos
@revisar: jurisprudência sobre faixa etária a incluir
O reajuste por mudança de faixa etária somente é válido quando cumpridos, cumulativamente, a previsão contratual expressa do percentual aplicável, a observância das normas expedidas pelos órgãos reguladores e a ausência de percentuais desarrazoados que, sem base atuarial idônea, onerem excessivamente o consumidor ou discriminem o idoso.

Não tendo a Ré apresentado o percentual contratualmente previsto nem a base atuarial correspondente, impõe-se o reconhecimento da abusividade e o expurgo do reajuste da base de cálculo da mensalidade.

### BLOCO: V | Da tutela de urgência
@condicao: F6==ATIVO
@fundamentos: art. 300 do CPC
A concessão da tutela de urgência encontra fundamento no art. 300 do Código de Processo Civil. A probabilidade do direito decorre do confronto entre os percentuais aplicados e os índices públicos da ANS; o perigo da demora, do risco de inadimplência e cancelamento de serviço essencial à saúde.

Requer-se, assim, que a Ré seja determinada a recalcular a mensalidade, aplicando os índices anuais autorizados pela ANS, resultando em valor estimado de **{valor_devido_atual}**.

### BLOCO: VI | Do direito à restituição dos valores pagos a maior
@condicao: sempre
@fundamentos: art. 42, parágrafo único, do CDC ou art. 876 do CC — decisão humana; Tema 610/STJ
Reconhecida a abusividade dos reajustes, impõe-se a restituição dos valores pagos a maior. Observada a prescrição trienal do Tema 610 do Superior Tribunal de Justiça, o montante alcança **{restituicao}**, apurado na tabela anexa, acrescido de correção monetária desde cada desembolso e juros de mora a partir da citação.

### BLOCO: VII | Da gratuidade de justiça
@condicao: sempre
@fundamentos: arts. 98 e 99 do CPC; presunção do art. 99, §3º, para pessoa natural
A parte Autora requer a concessão dos benefícios da gratuidade de justiça, nos termos dos arts. 98 e 99 do Código de Processo Civil, presumindo-se verdadeira a alegação de insuficiência de recursos deduzida por pessoa natural, na forma do art. 99, §3º, do mesmo diploma.

{narrativa_hipossuficiencia}

### BLOCO: VIII | Do processo 100% digital
@condicao: sempre
@fundamentos: padrão do escritório
A parte Autora manifesta expressa concordância com a tramitação do feito em formato 100% digital.
