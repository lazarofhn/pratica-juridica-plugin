---
name: plano-de-respostas
description: Monta o plano de redação de peça ou relatório nos níveis N2 e N3 — mapa de peso dos argumentos, índice por resultado, quantas gerações, o que cada uma pesquisa e relê nos autos e a revisão argumentativa ao fim. Chamado pelo orquestrador e pelas skills de saída; não use no N1.
---

# Plano de respostas

O plano revela a complexidade: antes de escrever, decida o peso de cada argumento, em
quantas gerações o texto sai e como se revisa. O nível (N1 a N4) vem do
`analise-processual`; chamado fora do pipeline, assuma N2.

## Seções não são gerações
Seção é parte da estrutura; geração é um passe de escrita. Seções curtas podem sair
juntas; um fundamento denso pode pedir várias gerações (subseções 5.1, 5.2…).

## Passo 1 — Hierarquizar, depois o índice
O índice nasce do peso de cada argumento no convencimento do julgador, não da lista de
teses (`escrita-juridica`, "Antes da forma: o peso decide"). Antes de numerar:
1. **Resultados:** escreva o que o dispositivo deve dizer, um resultado por linha (o não
   conhecimento do recurso, a prescrição de todas as sanções, a nulidade do auto…).
2. **Peso:** para cada argumento, fato ou objeção, seu ou do adversário, pergunte o que
   acontece com o resultado se o julgador não o ler. Cai → **núcleo**; fica mais difícil
   → **apoio**; nada muda → **fora** (sai, ou vira uma oração dentro de outro parágrafo).
3. **Objeção já levantada** pelo adversário passa pela mesma régua: só a que pode impedir
   o resultado recebe resposta desenvolvida. O peso se mede do lado do julgador, que lê a
   peça adversária: o ponto em que o adversário apoia o resultado dele recebe ao menos
   uma oração.
4. **Tópico é o caminho até um resultado:** reúne tudo de que o julgador precisa para
   chegar àquele resultado, ainda que sejam matérias distintas. Não abra um tópico por
   tese nem uma seção por capítulo ou alínea da peça adversária.
5. **Subtópico sinaliza importância:** só para etapa de núcleo.

O que a lei exige entra sempre, e o peso decide só o espaço: requisito de
admissibilidade, impugnação especificada (CPC, art. 341), fundamento autônomo da decisão
recorrida (Súmula 283/STF).

Grave o mapa no `plano.md`, antes do índice:

| Resultado | Núcleo | Apoio | Fora (sai ou vira oração) |
|---|---|---|---|

Depois, o índice. A estrutura vem da skill de saída (o artigo do CPC do tipo de peça).
Sem estrutura própria, use o esqueleto da peça protocolada:

```
1. Endereçamento — órgão competente, confirmado pela capa e pelo andamento no workspace: o juízo da causa; nos recursos, a quo ou ad quem conforme o CPC
2. Qualificação / referência ao processo
3. Fatos — só o necessário ao núcleo, tirado do workspace
4. Admissibilidade / cabimento — quando o tipo de peça exigir
5. Fundamentos — um tópico por resultado, na ordem do peso, com o espaço previsto
6. Pedidos — claros, específicos, cada um com fundamento
```

- Regras de segmentação próprias do tipo vêm da skill de saída (ex.: admissibilidade
  individualizada no REsp/RE, em `peca-recurso`). Não junte endereçamento com fatos nem
  admissibilidade com mérito.
- Os fatos vêm do workspace (`analise-processo-pje`), não de releitura do PDF.
- Havendo `estrategia.md` no workspace (relatório estratégico feito antes da peça),
  parta das decisões dele.

## Passo 2 — Quantas gerações
Segmente quando houver dois ou mais tópicos de núcleo, tutela de urgência mais mérito, ou
texto projetado acima de ~10 páginas. Sem gatilho, uma geração — o plano continua
explícito, com um item. Para cada geração anote: tema, perfil de pesquisa, documentos dos
autos a reler e registro de escrita.

## Passo 3 — Aprovação conforme o nível
- **N2:** mostre o mapa de peso e o plano num bloco curto e siga.
- **N3:** apresente o mapa de peso e o plano e espere o ok antes de redigir, junto com as
  decisões já tomadas com o conselheiro Fable (cabimento, eixo, ordem das teses).
- **Revisão tópico a tópico** só se o José pedir: aí, ao fim de cada geração, mostre as
  notas da geração e espere.

Salve o plano no workspace do processo (o caminho de `processo.py workspace <cnj>`) como
`plano.md`, com as decisões tomadas. Serve para retomar o trabalho depois.

## Passo 4 — Uma geração por vez
> ⚠️ **Erro fatal:** escrever todas as gerações num único output. Isso derrota a
> segmentação e produz peça rasa, mesmo com contexto longo. Cada geração é um ciclo
> próprio, em passo separado.

Ciclo de cada geração:
1. **Pesquisa focada** no tema (`pesquisa-juridica`); quando a seção invoca lei, leia o
   dispositivo e a doutrina antes de afirmar.
2. **Volta aos autos:** consulta pontual no workspace (`analise-processo-pje`: `find`,
   `extract`) para ancorar a seção nos fatos concretos — o que a decisão disse, o que a
   parte alegou.
3. **Redação** só daquela seção (`escrita-juridica`), direto no arquivo (`@tag` →
   `.docx` por `formatacao-entrega`), no espaço que o mapa de peso previu. No chat, só as
   notas da geração: o que a seção faz, fontes usadas, decisões. Nunca recole a redação
   no chat.

Seção densa — lei e doutrina mais jurisprudência de peso — sai em dois passes seguidos,
sem parar: **A**, fundação em lei e doutrina; **B**, jurisprudência que confirma ou
corrige o que A afirmou.

### N2 — você redige
Gerações em sequência, cada uma em passo separado, sem perguntar "como ficou".

### N3 — um subagente por tópico prepara, você redige
Uma só mão escreve a peça: é ela que mede o peso e liga os tópicos. Por isso, no N3, cada
tópico vai a um subagente Opus dedicado, com contexto limpo, que **prepara o tópico e não
o redige**. Briefing: objetivo da peça, eixo e decisões do `plano.md`; o tópico e o
resultado a que ele leva; caminhos dos extratos dos autos no workspace (o agente lê os
`.md`, não o PDF); rodar a `pesquisa-juridica` para o tema e gravar o rastro. Ele devolve
um dossiê em `<workspace>/redacao/D{N}-<tema>.md`:
- os fatos do tópico, cada um com documento, id e página, e a transcrição do trecho
  decisivo;
- os precedentes, com ID, trecho e a ratio em uma linha;
- o que a peça adversária e a decisão disseram sobre o tópico, com página;
- as lacunas: o que o tópico precisa e os autos ou a pesquisa não deram.

Sem texto de peça e sem juízo de peso. Tópicos independentes rodam em paralelo. Com os
dossiês, confira o mapa de peso e redija a peça inteira, geração a geração, como no N2.

## Passo 5 — Costura e revisão argumentativa
1. **Costura**, sua: transições, termos uniformes, nenhuma contradição entre tópicos,
   coerência fatos → fundamentos → pedidos, cada pedido com fundamento.
2. **Revisão argumentativa** — registro `peça`, do N2 em diante (o N1 não tem):
   - **`pratica-juridica:sensibilidade-argumentativa`** (Opus) reorganiza a peça pelo
     peso, sem argumento, fato, citação ou pedido novos, e grava
     `<peça>-sensibilidade.md` ao lado da original. Confira antes de adotar: nenhum fato,
     citação, folha ou pedido perdido ou alterado, nenhuma frase de tese com o sentido
     mudado. Os cortes que ele lista são seus para vetar.
   - **`pratica-juridica:moderador-final`** lê a versão adotada como o julgador e devolve
     a decisão simulada e até cinco ajustes. No N2, abra-o com `model: opus`; no N3 e no
     N4, com o modelo dele (Fable). Aplique o que procede: a decisão é sua.
   - Briefing dos dois: caminho da peça, registro, resultados pedidos, quem julga, o
     `plano.md` e os caminhos dos extratos da peça adversária e da decisão atacada, que
     são o que estará na mesa do julgador.
   - Uma rodada de cada. O moderador volta uma segunda vez só se indeferir o pedido
     principal por defeito que a peça pode corrigir.
   - Se o tipo de agente não existir na sessão, abra um subagente comum com o modelo
     indicado e, como instrução, o corpo do arquivo do agente
     (`${CLAUDE_PLUGIN_ROOT}/agents/<nome>.md`).
3. **Radar e citações:** `lint_peca.py` na versão final e `verificacao-citacoes`.

## Não confundir
- O plano de leitura (`analise-processo-pje`) decide o que extrair dos autos; este
  decide como escrever.
- O estudo de viabilidade do recurso (`peca-recurso`) é prévio e pode mudar a natureza
  da peça; o passe B acontece dentro de uma geração, com a arquitetura já decidida.
- A revisão argumentativa mexe na construção (peso, ordem, espaço); o radar e as
  varreduras da `escrita-juridica`, na forma; a `verificacao-citacoes`, nas fontes.
