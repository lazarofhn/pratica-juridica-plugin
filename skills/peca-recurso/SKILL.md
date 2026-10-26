---
name: peca-recurso
description: Redige recurso (apelação, agravo, embargos de declaração, recurso ordinário, REsp, RE) ou contrarrazões a partir dos autos, com estudo de viabilidade no REsp/RE. Não use para contestação, réplica, impugnação ou embargos à execução, que são da peca-especifica.
---

# Peça: recurso e contrarrazões

Nível típico: N3 no REsp/RE e na apelação ou nas contrarrazões com várias teses; N2 nos
embargos de declaração simples. Chamada fora do pipeline, assuma N3 no REsp/RE (recurso
excepcional sobe um nível) e N2 nos demais; declare em uma linha e o José ajusta.

## 1. Precondições
- Workspace (o caminho que `processo.py workspace <cnj>` imprime) com a decisão
  recorrida extraída e, havendo, o acórdão dos embargos; nas contrarrazões, também o
  recurso adverso. Intimação e prazo são dados dos autos: anote-os no `plano.md`.
- Plano pelo `plano-de-respostas` antes de redigir, com a segmentação do item 4.

## 2. Identificar o recurso
- Indicado, ou um só cabível (sentença → apelação): siga direto.
- Omitido, com mais de um plausível (ex.: acórdão omisso, embargos de declaração ou REsp
  direto): informe o cabimento que vê, com o fundamento, e confirme antes de redigir.
- Dúvida do próprio José: resolva com pesquisa processual antes de escrever.

## 3. Viabilidade — obrigatória no REsp/RE
Antes da estrutura, estude como o STJ e o STF vêm decidindo o tema (`pesquisa-juridica`),
cruzando com as bases do conector aplicáveis ao tribunal de origem e à matéria (quais
existem e como filtrá-las: a descrição viva da ferramenta e o `*_listar_filtros`). O modo
como a Corte decide define a natureza da peça, não só o conteúdo.
- **Óbice de conhecimento** (Súmula 7/STJ, Súmula 279/STF: reexame de prova): o mérito
  não pode ser o carro-chefe. Migre o eixo para o que é conhecível: negativa de prestação
  jurisdicional (CPC, art. 1.022), questão de direito pura, divergência.
- Identifique de saída o precedente qualificado que rege o tema e os óbices sumulares.
- **O pedido segue o eixo.** Com eixo no art. 1.022, o pedido é anulatório, de retorno à
  origem; pedir o provimento direto do mérito reintroduz o óbice contornado.
- **Não misture as vias.** No REsp, argumento constitucional (isonomia, capacidade
  contributiva, art. 150 da CF) não vira tópico autônomo: é matéria de RE e enfraquece o
  especial. Dilua-o como reforço das teses infraconstitucionais (ex.: a solução de
  consulta que reconhece o crédito mostra que a omissão era decisiva, sem abrir capítulo
  de isonomia). No RE, o espelho: não trave tese infraconstitucional como constitucional.
- **N3:** o eixo, e o cabimento quando duvidoso, passam pelo conselheiro Fable (advisor,
  se ligado; senão, subagente Fable com dossiê); você decide e registra no `plano.md`.
- Estudo feito antes, como estratégia no `relatorio`: na redação, reabra os precedentes
  pela fonte, pelo rastro da `pesquisa-juridica`, e não pela memória da conversa.

## 4. Estrutura e segmentação
- A estrutura é a do artigo do CPC que regula o recurso, lido na fonte e não de memória;
  sem regra própria, o esqueleto do `plano-de-respostas`.
- Admissibilidade com ênfase média-alta por padrão: tempestividade, cabimento, preparo.
- **Colacione a decisão recorrida** (praxe): ementa e trechos cruciais do julgado e,
  havendo, do acórdão dos embargos, por `@citacao-ref fonte: autos`, verbatim do
  workspace, sem redigitar. Na negativa de prestação jurisdicional, a ementa genérica dos
  embargos costuma ser a própria prova da omissão.
- Coerência decisão recorrida → fundamentos → pedidos: todo fundamento autônomo da
  decisão que sustenta o resultado precisa ser atacado.

> **REGRA DE OURO — RE e REsp.** A falta de fundamentação específica de um requisito de
> admissibilidade leva ao não conhecimento (ex.: RE sem o tópico de repercussão geral).
> Salvo comando em contrário, o plano dedica **uma geração a cada requisito**: o
> cabimento sempre em tópico isolado; correlatos (tempestividade, prequestionamento)
> podem compartilhar. Admissibilidade nunca se mistura com a síntese fática nem com o
> mérito, mesmo quando o eixo é processual (art. 1.022).

## 5. Contrarrazões
Mesmo método, com a admissibilidade invertida; a estrutura vem do artigo do CPC que prevê
a resposta àquele recurso.
- **Não conhecimento primeiro.** Confira cada requisito do recurso adverso
  (tempestividade, cabimento, preparo, regularidade formal, impugnação específica dos
  fundamentos da decisão) e os óbices da Corte; no REsp/RE, o estudo do item 3, feito do
  lado de quem responde, aponta-os (reexame de prova, falta de prequestionamento,
  fundamento não atacado). Alegue o óbice que os autos sustentam, não a lista inteira.
- **Responda pelo peso, não pelo índice do recurso.** Todo fundamento do recurso que,
  acolhido, mudaria o resultado recebe resposta, no espaço que o peso pede; o resto, uma
  oração ou nada (`plano-de-respostas`, Passo 1). Organize por resultado defendido, não
  capítulo por capítulo do recorrente, e sustente a decisão recorrida com os fundamentos
  dela.
- **Pedido:** não conhecimento; subsidiariamente, desprovimento.
- Segmentação: uma geração para o não conhecimento e uma por tópico de núcleo.

## 6. Pesquisa e verificação
- Pesquisa em duas linhas: admissibilidade (cabimento e requisitos do recurso concreto) e
  mérito (uma por fundamento). Escrita (registro `peça`) e entrega (`.docx`): o padrão.
- `verificacao-citacoes` obrigatória; no REsp/RE, confira também que cada requisito tem
  tópico próprio e fundamentado e, nas contrarrazões, que cada óbice tem base nos autos.
