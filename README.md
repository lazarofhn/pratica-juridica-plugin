# pratica-juridica

Plugin para o **Claude** que transforma um processo judicial em PDF (padrão **PJe**)
em análise e em **peças/relatórios jurídicos** — do reconhecimento dos autos à entrega
formatada em `.docx`. Um **orquestrador** entende o seu objetivo (recorrer, contestar,
relatar, memorial…) e aciona skills especializadas para pesquisar, redigir e conferir.

Pensado para a prática (advocacia, procuradorias, assessorias): lida com autos grandes
sem estourar o contexto, ancora cada argumento nos fatos do processo e na fonte
(lei, doutrina, jurisprudência) e **cola ementas verbatim**, sem redigitação.

> **Funciona nos dois ambientes do Claude:**
> - **Claude Code** (CLI/terminal) — instalação por marketplace (repositório GitHub).
> - **Claude Desktop / Cowork** (app) — instalação por upload em *Plugins pessoais*.
>
> O plugin **detecta o ambiente** e se adapta sozinho (caminhos de trabalho,
> descoberta de transcript, diretório de dados gravável). Veja *Instalação* e
> *Persistência dos dados*.

---

## O que ele faz

- **Reconhece autos grandes com eficiência.** Lê o *índice* do PDF (bookmarks do PJe),
  rankeia os documentos que importam para o seu objetivo e **extrai só esses** —
  processos de milhões de tokens cabem no fluxo sem carregar o PDF inteiro.
- **Produz a peça certa.** Recurso (apelação, agravo, embargos, RE/REsp, contrarrazões),
  contestação/impugnação/embargos, petições simples, memorial, relatório (interno ou
  para o cliente) e análise de estratégia — cada uma com estrutura e método próprios.
- **Pesquisa na fonte antes de afirmar.** Lei e doutrina (conector *Know-How Jurídico*)
  e jurisprudência (conector *juris_br*: STJ, STF, CARF, RFB/Cosit, TCU, TRF-5), com
  filtros e rastro de proveniência.
- **Cita sem redigitar.** A ementa pesquisada é **colada verbatim** na peça
  (`@citacao-ref`), com fidelidade comprovável — jurisprudência ou trecho dos próprios
  autos.
- **Entrega formatada.** Gera `.docx` (fonte, recuos, citações e realce padronizados).
- **Confere antes de fechar.** Uma etapa de verificação cruza cada citação com a fonte
  real, contra citação alucinada ou superada.
- **Escreve com método.** Uma seção por vez, com checkpoint; a redação vai para o
  documento, não para o chat (poupa contexto para o texto render).

---

## Requisitos

- **Claude Code** ou **Claude Desktop (Cowork)**.
- **Python 3** disponível no sistema, com:
  ```
  pip install pypdfium2 python-docx
  ```
  (`pypdfium2` = extração do PDF dos autos; `python-docx` = geração do `.docx`.)
- **Conectores MCP** habilitados na sua conta Claude (em *Conectores*), para os recursos
  de pesquisa/citação:
  - **juris_br** — jurisprudência (STJ, STF, CARF, RFB, TCU, TRF-5). *Público.*
  - **Know-How Jurídico** — legislação comentada + doutrina, por área do Direito.

  As URLs de referência estão em [`.mcp.json.example`](./.mcp.json.example). Os conectores
  são do lado da conta (claude.ai/OAuth) — o plugin não empacota servidores MCP.

---

## Instalação

### Claude Code (CLI)
```text
/plugin marketplace add lazarofhn/pratica-juridica-plugin
/plugin install pratica-juridica@pratica-juridica
/reload-plugins
```
Depois, comece por:
```text
/pratica-juridica:analise-processual
```

### Claude Desktop / Cowork (app)
1. **Customize → Plugins pessoais → + → Adicionar → Adicionar marketplace** e informe o
   repositório **`lazarofhn/pratica-juridica-plugin`** (ou a URL do GitHub) — o app puxa
   direto do GitHub, sem baixar nada manualmente.
2. Ainda em *Plugins pessoais*, instale o **pratica-juridica** do marketplace que você
   acabou de adicionar.
3. As skills aparecem como `pratica-juridica:<skill>`.

> Alternativa offline (ou repositório privado sem acesso do colega): **Fazer upload de
> plugin** e envie um `.zip` do plugin (com `.claude-plugin/plugin.json` na raiz do arquivo).

---

## Como usar

Descreva o **objetivo** e aponte o PDF dos autos. O orquestrador `analise-processual`
roteia o resto. Exemplos:

- "Faça uma **apelação** contra esta sentença." (autos em `processo.pdf`)
- "Preciso de um **REsp**; o mérito esbarra na Súmula 7?" (ele faz o estudo de
  viabilidade e ajusta o eixo da peça)
- "Gere um **relatório para o cliente** sobre o andamento."
- "Monte a **estratégia** deste caso antes de eu decidir a peça."

O plugin analisa os autos sob demanda a cada etapa (ancoragem nos fatos), pesquisa a
fundamentação, redige seção a seção com checkpoints e entrega o `.docx`.

---

## Como funciona (arquitetura)

Orquestrador + camadas componíveis — skill nova só quando muda **estrutura e finalidade**;
tom e método de pesquisa são **parâmetros** de skills compartilhadas.

```
A. ORQUESTRADOR    analise-processual         → porta de entrada (roteia por objetivo)
B. AQUISIÇÃO       obter-processo             → opcional; padrão = PDF baixado manualmente
C. ANÁLISE         analise-processo-pje       → extração seletiva do PDF (índice → ranking → extrai)
D. OUTPUTS         peca-recurso, peca-especifica, peca-simples, memorial,
                   relatorio, analise-estrategia
E. COMPARTILHADAS  peca-processual-base, pesquisa-juridica, escrita-juridica,
                   plano-de-respostas, formatacao-entrega, verificacao-citacoes
```

---

## Persistência dos dados

Cada processo tem um **workspace** (documentos extraídos em `.md`, resumo, rastro de
pesquisas, `.docx`), reaproveitado entre tarefas e sessões. O diretório é resolvido de
forma **gravável e automática**, conforme o ambiente:

`PRATICA_JURIDICA_DATA` (se você quiser fixar um local) → `CLAUDE_PLUGIN_DATA`
(Claude Code) → pasta **`dados-juridicos/`** detectada na sua pasta de trabalho →
`./outputs` (sessão).

No Claude Desktop/Cowork, na primeira análise o plugin cria a pasta `dados-juridicos/`
na pasta que você montou na sessão e avisa — dali em diante os dados dos processos
persistem no seu computador, sem configurar nada.

---

## Privacidade

- A leitura dos autos e a geração do `.docx` rodam **localmente** (Python no seu sistema);
  o PDF do processo não é enviado a lugar nenhum pelo plugin.
- A pesquisa usa os **conectores MCP** da sua conta; o rastro das buscas fica no
  workspace do processo.

---

## Contribuições e status

Plugin em uso real, evoluindo a cada caso. *Issues* e sugestões são bem-vindos.
Consulte o [CHANGELOG](./CHANGELOG.md) para o histórico de versões.

Autoria e manutenção: **José Lázaro**.
Licença: **MIT** — ver [LICENSE](./LICENSE).
