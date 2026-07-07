---
name: analise-processo-pje
description: >-
  Analisa processos judiciais GRANDES em PDF (cópia integral do PJe, centenas/milhares
  de páginas) sem carregar tudo no contexto. Use quando o usuário pedir para resumir um
  processo, gerar relatório completo, redigir uma peça (apelação, contrarrazões,
  embargos, manifestação), analisar o valor/pedidos da causa, encontrar ou ler
  documentos específicos, ou rastrear o andamento. Funciona com PDFs que têm índice de
  documentos em bookmarks (padrão do PJe). Faz retrieval agêntico guiado pelo índice:
  lê o mapa, rankeia o que importa, extrai só os documentos necessários.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Análise de Processos PJe (grandes) — camada C

Processos do PJe em PDF têm **bookmarks** que mapeiam cada documento (tipo, evento/NUM,
data, página). Isso permite **extração sob demanda**: nunca carregamos o PDF inteiro
(que pode ter 3M+ tokens) — lemos o índice, decidimos o que importa, e extraímos só isso.

## Encaixe no plugin (camada C)
- **Chamada pelo orquestrador** (`analise-processual`) COM o **objetivo** já definido.
  O objetivo muda o que é "estratégico": para um recurso importam sentença/acórdão e
  razões; para uma contestação, a inicial e o que a instrui.
- **Grava no workspace persistente** do processo, não em pasta temporária. **Não
  hardcode** o caminho: rode `processo.py workspace <numero-cnj>` e use o diretório
  **gravável** que ele imprime (ver "Ambiente e caminhos"). Assim outra tarefa depois
  (recurso hoje, relatório semana que vem) reaproveita as peças já convertidas em `.md`.
- **Não confundir dois "planos":** o *plano de leitura* daqui (quais documentos
  extrair) é diferente do `plano-de-respostas` (como segmentar a escrita do output).
  Este roda antes, na análise; aquele roda depois, antes de escrever.
- **Uso recorrente, não só inicial:** a análise NÃO se esgota na leitura de contexto
  do começo do pipeline. O workspace persistente é **reconsultado durante as
  gerações** da peça, via `find`/`extract` sob demanda, para **ancorar cada seção aos
  fatos concretos** (ex.: reabrir a petição de embargos para listar as questões
  suscitadas; reler a decisão recorrida para citar o que ela de fato disse). Espere
  voltar aos autos a cada geração, não apenas uma vez.

## Motor (CLI)

Script: `${CLAUDE_PLUGIN_ROOT}/skills/analise-processo-pje/scripts/processo.py`.
Requer `pypdfium2` (wheel leve, sem PyTorch). Se faltar: `pip install pypdfium2`.
Nos exemplos abaixo, `processo.py` = esse caminho completo.

```
python processo.py index   <pdf>                     # mapa dos documentos (markdown)
python processo.py index   <pdf> --json              # idem em JSON
python processo.py peek    <pdf> --docs 10,22 --chars 300   # substância inicial p/ ranking
python processo.py extract <pdf> --docs 10,22 --out <dir>   # markdown completo (rodapé limpo)
python processo.py find    <pdf> --id 240714892      # resolve citação "id N" -> documento
python processo.py workspace <numero-cnj>            # cria/resolve o diretório GRAVÁVEL do processo e imprime o caminho
```

`index` marca `peça? sim/—`: peças jurídicas (decisão, petição, manifestação, parecer,
sentença, embargos, contrarrazões, despacho, certidão...) vs anexos/documentos
(registrados, mas não transformados por padrão).

## Ambiente e caminhos (workspace gravável + Bash↔Read)
O plugin roda tanto no **Claude Code (CLI)** quanto no **Cowork (app desktop)**, que têm
sistemas de arquivos diferentes. Três regras evitam os atritos conhecidos:

1. **Nunca hardcode o diretório de dados.** Rode `processo.py workspace <numero-cnj>` e
   use o caminho que ele **imprime** (stdout). Ele escolhe, nessa ordem, um diretório
   **gravável**: `$PRATICA_JURIDICA_DATA` (config explícita do usuário) →
   `$CLAUDE_PLUGIN_DATA` (Claude Code) → pasta **`dados-juridicos/`** auto-detectada
   (ver regra 2) → `./outputs` (sessão). No Cowork o `.claude/plugins/data` costuma ser
   **read-only** (`nobody:nogroup`); sem `dados-juridicos/`, cai em `./outputs` —
   funciona, mas **não persiste entre sessões**.
2. **Persistência automática no Cowork — a regra da primeira sessão.** Antes de rodar o
   `workspace`, verifique se o usuário montou uma pasta de trabalho na sessão (ela
   aparece no seu contexto como "pasta selecionada"; no sandbox fica em
   `/sessions/<id>/mnt/<pasta>/`). Se houver pasta montada e ainda **não existir**
   `<pasta-montada>/dados-juridicos/`, **crie-a** (`mkdir`) — uma vez criada, o
   `processo.py` a **detecta sozinho** em todas as sessões futuras em que essa pasta
   estiver montada, e o `workspace` passa a resolver para dentro dela (persistente no
   PC do usuário). Avise o usuário em uma linha: *"criei `dados-juridicos/` na sua
   pasta para os dados do processo persistirem entre sessões"*. Se **não** houver pasta
   montada, siga com `./outputs` e avise que os dados valem só para a sessão (sugira
   montar uma pasta ou definir `PRATICA_JURIDICA_DATA`). **Não crie** a pasta se o
   usuário já tiver indicado outro local via `PRATICA_JURIDICA_DATA`.
3. **Bash e Read/Edit podem exigir caminhos diferentes.** Em alguns ambientes (Cowork), o
   script grava num caminho POSIX do sandbox (`/sessions/.../mnt/outputs/...`) enquanto as
   ferramentas Read/Edit exigem o caminho do host (`C:\Users\...\outputs\...`). Logo: **não
   presuma que o caminho impresso pelo script funciona direto no Read.** Depois de extrair,
   liste o diretório e use a forma de caminho que a ferramenta de leitura aceita naquele
   ambiente (o caminho impresso é a referência; traduza se o Read falhar).

## Fluxo de trabalho

1. **Ler o índice** (barato): `index <pdf>`. ~400 documentos cabem em poucos K tokens.
2. **Rankear (2 estágios)** conforme o pedido do usuário:
   - *Estágio 1*: filtre por tipo + data + tamanho, direto do índice (de graça).
   - *Estágio 2*: para os ~15-30 candidatos, rode `peek` e desempate pela substância.
3. **Mostrar o plano de leitura ao usuário** antes de extrair em massa:
   "Vou analisar estes N documentos: ...". Deixe-o adicionar/remover (salvaguarda
   contra erro de ranking).
4. **Extrair** os alvos para o workspace do processo: primeiro resolva o diretório com
   `workspace <numero-cnj>` (imprime um caminho gravável) e passe-o em
   `extract --docs ... --out <esse-caminho>`. O comando informa o custo estimado em
   tokens de cada arquivo. (Se um `--out` read-only for passado assim mesmo, o `extract`
   **auto-cai** para `./outputs/...` e avisa no stderr — nunca falha por permissão.)
5. **Ler verbatim** os markdowns extraídos e produzir a resposta.
6. **Seguir citações e iterar**: peças citam outras por `id NNNNN`. Ao encontrar uma
   citação relevante, resolva com `find --id NNNNN` e extraia o documento citado.
   Repita até ter o necessário.

## Orquestração de modelos (importante)

Quando rodando em Opus, **delegue a triagem a um subagente Sonnet** (Agent tool,
`model: sonnet`) e mantenha o raciocínio jurídico no Opus:

- **Subagente Sonnet (triagem)**: recebe o caminho do PDF + o pedido do usuário.
  Ele mesmo roda `index` e `peek` e devolve **só a shortlist rankeada**
  (seq, tipo, páginas, 1 linha de justificativa cada). Assim os snippets de `peek`
  **nunca entram no contexto do Opus** — é o maior ganho (higiene de contexto, não só custo).
- **Opus (principal)**: a partir da shortlist, roda `extract` e **lê o texto verbatim**
  para a redação/análise.

**A linha que não se cruza:** delegue TRIAGEM, não a LEITURA PROFUNDA. Para redigir uma
peça ou analisar um argumento específico, o Opus deve ler o texto literal — resumo de
subagente perde nuance que importa juridicamente.

Exceção por tipo de tarefa:

| Pedido | Orquestração |
|---|---|
| Apelação / contrarrazões / analisar argumento | Sonnet triagem → **Opus lê verbatim** as peças-chave |
| Relatório completo do processo | **Map-reduce**: vários Sonnet resumem peças em paralelo → Opus sintetiza |
| Encontrar/ler um documento específico | Direto: `find`/`index` → `extract` → ler |

## Estratégia por tipo de pedido

- **Relatório completo**: varra TODAS as peças (`is_peca = sim`). Em geral são poucas
  páginas no total mesmo num processo gigante; processe em lotes (map-reduce).
- **Redigir peça** (apelação etc.): foco na decisão/sentença recorrida, nas peças da
  parte, e nas citações que elas fazem. Retrieval rankeado + seguir citações.
- **Análise de valor**: priorize petição inicial, planos, laudos, decisões sobre
  crédito/tutela; rode `peek` para achar onde estão os números.

## Anexos e escaneados

- Por padrão só transformamos peças. Anexos ("Outros Documentos", "Anexo",
  "Procuração") ficam no índice como referência ("p. X-Y no PDF"); só extraia se o
  pedido exigir.
- Se um documento vier com páginas-imagem sem texto (raro — o PJe costuma aplicar OCR),
  o `extract` traz pouco/nada. Nesse caso use OCR local (Tesseract) sob demanda:
  veja `scripts/processo.py` (comando `ocr` é o ponto de extensão) e
  `pip install pytesseract` + binário do Tesseract. Marque o resultado como
  `fonte: ocr` (pode ter erros).

## Boas práticas

- **Nunca** despeje o PDF inteiro no contexto. Sempre via `index` → `extract` seletivo.
- Cite sempre a procedência ao responder: tipo do documento, evento (NUM) e páginas.
- Ao terminar, ofereça extrair documentos adicionais que ficaram fora do escopo inicial.
- Cuidado com documentos partidos (vários "Anexo"/"Outros Documentos" consecutivos com
  NUMs sequenciais): podem ser um único documento lógico dividido por limite de upload.
