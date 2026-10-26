---
name: verificacao-citacoes
description: Confere cada citação de peça ou relatório contra a fonte antes de fechar (jurisprudência pelo ID do rastro, lei e doutrina, autos, números e datas). Não use para pesquisar fundamento novo (pesquisa-juridica) nem para revisar estilo.
---

# Verificação de citações

Numa peça assinada, citação errada não é bug: é risco ético e reputacional. Esta skill
não redige, audita, e roda antes de fechar todo output com citação. Fora do pipeline,
assuma N2.

| Nível | Profundidade |
|---|---|
| N1 | Referências aos autos e a lei citada. |
| N2 | Completa. |
| N3 | Completa, com subagentes; conferência de ratio por Opus nos precedentes decisivos. |
| N4 | O verificador da equipe, com esta skill como régua. |

## Princípios
- **P1 — Contra a fonte, nunca contra a memória do modelo.** Cada item se confere
  abrindo a fonte real: o registro reaberto no juris_br, `ler_fonte` no Know-How, o
  workspace do processo. "Eu me lembro que é assim" não confere nada.
- **P2 — Inventário antes de verificar.** Primeiro liste todas as asserções
  verificáveis; só então confira uma a uma. O que fica fora da lista não é conferido, e
  é aí que mora o erro.
- **P3 — Postura adversarial.** Tente refutar cada citação (existe mesmo? diz isso
  mesmo?) em vez de confirmá-la por inércia.
- **P4 — Na dúvida, não cite.** O que não se confirma na fonte é tratado como
  inexistente e sai (R3 da `pesquisa-juridica`).

## Passo 1 — Inventário
Liste cada ocorrência de: jurisprudência (acórdão, súmula, tema, enunciado); legislação
(artigo, parágrafo, inciso, alínea, citado ou transcrito); doutrina (tese atribuída a
autor ou obra); referências aos autos (tipo do documento, NUM ou id, páginas, nomes,
qualificações); números e datas (valores, prazos, marcos temporais).

## Passo 2 — Conferir cada item

### A. Jurisprudência — reabrir pelo ID do rastro
1. **Localize** no `pesquisas.jsonl` a linha que trouxe o precedente. Sem linha, a
   citação não veio de busca registrada: busque-a agora pela `pesquisa-juridica`,
   registrando; não a achando, é ⚠️ ou ❌ (P4).
2. **Reabra pelo ID** com o `*_detalhes_*` da base. Não re-rode a busca nem busque por
   número de processo: o ranking muda, a busca por número não é confiável, e o falso
   negativo levaria a remover precedente bom.
3. **Forma:** número, órgão, data e relator batem com o registro reaberto, no formato da
   ferramenta; se divergirem, corrija a peça.
4. **Texto:** compare o que entrou na peça com a ementa reaberta; o texto que cada
   `@citacao-ref` resolve sai por `citar.py … --json`. O `@citacao-ref` recusa ementa
   truncada ou com "?" no lugar da aspa de abertura (defeito conhecido do conector); se
   a geração parou nisso, reabra pelo `*_detalhes_*` e cite de novo a partir da ementa
   íntegra. `@citacao` escrito à mão: confronto literal.
5. **Ratio:** a tese atribuída é a *ratio decidendi*, não obiter nem leitura invertida.
   Leia o inteiro teor onde a base o oferece (`*_inteiro_teor`); onde não oferece, a
   ementa íntegra pelo `*_detalhes_*`, e o relatório declara o alcance ("conferido pela
   ementa íntegra; a base não oferece inteiro teor").
6. **Vigência:** não foi superado; cruze com jurisprudência recente (filtro de data).
   Súmula: enunciado transcrito ao pé da letra e não cancelado.

### B. Legislação e C. Doutrina (Know-How)
O dispositivo existe e está vigente, na redação atual; a transcrição bate literalmente; a
interpretação atribuída se sustenta. A obra e o autor existem e a passagem diz aquilo
(`ler_fonte`): nenhuma tese atribuída a quem não a sustenta.

### D. Referências aos autos (workspace)
Cada tipo de documento, NUM ou id e página bate com o workspace do processo (o caminho
que `processo.py workspace <cnj>` imprime: extratos e índice da `analise-processo-pje`).
Nomes e qualificações corretos.

### E. Números, datas e coerência
Valores, prazos e datas conferem com os autos; pedidos ↔ fundamentos ↔ fatos coerentes;
tempestividade consistente com o marco de intimação.

## Passo 3 — Relatório e gate
Um veredito por item, com evidência, salvo em `<workspace>/verificacao.md`:
- **✅ Conferido** — onde se confirmou (fonte e ID).
- **⚠️ Suspeito** — o motivo (ementa não confirma a ratio, redação divergente, possível
  superação, conferência só pela ementa onde a ratio é disputada).
- **❌ Não localizado ou divergente** — a fonte não confirma ou contradiz.

**Gate:** nenhum ⚠️ ou ❌ vai para o documento final sem resolução: corrigir pela fonte
real, remover a alegação ou levar ao José. Em peça, a entrega (`formatacao-entrega`) só
ocorre com o relatório limpo ou com os pontos decididos por ele.

## Delegação
- **Inventário:** subagente Haiku; devolve a lista do Passo 1 com a linha de cada item.
- **Reconferência por ID e de números e datas:** subagentes Sonnet, um por lote, com a
  postura do P3; recebem itens e linhas do rastro e devolvem veredito com evidência.
- **Veredito sobre a ratio:** seu, lendo o texto da fonte, nunca resumo de resumo. No N3,
  um subagente Opus confere a ratio de cada precedente decisivo e traz o trecho; o
  veredito continua seu.

Sem subagentes no ambiente, faça você mesmo, em passos separados.
