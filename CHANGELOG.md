# Changelog — pratica-juridica

## v1.0.4 (2026-07-28)

Calibragem da `escrita-juridica` a partir do uso real do plugin em vários modelos
(feedback do usuário: parágrafos longos/mecânicos e tom persuasivo aquém do ideal).

- **Nova regra de ouro GO-4 — parágrafos curtos e respiráveis.** Um parágrafo = um
  passo do raciocínio (2–4 períodos, ~4–7 linhas no Word); **quebrar nunca é
  resumir** (o desenvolvimento completo permanece, distribuído em mais parágrafos
  encadeados por conectivos); costuras naturais de quebra (premissa ¦ aplicação ¦
  consequência); anti-mecanicidade (variar comprimento e abertura dos parágrafos);
  teste obrigatório de revisão por tamanho de bloco. Motivo: assessores, juízes e as
  IAs dos tribunais param de ler no meio de blocos densos.
- **Nova seção "Persuasão calibrada" (registro `peça`).** Nem morno, nem
  espalhafatoso: ênfase por verbos assertivos e arquitetura do argumento (não por
  adjetivos de indignação, banidos); criticar a decisão, jamais o julgador (rechaço
  firme no conteúdo, respeitoso na forma); tomar partido nos fechos de tópico e
  pedidos (fecho que caberia em parecer neutro = falta ênfase); escala de referência
  com exemplo morno / calibrado / espalhafatoso para ancorar o tom.

## v1.0.3 (2026-07-07)

Nota de **"regra de uso"** no topo de cada skill (pipeline vs. avulso).

- Todas as skills **exceto** o orquestrador `analise-processual` ganharam um bloco no topo
  informando que a orquestração geral do plugin (fluxo de ponta a ponta) está definida em
  `analise-processual`, e instruindo o Claude a **perguntar**, quando a skill for acionada
  isoladamente, se o usuário quer **(a) seguir o pipeline do plugin** ou **(b) usar a skill
  de forma avulsa**. Evita rodar uma etapa isolada por engano quando o usuário esperava o
  fluxo completo (e vice-versa).

## v1.0.2 (2026-07-02)

Persistência **automática** do workspace no Cowork, sem configuração manual.

**Contexto:** a v1.0.1 dependia de o usuário definir `PRATICA_JURIDICA_DATA` para os
dados do processo persistirem entre sessões no Cowork — variável que o sandbox não
mantém entre sessões e que o usuário precisaria redefinir/configurar por fora. A v1.0.2
troca a dependência de variável por uma **convenção de pasta**: `dados-juridicos/`
dentro da pasta de trabalho montada (que vive no PC do usuário e persiste).

**`skills/analise-processo-pje/scripts/processo.py`**
- Novo helper `_detect_dados_juridicos()` — procura uma pasta `dados-juridicos/` já
  existente e gravável no cwd, nos ancestrais e nas pastas irmãs sob `mnt/` (padrão de
  mounts do Cowork).
- `_data_root()` — nova precedência: `PRATICA_JURIDICA_DATA` → `$CLAUDE_PLUGIN_DATA` →
  `dados-juridicos/` auto-detectada → `./outputs`.
- `workspace` — o diagnóstico (stderr) passa a tratar a pasta detectada como
  persistente (`[ok]`) e, no fallback de sessão, orienta a criar `dados-juridicos/`.
- `_writable()` — tolera mounts que permitem **criar/gravar mas bloqueiam delete**
  (comportamento real da pasta montada no Cowork): o unlink do arquivo de teste
  virou best-effort; conseguir gravar basta.
- `_detect_dados_juridicos()` robusto a `PermissionError` (stat em mounts de sistema
  como `/mnt/.virtiofs-root`); `_data_root()` só roda a detecção se nenhuma variável
  de ambiente válida existir (precedência garantida).

**SKILLs**
- `analise-processo-pje/SKILL.md` — "Ambiente e caminhos" ganha a **regra da primeira
  sessão**: havendo pasta do usuário montada e sem `dados-juridicos/`, o Claude a cria
  (`mkdir`) antes de resolver o workspace e avisa o usuário em uma linha; o script
  detecta a pasta sozinho dali em diante.
- `analise-processual/SKILL.md` — seção "Persistência" atualizada com a nova
  precedência e a regra da primeira sessão.

## v1.0.1 (2026-07-02)

Correções pós-deploy (v1.0.0), a partir do **teste no Claude Cowork** (app desktop).
Duas levas: (1) robustez de ambiente e (2) uma regra de eficiência que faltava.

### 1. Robustez de ambiente (Claude Code CLI ↔ Cowork)

**Contexto (feedback do teste):** no sandbox do Cowork, `${CLAUDE_PLUGIN_DATA}`
(`.claude/plugins/data`) é **read-only** (`nobody:nogroup`) → a persistência do
workspace quebrava; e o **Bash grava em caminho POSIX** (`/sessions/.../mnt/outputs/…`)
enquanto **Read/Edit exigem o caminho do host** (`C:\Users\…\outputs\…`).

**`skills/analise-processo-pje/scripts/processo.py`**
- **Novo comando `workspace <cnj>`** — resolve/cria um diretório **gravável** por
  precedência `PRATICA_JURIDICA_DATA → $CLAUDE_PLUGIN_DATA → ./outputs` e **imprime o
  caminho absoluto** (stdout); diagnóstico de persistência vai para stderr.
- **`extract` nunca falha por permissão** — passou a usar `_ensure_writable(--out)`:
  se o destino for read-only, cai automaticamente para `./outputs/<nome>` e avisa no stderr.
- Helpers novos: `_writable`, `_ensure_writable`, `_data_root`; adicionado `import os`.

**SKILLs — deixaram de *hardcodar* o caminho do workspace:**
- `analise-processo-pje/SKILL.md` — nova seção **"Ambiente e caminhos"** (resolver o
  workspace pelo comando; nota do `PRATICA_JURIDICA_DATA` para persistir no Cowork;
  alerta **Bash↔Read**); comando `workspace` no bloco de CLI; passo 4 (extract) passa a
  usar o caminho resolvido, com nota do auto-fallback.
- `analise-processual/SKILL.md` — seção "Persistência" aponta ao diretório **resolvido**,
  não a `${CLAUDE_PLUGIN_DATA}` fixo; persistência entre sessões exige `PRATICA_JURIDICA_DATA`.
- `pesquisa-juridica/SKILL.md` — o rastro (`pesquisas.jsonl`) vai ao `<workspace>`
  resolvido, não ao caminho fixo.

**`skills/formatacao-entrega/scripts/citar.py` — auto-descoberta de transcript multi-ambiente**
- O `@citacao-ref` (modo jurisprudência) cola a ementa **verbatim** do transcript da
  sessão. A busca só olhava `~/.claude/projects` (HOME) — **vazio no Cowork**, onde o
  transcript fica sob um mount (ex.: `.../mnt/.claude/projects`). Agora `transcripts()`
  procura em **vários locais**: env `CLAUDE_PROJECTS_DIR` → HOME → subindo a partir do
  diretório atual (inclusive sob `mnt/`). Confirmado no Cowork: colagem verbatim de
  ementa do STJ de ponta a ponta, **sem precisar passar `--transcript` na mão** (o
  override explícito continua disponível).

### 2. Regra de eficiência — "a redação vai para o arquivo, não para o chat"

**Contexto (feedback do usuário):** a regra que aplicávamos à mão no teste — *escrever a
redação direto no `.docx`/`@tag` e, no chat, dar só um resumo* — **não estava nas skills**;
pior, o checkpoint dizia "mostre a seção pronta" (o oposto, que faz colar a redação no chat
e queimar contexto de output).

- `plano-de-respostas/SKILL.md` (Passo 4, itens 2–3 e subgeração A) — o checkpoint agora:
  grava a seção no documento e, **no chat, só um RESUMO** (notas da subgeração: o que faz,
  fontes/precedentes, decisões); **nunca reproduzir a redação inteira no chat**.
- `escrita-juridica/SKILL.md` ("Contrato de saída @tag") — bloco novo em destaque:
  **"A redação vai para o ARQUIVO, não para o chat"**, com ponteiro para o Passo 4.

### Empacotamento
- `.claude-plugin/plugin.json` e `.claude-plugin/marketplace.json`: versão **1.0.0 → 1.0.1**.
- Zip de deploy gerado com Python (barras `/`, `plugin.json` na raiz, sem `__pycache__`/`teste`)
  — **não** usar `Compress-Archive` do PowerShell (grava `\` e quebra o padrão ZIP).

### Validado no Cowork
- `@citacao-ref` nos dois modos — **jurisprudência** (transcript) e **`fonte: autos`**
  (workspace) — confirmado funcionando no Cowork após a correção de auto-descoberta do
  `citar.py` (ementa do STJ colada verbatim de ponta a ponta).

### Confirmado JÁ presente (sem mudança nesta versão)
- Colacionar ementas **verbatim** via `@citacao-ref` / não redigitar
  (`escrita-juridica`, `peca-recurso`, `pesquisa-juridica`).
- Loop **uma geração por vez** + checkpoint **"Como ficou a G{N}?"** (`plano-de-respostas`).

---

## v1.0.0 (2026-07-02)
- Primeiro empacotamento para deploy. Criado `.claude-plugin/marketplace.json`
  (marketplace local `jose-plugins`, `source: "./"`). Pasta `teste/` movida para fora do
  plugin (→ `../pratica-juridica-teste`). 14 skills, hooks e scripts do pipeline validados
  no teste de ponta a ponta (REsp real).
