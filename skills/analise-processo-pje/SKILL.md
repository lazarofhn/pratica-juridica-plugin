---
name: analise-processo-pje
description: Lê autos do PJe em PDF sem carregar o processo inteiro — índice de documentos, busca textual, extração seletiva em .md no workspace e imagem de página escaneada. Não use para redigir a peça (skills de saída) nem para PDF que não sejam autos.
---

# Leitura dos autos (PJe)

O PDF do PJe traz bookmarks que mapeiam cada documento (tipo, nome, evento, data,
páginas). O script lê o mapa, localiza o que importa e extrai só isso para o workspace
do processo. Nunca carregue o PDF inteiro no contexto.

Chamada pelo `analise-processual` com objetivo e nível definidos (fora do pipeline,
N2). O objetivo decide o que é estratégico: no recurso, a decisão recorrida e as razões;
na contestação, a inicial e os documentos. O workspace é reconsultado a cada geração da
peça, não só no começo. Plano de leitura (o que extrair) não é `plano-de-respostas`.

| Nível | Leitura |
|---|---|
| N1 | consulta pontual: `find`, `grep` ou `peek`; extrai só o documento da resposta |
| N2 | índice → shortlist → `extract` dos documentos da tese; plano de leitura em uma linha, sem parar |
| N3 | leitura ampla com triagem por subagente; mostre o plano de leitura e siga (a aprovação do N3 é a do plano de respostas) |
| N4 | a leitura que a equipe (`equipe-juridica`) definir |

## Motor (CLI)
Script: `${CLAUDE_PLUGIN_ROOT}/skills/analise-processo-pje/scripts/processo.py`, abaixo
`processo.py`. Requer `pypdfium2` (`pip install pypdfium2`); Pillow é opcional (render em
cores). A saída sai em UTF-8 em qualquer console.

```
processo.py workspace <cnj>                  # pasta do processo (imprime o caminho)
processo.py index   <pdf> [--json]           # seq, tipo, nome, evento, data, págs, s/ texto, peça?
processo.py peek    <pdf> --docs 10,22 [--chars 300]   # começo de cada documento, sem o timbre
processo.py grep    <pdf> "<termo>" [--docs 10,22] [--regex] [--exato] [--max 40]
processo.py find    <pdf> --id 240714892     # evento/id → documento (--pattern = grep)
processo.py refs    <pdf> --docs 27          # "ID N - Pág. X" citados no documento → doc. e página
processo.py extract <pdf> --docs 10,22 [--out <workspace>]     # um .md limpo por documento
processo.py extract <pdf> --pages 120-135 [--out <workspace>]  # fatia de páginas
processo.py sem-texto <pdf> [--doc 4] [--json]                # páginas sem texto extraível
processo.py render  <pdf> --pages 7,12 [--out <pasta>]         # PNG das páginas
```

- `index`: o nome vem do bookmark; no TRF-5, que só traz o tipo, do documento "Índice"
  dos autos. `peça?`: **sim** (petição, decisão, parecer) · **?** (petição genérica ou
  volume digitalizado — o de processo migrado reúne as peças da fase física: localize por
  `grep` e extraia por `--pages`) · **—** (anexo, expediente).
- `grep` ignora maiúsculas e acentos (`--exato` respeita) e devolve página, documento e
  trecho: ache o ponto antes de extrair.
- `extract` remove rodapé de assinatura e cabeçalho de página do PJe. Sem `--out`, grava
  no workspace do processo pelo CNJ do PDF. Acima de ~150 mil tokens estimados, recusa
  (exit 3) e pede `--confirmar`; antes disso, prefira `grep` e `--pages`.

## Fluxo
1. `workspace <cnj>` e reaproveite o que já está extraído (`doc_NNN_*.md`).
2. `index` (barato: ~400 documentos cabem em poucos mil tokens; a 1ª chamada mede as
   páginas sem texto e leva segundos em PDF grande, as seguintes usam cache).
3. Shortlist pelo índice (tipo, data, tamanho, `peça?`); desempate por `peek` nos
   candidatos; ache pontos específicos com `grep`. Vários "Anexo" seguidos, com NUMs
   sequenciais, podem ser um documento só, partido pelo limite de upload.
4. `extract` para o workspace e leia os `.md` verbatim.
5. Siga as citações: `refs --docs N` resolve os "ID N - Pág. X" da peça para o documento
   e a página do PDF; extraia o citado (ou só a página, com `--pages`). Repita até ter o
   necessário.
6. Cite a procedência: tipo, evento (NUM) e páginas. Ao terminar, ofereça extrair o que
   ficou fora do escopo.

Por pedido: relatório completo varre as peças (`peça?` sim e ?), em lotes; peça foca a
decisão atacada, as peças da parte e o que citam; valor da causa parte da inicial, dos
laudos e das decisões sobre crédito, com `grep` pelos números.

## Triagem delegada (subagentes nativos)
- **Haiku**: localizar documentos no índice — roda `index`, `find` e `grep` e devolve
  seq, evento e páginas.
- **Sonnet**: triar índice grande (centenas de documentos) — roda `index` e `peek` e
  devolve só a shortlist rankeada (seq, tipo, págs., uma linha de motivo). Os snippets
  ficam fora do contexto principal. No relatório completo, resume lotes de peças.
- A leitura profunda não se delega: para redigir ou analisar argumento, leia o texto
  literal extraído; resumo de subagente perde a nuance que importa. Sem subagentes no
  ambiente, faça você mesmo, em passos separados.

## Sem bookmarks
`index` avisa no stderr e no topo da tabela. Com o rodapé "Num. N - Pág. M" do PJe, os
documentos são remontados por ele (sem data; o tipo vem do cabeçalho de página, quando
há): confira com `peek`. Sem rodapé, modo sem índice: faixas de 50 páginas; localize com
`grep` e leia com `extract --pages`.

## Páginas sem texto
Página com menos de 80 caracteres úteis (sem rodapé e cabeçalho do PJe) e imagens
cobrindo ao menos 10% dela: escaneada sem OCR. O plugin não faz OCR.
- `index` conta essas páginas por documento (coluna `s/ texto`); `sem-texto` as lista
  (`--json` para uso por programa).
- `extract` marca a página (`<!-- pág. N · sem texto extraível (imagem) -->`) e preenche
  no front matter `fonte` (texto-nativo | ocr | misto | sem-texto), `paginas_sem_texto`
  e `paginas_ocr`. **ocr** = texto que a digitalização já pôs sobre a imagem: pode ter
  erro; confira na imagem antes de citar literalmente.
- Página decisiva sem texto: `render --pages N` e leia o PNG com a ferramenta de leitura
  de arquivo (ela mostra a imagem). Transcrição de imagem é marcada como tal e vai à
  `verificacao-citacoes`.

### Busca nas páginas sem texto (conector busca-autos)
Com o conector busca-autos instalado, dá para achar documentos nas páginas sem texto pela
imagem, que o `grep` e o título do índice não alcançam (no teste com dois processos do
TRF-5: 0 de 20 sem ele, 16 de 20 com ele). Regra de uso:
1. **Decida pelo `index`.** Processo digital ou com OCR: não indexe; título e `grep`
   bastam. Parte relevante sem texto (volumes de autos físicos, anexos digitalizados) e o
   que se procura pode estar nela: use o busca-autos.
2. **Quando:** no N3/N4, dispare a indexação logo no início, em segundo plano, e siga com
   o resto; no N1/N2, só se o documento procurado for escaneado. Processo já indexado
   (`status_indice`): busque direto.
3. **Só a parte que é imagem vai ao Colab:** as páginas sem texto e as que são quase toda
   imagem. Digitais e com OCR ficam no índice local. Modo rápido por padrão; o fino, só
   quando o José pedir; GPU A100 quando houver pressa. Leva de poucos minutos a ~40 min,
   conforme o tamanho da parte escaneada.
4. **Buscar:** `buscar_paginas` filtrando as páginas sem texto (`classe='imagem_sem_texto'`)
   e ler o achado com `ler_pagina`, que devolve a imagem. Transcrição de imagem segue a
   regra do item acima.
5. **Peça longa datilografada dentro de volume** (inicial, sentença, decisão, parecer): a
   busca por imagem falha. Use as folhas citadas em outras peças e o índice de volumes do
   PJe e leia as faixas como imagem (`ler_pagina` ou `render`), com leitores Haiku se
   forem muitas páginas.

Nomes e parâmetros exatos: a descrição viva das ferramentas do conector.

## Workspace
`workspace <cnj>` resolve a pasta, nesta ordem: `PRATICA_JURIDICA_DATA` →
`CLAUDE_PLUGIN_DATA` → `dados-juridicos/` na pasta de trabalho (atual, ancestrais ou
mounts do Cowork) → `./outputs` da sessão. Pasta antiga no formato `<raiz>/<cnj>` é
reaproveitada. Caindo em pasta temporária, o script avisa alto no stderr: diga ao José em
uma linha e recomende `PRATICA_JURIDICA_DATA`. Use sempre o caminho impresso; nunca o
monte à mão.

> **Cowork.** Havendo pasta de trabalho montada sem `dados-juridicos/`, crie-a uma vez e
> avise o José; o script a detecta nas sessões seguintes. Bash e Read podem pedir formas
> diferentes do mesmo caminho: se o Read recusar o impresso, liste a pasta e use a forma
> que ele aceita.
