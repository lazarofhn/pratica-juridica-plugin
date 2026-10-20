# Changelog — pratica-juridica

## v1.3.1 (2026-10-20)

Ligação entre parágrafos. O José pegou o texto robótico em peça pronta, com e sem a
`escrita-juridica`: a maioria dos parágrafos abria com sujeito nominal seco ("O MPF", "O
acórdão", "A sentença") e faltava fluidez entre parágrafos e capítulos. Na manifestação e
no memorial medidos, 73% e 67% dos parágrafos abriam assim, e o radar dava média de 58
palavras, abaixo da faixa; a peça da equipe de 16/10 tinha 49%, com média de 43. Duas
regras empurravam para isso: "parágrafos curtos" lido como frase solta e o corte de
metalinguagem levando junto as frases de transição.

- **GO-1 reescrita:** a abertura do parágrafo faz a ligação, pelo conectivo da relação
  lógica, por uma circunstância ou pela retomada da ideia anterior. Sujeito nominal seco
  abrindo parágrafo é exceção: no máximo cerca de 30% e nunca mais de dois seguidos. O
  capítulo abre retomando o anterior e fecha conduzindo ao próximo.
- **Ligar não é metalinguagem:** a transição que diz a relação entre as ideias e o
  parágrafo de síntese que costura capítulos ficam; a revisão ganhou o "cuidado inverso"
  e nunca propõe cortá-los. O GO-4 passa a nomear o vício oposto ao bloco denso, os
  parágrafos de uma frase em série.
- **Radar (`lint_peca.py`):** novo alerta `GO-1/abertura-nominal`, que dispara acima de
  ~30% de aberturas por sujeito nominal ou com três seguidas, em peça de seis ou mais
  parágrafos. Locuções ("A partir disso", "Uma vez que", "A meu ver") e retomadas ("O
  mesmo acórdão") não contam. A linha de estatística mostra a parcela, e há as opções
  `--max-abertura-nominal` e `--max-nominais-seguidas`. São 7 testes novos.
- Acompanha o `equipe-juridica` 0.4.1: os executores ganharam a regra com exemplo, e o
  crítico ganhou a lente de ligação.

## v1.3.0 (2026-10-20)

Revisão geral: auditoria das 15 skills por quatro revisores em paralelo, contagem de uso
nos registros de sessão e decisões do José. A complexidade do pedido passa a decidir a
profundidade, e o que toda peça carrega ficou menor (SKILL.md: 1.753 → 1.201 linhas;
cadeia de um REsp: −34%; peça protocolar: −63%).

**Arquitetura (`analise-processual`, `plano-de-respostas`, GUIA)**
- **Triagem de complexidade N1–N4** como primeira regra do pipeline: o nível é declarado
  em uma linha, sem pergunta e antes de ler qualquer documento (só o índice do PDF pode
  vir antes), e decide o plano, quem redige, o conselheiro e a verificação. N4 →
  proposta de `/equipe-juridica:iniciar`.
- **Profundidade sem paradas:** o checkpoint "Como ficou a G{N}?" deixa de ser padrão. N2
  segue geração a geração sem parar; N3 tem aprovação do plano e **um subagente Opus por
  tópico**, com leitura integral e costura do coordenador. Revisão tópico a tópico, só a
  pedido.
- **Agentes nativos com modelo por tarefa:** Haiku (mecânico), Sonnet (leitura, triagem,
  buscas com síntese), Opus (tópicos do N3, ratio) e **conselheiro Fable** nas decisões
  decisivas — o advisor da aba Code (`/advisor fable`) quando ligado; senão, subagente
  Fable com dossiê. Saem as referências ao conector de agentes externos.
- Rotas novas no orquestrador: contrarrazões, revisão de peça pronta, consulta pontual nos
  autos e andamento (conectores antes do navegador).
- **Remissão ao conector busca-autos** (busca por imagem nas páginas sem texto), com a
  regra de uso na `analise-processo-pje`: decide-se pelo índice; no N3/N4 a indexação
  começa no início, em segundo plano; só a parte que é imagem vai ao Colab; modo rápido
  por padrão. No teste com dois processos do TRF-5, os documentos escaneados achados
  passaram de 0 para 16 em 20.

**Skills: 15 → 13**
- Removida `peca-processual-base`: esqueleto e coerência da peça protocolada →
  `plano-de-respostas`; antecipação de objeção → `escrita-juridica/references/persuasao.md`.
- Removida `analise-estrategia`: vira o modo interno com foco em estratégia do `relatorio`.
- Sai das 14 skills o bloco "regra de uso" (pergunta pipeline × avulso), que nas sessões
  reais nunca foi respondido e o equipe-juridica anulava à mão.
- **Frontmatter YAML corrigido:** na v1.2.0, 7 descrições tinham ": " sem aspas e essas
  skills ficavam fora da lista que o modelo vê (só como comando de barra). As 13 passam
  em YAML estrito, com descrição de ~250 caracteres (o que produz e quando não usar).
- Template "só o delta" nas saídas (452 → 273 linhas).

**Saídas**
- `peca-recurso`: ramo de contrarrazões (não conhecimento primeiro; rebater cada ponto);
  cabimento só perguntado com mais de um recurso plausível; viabilidade com as bases do
  conector aplicáveis; eixo do REsp/RE pelo conselheiro no N3; fora do pipeline, REsp/RE
  assume N3.
- `peca-especifica`: bordas corrigidas (reconvenção na contestação; fim das "exceções"
  autônomas; exceção de pré-executividade).
- `peca-simples`: trilho protocolar com mini-modelo embutido, sem carregar a escrita
  inteira; no máximo uma pergunta.
- `memorial`: matriz eixo → documento/página da peça-base.
- `relatorio`: chance qualitativa com base declarada; o modo externo só afirma o que está
  nos autos ou no plano; confere se o workspace está defasado.

**Compartilhadas**
- `escrita-juridica` (361 → 195): núcleo com GO-1 a GO-6; persuasão, padrões da casa e
  revisão em `references/`, lidos em passos definidos; lentes "enumeração-andaime" e
  "metalinguagem" trazidas do equipe-juridica; rotas de revisão de peça pronta e de
  "remover juridiquês"; exemplo do GO-5 que contradizia o GO-6 corrigido.
- **Régua do parágrafo (GO-4), refeita pelo José:** uma ideia por parágrafo, normalmente
  em um ou dois períodos curtos; média de 70 a 90 palavras na peça; 120 como referência
  de teto, não como limite (125 ou 130 cabem se a ideia pede). Substitui os "2 a 4
  períodos / ~7 linhas" e a mediana de ~41 palavras.
- **Novo `escrita-juridica/scripts/lint_peca.py`:** varredura determinística do estilo
  (travessão, parágrafo acima da referência, média da peça fora de 70–90, aberturas
  repetidas, léxico ensaístico, "não é X, mas Y", "o mesmo") — radar, não juiz.
- `pesquisa-juridica` (189 → 90): só o método; bases e parâmetros pela descrição viva da
  ferramenta; rastro com ferramenta + ID + parâmetros.
- `verificacao-citacoes`: reabre precedentes pelo ID; inteiro teor onde a base oferece,
  declarando o alcance; o mecânico vai a subagentes (Haiku/Sonnet).
- `formatacao-entrega`: contrato `@tag` e `@citacao-ref` documentados; timbrado por
  `--template`.

**Scripts**
- `processo.py`: UTF-8 no console do Windows (antes quebrava em 2 de 4 PDFs reais);
  índice que separa nome e tipo e marca peça com critério (antes, 98% das páginas davam
  "peça"); aviso para PDF sem bookmarks, com remontagem pelo rodapé; novos `grep`,
  `refs`, `sem-texto`, `render` e `extract --pages`, com trava de tamanho; páginas sem
  texto e com OCR de terceiros marcadas — ponto de encaixe do MCP de embeddings
  multimodais, em desenvolvimento.
- `citar.py`: reconhece o cabeçalho de TRF-5, TRF-1 e TJPE (antes, só o do STJ); casa
  número exato ("REsp 213661" não casa mais "REsp 2136610"); recusa ementa truncada ou
  com "?" no lugar de aspas; lê só o registro da conversa atual e guarda as ementas em
  `<workspace>/citacoes/` (antes varria os registros de todos os projetos).
- `build_docx.py`: docstring corrigida; `--workspace`; **timbrado por modelo** —
  `--modelo <nome>` (modelos em `<raiz de dados>/modelos/`, fora do repositório),
  `--preparar-modelo` (cria o modelo a partir de um documento real do escritório) e
  limpeza automática de todo modelo (corpo, comentários, notas, imagens do corpo,
  metadados e propriedades do arquivo não passam para a peça).
- Testes novos: `tests/test_processo.py`, `test_citar.py`, `test_lint_peca.py` e
  `test_build_docx.py` (83 testes).

**Aquisição e documentação**
- `obter-processo`: modo consulta de andamento; o que está verificado (1º grau) e o que
  não está (2º grau) — a v1.1.0 anunciou "1º e 2º graus"; armadilhas de espera do
  download; painel padronizado; não abrir intimação pelo navegador (pode registrar ciência
  e abrir prazo).
- README e GUIA reescritos para a v1.3 (decisões travadas no GUIA).
- Removidos `.mcp.json.example` (URL desligada), `hooks/hooks.json` (vazio; nunca houve
  hook) e `docs/PR-OPENAI.md` (PR já mesclado).
- Variante ChatGPT Work/Codex congelada em 1.2.0. Registro: ela entrou no `main` em 09/09
  (PR #1) sem entrada própria neste changelog.

## v1.2.0 (2026-08-12)

Calibragem por feedback de uso real (revisão de peça densa, 8 constatações) +
correção do viés de inchaço na `peca-simples`. Uma única regra de ouro nova, para
não banalizar as GO; o resto encaixa em seções existentes.

**`escrita-juridica`:**
- **Nova GO-6 — definição por negação**: proibido definir/qualificar por negação
  quando ninguém sustentou o contrário ("não é projeto anunciado, mas…" → afirmar
  direto). Teste de triagem: *alguém nos autos sustentou o que estou negando?* —
  negação legítima (refutar tese, afastar precedente) se mantém.
- **GO-5 ampliado — metadiscurso estratégico**: além do comentário estilístico, é
  proibido revelar a arquitetura interna da tese ("argumento subsidiário", "o que
  se admite apenas para argumentar"). A peça mostra o resultado, nunca o processo.
- **Nota de método de revisão** (GO-4 a GO-6): diagnosticar antes de reescrever
  (estrutura ≠ vocábulo ≠ conteúdo; se só o léxico peca, preserva-se a arquitetura);
  agente auxiliar é radar, nunca revisor (localiza o padrão; a reescrita é do
  redator com o texto à vista).
- **Persuasão calibrada**: abrir o tópico afirmando a própria tese; distinção e
  objeção vêm depois; premissa fundamental abre o capítulo, não fica no meio.
- **Precisão**: o léxico não concede a premissa adversária ao relatar ato/tese
  contrária ("depender de providência futura a eficácia" → "ainda não editou"),
  com teste de varredura pela premissa nuclear; léxico da casa ("ação"/"demanda"
  em vez de "impetração").
- **Padrão da casa 1 + Ancoragem**: leitura dirigida estendida a prova documental
  e enumeração (estatuto, CNAE, cláusula) — fonte não se "joga", narra-se a cadeia
  amarrada ao dispositivo.

**`peca-processual-base`:**
- **Antecipação de objeção — oportunidade e lugar**: antecipa-se só a objeção
  provável e específica (nunca o desenho normal da ação); e no corpo da
  fundamentação, jamais nos pedidos ("pedido que se defende é pedido que se
  confessa frágil").

**`peca-simples`:**
- **Régua de duas pontas**: a skill só freava o vício de rasar e induzia o de
  inflar. Agora o porte é ditado pelo comando, com **bifurcação de porte (passo
  2.1)**: *protocolar* (só comunica/requer o rotineiro — parágrafos a uma lauda,
  sem pesquisa, 1 geração, sem plano) × *substancial* (fluxo completo). Teste
  objetivo: o leitor precisa ser convencido de algo? Na dúvida, perguntar o
  porte-alvo ao usuário.

## v1.1.1 (2026-08-05)

`escrita-juridica`: **nova regra de ouro GO-5 — registro técnico, não narrativo**
(feedback de uso real: as peças saíam fluidas, mas com fórmulas de crônica/ensaio e
padrão de formalidade abaixo do forense).

- Tabela de conversão com exemplos reais corrigidos pelo usuário ("é o que melhor
  revela o descompasso" → "parte de premissa que não corresponde à tese vinculante";
  "o problema não está em…"; "seria uma coisa; …, porém"; "e nunca o seguiu").
- Marcadores do registro ensaístico a varrer: avaliação impressionista do próprio
  argumento, contraste retórico em suspense, dramatização por reforço, metáfora/imagem,
  narrador comentando a própria peça.
- Regra de conversão: a frase técnica nomeia o objeto processual + a operação jurídica,
  sem avaliação impressionista nem imagem. A ênfase legítima segue sendo a da
  "Persuasão calibrada" (vocabulário forense tradicional, não ensaístico).
- Teste de varredura obrigatório na revisão final ("caberia numa crônica? reformule"),
  aplicado à peça inteira.
- Abertura da skill ajustada: "natural" = fluida no registro técnico-forense, não é
  licença literária (era a brecha que induzia o desvio).

## v1.1.0 (2026-08-05)

**`obter-processo` sai do stand-by: download automático dos autos no PJe.** A camada B
deixa de ser esqueleto e passa a baixar a íntegra do processo automatizando o navegador
(extensão do Claude no Chrome), a partir do número CNJ.

- **PJe mapeado ponta a ponta**, verificado ao vivo em duas versões (2.11 e 2.9.1.1):
  TRF-5 e TRF-1, 1º e 2º graus. Caminho completo em `references/pje.md` — endereços por
  tribunal/grau, `id` estáveis das seis caixas do número CNJ, disparo da busca, abertura
  dos autos, painel de filtros do download e conferência final.
- **Login e certificado digital continuam sendo do usuário** — a skill nunca digita
  credencial; se cair em tela de login, para e devolve a vez.
- **Armadilhas documentadas** (as que travam a automação na prática): o `window.confirm`
  nativo do aviso do CNJ, que congela a aba e a extensão (prevenir sobrescrevendo antes
  do clique) e **não atravessa abas** — precisa ser reaplicado na aba dos autos, onde o
  TRF-1 dispara um segundo `confirm` no download; o segundo ícone de download, que baixa
  só o documento aberto; e o "Índice do PDF", que **não** pode ser desmarcado, porque são
  esses bookmarks que a `analise-processo-pje` usa para ler autos enormes.
- **Regras gerais de automação**: não confiar em coordenadas de tela (usar seletor) nem
  no screenshot logo após AJAX (ler o DOM); em processos gigantes, combinar o recorte com
  o usuário e baixar seletivamente.
- Sistemas não mapeados (eproc, Projudi, e-SAJ, PJe de outros tribunais): a skill diz
  isso na cara e oferece mapear junto, gerando um novo `references/<sistema>.md`.
- Atualizados README (recursos, arquitetura, requisito do Chrome), `analise-processual`
  (roteamento) e o guia de construção.

## v1.0.5 (2026-07-28)

`escrita-juridica` ganha a seção **"Padrões da casa"** — padrões extraídos de peça
REAL do usuário (REsp manual de 2024, **recurso provido**), que ancoram o GO-4 e a
"Persuasão calibrada" em exemplo vencedor:

- Métrica-alvo medida na peça: mediana de 2 períodos / ~41 palavras por parágrafo;
  43% dos parágrafos com um único período.
- Sete padrões de construção: sanduíche de citação (anúncio → transcrição → leitura
  dirigida; nenhuma citação órfã); alavanca "Ora, se… (então)" (a premissa do próprio
  julgado como motor da conclusão); micro-conclusão parcial de 1 período fechando cada
  tópico; reformulação "Ou seja," (técnico → tradução direta); ênfase mirada no
  requisito/vício/situação (nunca no julgador); vocativo estratégico pontual nos
  momentos decisivos; recapitulação enumerada antes do fecho.
- TODO de exemplos-âncora do registro `peça` concluído (pendem `interno`/`externo`).

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
