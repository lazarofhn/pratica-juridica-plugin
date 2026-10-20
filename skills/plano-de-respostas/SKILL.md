---
name: plano-de-respostas
description: Monta o plano de redação de peça ou relatório nos níveis N2 e N3 — índice numerado, quantas gerações, o que cada uma pesquisa e relê nos autos, e quem redige (você ou um subagente por tópico). Chamado pelo orquestrador e pelas skills de saída; não use no N1.
---

# Plano de respostas

O plano revela a complexidade: antes de escrever, decida em quantas gerações o texto
sai e quem escreve cada uma. O nível (N1 a N4) vem do `analise-processual`; chamado
fora do pipeline, assuma N2.

## Seções não são gerações
Seção é parte da estrutura; geração é um passe de escrita. Seções curtas podem sair
juntas; um fundamento denso pode pedir várias gerações (subseções 5.1, 5.2…).

## Passo 1 — Índice numerado
A estrutura vem da skill de saída (o artigo do CPC do tipo de peça). Sem estrutura
própria, use o esqueleto da peça protocolada:

```
1. Endereçamento — órgão competente, confirmado pela capa e pelo andamento no workspace: o juízo da causa; nos recursos, a quo ou ad quem conforme o CPC
2. Qualificação / referência ao processo
3. Fatos — só o necessário à tese, tirado do workspace
4. Admissibilidade / cabimento — quando o tipo de peça exigir
5. Fundamentos — um por tese ou causa de pedir
6. Pedidos — claros, específicos, cada um com fundamento
```

- Regras de segmentação próprias do tipo vêm da skill de saída (ex.: admissibilidade
  individualizada no REsp/RE, em `peca-recurso`). Não junte endereçamento com fatos nem
  admissibilidade com mérito.
- Os fatos vêm do workspace (`analise-processo-pje`), não de releitura do PDF.
- Havendo `estrategia.md` no workspace (relatório estratégico feito antes da peça),
  parta das decisões dele.

## Passo 2 — Quantas gerações
Segmente quando houver dois ou mais fundamentos de mérito, tutela de urgência mais
mérito, ou texto projetado acima de ~10 páginas. Sem gatilho, uma geração — o plano
continua explícito, com um item. Para cada geração anote: tema, perfil de pesquisa,
documentos dos autos a reler, registro de escrita e quem redige.

## Passo 3 — Aprovação conforme o nível
- **N2:** mostre o plano num bloco curto e siga.
- **N3:** apresente o plano e espere o ok antes de redigir, junto com as decisões já
  tomadas com o conselheiro Fable (cabimento, eixo, ordem das teses).
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
   `.docx` por `formatacao-entrega`). No chat, só as notas da geração: o que a seção
   faz, fontes usadas, decisões. Nunca recole a redação no chat.

Seção densa — lei e doutrina mais jurisprudência de peso — sai em dois passes seguidos,
sem parar: **A**, fundação em lei e doutrina; **B**, jurisprudência que confirma ou
corrige o que A afirmou.

### N2 — você redige
Gerações em sequência, cada uma em passo separado, sem perguntar "como ficou".

### N3 — um subagente por tópico
Cada geração vai para um subagente Opus dedicado, com contexto limpo. Briefing:
- objetivo da peça, eixo e decisões já tomadas (do `plano.md`);
- o tópico: função na peça, tese a sustentar, o que não repetir dos outros tópicos;
- caminhos dos extratos dos autos no workspace — o agente lê os `.md`, não o PDF;
- pesquisa: rodar `pesquisa-juridica` para o tema e gravar o rastro;
- regras: `escrita-juridica`, registro peça; escrever a seção em
  `<workspace>/redacao/G{N}-<tema>.md`; devolver só as notas (o que fez, fontes,
  pendências).

Tópicos independentes podem rodar em paralelo; os que dependem de outro (ex.: mérito que
pressupõe o enquadramento do cabimento) esperam. Ao receber, **leia cada seção
inteira** — as notas do agente não bastam — antes de costurar.

## Passo 5 — Costura
Uma passada final, sua: transições, termos uniformes, nenhuma contradição entre
tópicos, coerência fatos → fundamentos → pedidos, cada pedido com fundamento. Depois,
`verificacao-citacoes`.

## Não confundir
- O plano de leitura (`analise-processo-pje`) decide o que extrair dos autos; este
  decide como escrever.
- O estudo de viabilidade do recurso (`peca-recurso`) é prévio e pode mudar a natureza
  da peça; o passe B acontece dentro de uma geração, com a arquitetura já decidida.
