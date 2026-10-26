# pratica-juridica

> **Variante ChatGPT Work / Codex:** a cópia adaptada em
> [`plugins/pratica-juridica-work`](plugins/pratica-juridica-work/README.md) está
> **congelada em 1.2.0** e não acompanha a v1.3. A análise da adaptação está em
> [`docs/ADAPTACAO-OPENAI.md`](docs/ADAPTACAO-OPENAI.md). O resto deste README descreve
> a versão Claude.

Plugin para o **Claude** que transforma um processo judicial em PDF (padrão **PJe**)
em análise e em **peças/relatórios jurídicos** — do reconhecimento dos autos à entrega
formatada em `.docx`. Um **orquestrador** mede a complexidade do pedido (N1 a N4),
entende o objetivo (recorrer, contestar, relatar, memorial…) e aciona skills
especializadas para pesquisar, redigir e conferir.

Pensado para a prática (advocacia, procuradorias, assessorias): lida com autos grandes
sem estourar o contexto, ancora cada argumento nos fatos do processo e na fonte
(lei, doutrina, jurisprudência) e **cola ementas verbatim**, sem redigitação.

> **Ambientes:**
> - **Aba Code do app desktop (Windows)** — o Claude trabalha direto no disco do
>   computador: roda o Python local e confere o PDF baixado na pasta de Downloads.
> - **Cowork** (app desktop) — ambiente isolado, que enxerga só a pasta montada na
>   sessão.
> - **Claude Code CLI** (terminal) — acesso ao disco como na aba Code.
>
> O que muda entre eles — onde os dados persistem, se o Claude enxerga o PDF baixado,
> se há advisor — está em *Persistência dos dados*, *Como funciona* e na skill
> `obter-processo`.

---

## O que ele faz

- **Mede o pedido antes de começar.** Classifica em N1 (simples), N2 (padrão), N3
  (complexo) ou N4 (equipe), declara o nível em uma linha e segue; você sobe ou desce.
  O nível decide o plano, quem redige, o conselheiro e a profundidade da verificação.
- **Baixa os autos ou consulta o andamento.** Para o andamento, usa primeiro os
  conectores que você tiver (ex.: Legal One, DataJud/DJEN); o navegador fica para quando
  eles não bastam. Para a íntegra, automatiza o **PJe** pela extensão do Claude no
  Chrome — caminho verificado ao vivo no 1º grau do TRF-5 e do TRF-1; o 2º grau ainda
  não foi percorrido. Login e certificado digital são sempre seus: o plugin nunca digita
  credencial. Já tem o PDF? Aponte o arquivo.
- **Reconhece autos grandes com eficiência.** Lê o *índice* do PDF (bookmarks do PJe),
  rankeia os documentos que importam para o seu objetivo e **extrai só esses** —
  processos de milhões de tokens cabem no fluxo sem carregar o PDF inteiro. Também busca
  texto nos autos, resolve referências "id N" e marca as páginas sem texto (escaneadas),
  que o Claude pode ler como imagem.
- **Produz a peça certa.** Recurso (apelação, agravo, embargos de declaração, RE/REsp) e
  contrarrazões; contestação, réplica, impugnação, embargos à execução ou de terceiro;
  petições simples; memorial; relatório interno ou para o cliente, inclusive de
  estratégia — cada um com estrutura e método próprios.
- **Pesquisa na fonte antes de afirmar.** Lei e doutrina (conector *Know-How Jurídico*)
  e jurisprudência (conector *juris_br*, nas bases que o próprio conector oferece), com
  rastro de proveniência.
- **Cita sem redigitar.** A ementa pesquisada é **colada verbatim** na peça
  (`@citacao-ref`), com fidelidade comprovável — jurisprudência ou trecho dos próprios
  autos.
- **Constrói o argumento pelo peso.** Antes do índice, mede quanto cada argumento pesa
  no convencimento do julgador: o que decide o resultado abre e ganha espaço, o que não
  muda nada sai ou vira uma oração, e cada tópico é o caminho até um resultado.
- **Escreve com método.** Plano de respostas, uma geração por vez, redação direto no
  arquivo e não no chat. Uma só mão escreve a peça: no N3, um subagente Opus prepara cada
  tópico e o Claude redige o todo.
- **Revisa a construção antes de entregar.** Com a peça pronta, a
  `sensibilidade-argumentativa` a reorganiza pelo peso, sem nada novo, e o
  `moderador-final` lê como o julgador e diz como decidiria; o Claude decide o que adotar.
- **Entrega formatada.** Gera `.docx` (fonte, recuos, citações e realce padronizados).
- **Confere antes de fechar.** A verificação cruza cada citação com a fonte real,
  contra citação alucinada ou superada, na profundidade do nível.

---

## Requisitos

- **Claude** — aba Code do app desktop, Cowork ou CLI.
- **Python 3** no sistema, com:
  ```
  pip install pypdfium2 python-docx
  ```
  `pypdfium2` extrai o texto e o índice do PDF dos autos (testado na 5.11.0);
  `python-docx` gera o `.docx`.
  Opcional: `pip install Pillow`, para a página escaneada renderizada como imagem (que o
  Claude lê) sair em cor; sem ele, o `render` gera PNG em tons de cinza. Não é preciso
  Tesseract nem outro OCR local.
- **Conectores MCP** habilitados na sua conta Claude (em *Conectores*):
  - **juris_br** — jurisprudência. Exige login. As bases disponíveis são as que o
    próprio conector lista, não uma lista fixa.
  - **Know-How Jurídico** — legislação comentada e doutrina, por área do Direito.
  - **Andamento** (opcional) — os que você tiver, como Legal One ou DataJud/DJEN, para
    consultar o andamento sem abrir o navegador.
  - **busca-autos** (opcional, local) — busca por imagem nas páginas escaneadas sem OCR.
    Só a parte do processo que é imagem vai ao Colab para indexar; o resto fica no
    índice local.

  Os conectores ficam na conta; o plugin não empacota servidor MCP nem traz
  configuração de MCP.
- **Extensão do Claude no Chrome** — para o `obter-processo` operar o PJe (download da
  íntegra ou consulta pelo navegador). Dispensável se você aponta o PDF e tem conector
  de andamento.

---

## Instalação

### App desktop (abas Code e Cowork)
1. **Customize → Plugins pessoais → + → Adicionar → Adicionar marketplace** e informe o
   repositório **`lazarofhn/pratica-juridica-plugin`** (ou a URL do GitHub) — o app puxa
   direto do GitHub, sem baixar nada manualmente.
2. Ainda em *Plugins pessoais*, instale o **pratica-juridica** do marketplace que você
   acabou de adicionar. Instalado na conta, ele fica disponível nas abas Code e Cowork.
3. As skills aparecem como `pratica-juridica:<skill>`.

> Alternativa offline (ou repositório privado sem acesso do colega): **Fazer upload de
> plugin** e envie um `.zip` do plugin (com `.claude-plugin/plugin.json` na raiz do arquivo).

### Claude Code (CLI)
```text
/plugin marketplace add lazarofhn/pratica-juridica-plugin
/plugin install pratica-juridica@pratica-juridica
/reload-plugins
```

Em qualquer ambiente, comece por:
```text
/pratica-juridica:analise-processual
```

---

## Como usar

Descreva o **objetivo** e aponte o PDF dos autos — ou dê o número CNJ. O orquestrador
`analise-processual` declara o nível e roteia o resto. Exemplos:

- "Faça uma **apelação** contra esta sentença." (autos em `processo.pdf`)
- "Preciso de um **REsp**; o mérito esbarra na Súmula 7?" (ele faz o estudo de
  viabilidade e ajusta o eixo da peça)
- "Gere um **relatório para o cliente** sobre o andamento."
- "Monte a **estratégia** deste caso antes de eu decidir a peça." (relatório interno
  com foco em estratégia)
- "**Baixe os autos** do 1234567-89.2024.4.05.8100."
- "**Como está** o 1234567-89.2024.4.05.8100? Não precisa baixar." (consulta de
  andamento)

O plugin volta aos autos a cada etapa (ancoragem nos fatos), pesquisa a fundamentação,
redige geração a geração e entrega o `.docx`. Aprovação, só a do plano no N3 — ou
tópico a tópico, se você pedir ("revisar tópico a tópico").

---

## Como funciona (arquitetura v1.4)

Orquestrador + camadas componíveis — skill nova só quando muda **estrutura e finalidade**;
tom e método de pesquisa são **parâmetros** de skills compartilhadas.

### Triagem de complexidade (primeira regra do pipeline)

| Nível | Pedido típico | Plano de respostas | Quem redige | Conselheiro Fable | Revisores | Verificação |
|---|---|---|---|---|---|---|
| **N1** simples | juntada, ciência, prazo, resposta a despacho simples | — | o Claude, de uma vez | — | — | referências aos autos |
| **N2** padrão | peça ou relatório com 1 a 3 fundamentos | curto, com o mapa de peso: mostra e segue | o Claude, geração a geração | — | sensibilidade + moderador (Opus) | completa |
| **N3** complexo | REsp/RE, apelação ou contrarrazões com várias teses; memorial decisivo | mapa de peso e plano aprovados antes de redigir | o Claude, com um dossiê Opus por tópico | nas decisões decisivas | sensibilidade + moderador (Fable) | completa, com subagentes |
| **N4** equipe | várias frentes ou processos; parecer amplo | o do Claude, no protocolo da equipe | o Claude, com o operacional da equipe | nas decisões decisivas | sensibilidade + moderador (Fable) | verificador da equipe |

O N4 vai para o plugin **`equipe-juridica`** (`/equipe-juridica:iniciar`), sempre por
proposta e com o seu ok — nunca automático.

### Agentes e modelos

Só subagentes nativos do Claude, cada modelo na sua tarefa. O juízo — tese, coerência
final, ratio de precedente, o que dizer ao cliente — fica com a sessão principal.

- **Haiku** — o mecânico: localizar documentos no índice, inventário de citações,
  conferir números, datas e IDs.
- **Sonnet** — ler e triar documentos extraídos, rodar buscas de jurisprudência e
  sintetizar, primeira revisão de estilo.
- **Opus** — dossiê de tópico no N3, a `sensibilidade-argumentativa` (reorganiza a peça
  pronta pelo peso) e conferência de ratio.
- **Fable** — conselheiro nas decisões decisivas de N3/N4 (cabimento e eixo do recurso,
  escolha e ordem das teses, risco num relatório, conflito entre precedentes), quando a
  sessão principal não é Fable. Com o advisor da aba Code ligado (`/advisor fable`,
  recurso experimental), o Claude o consulta antes de decidir; sem advisor (ex.:
  Cowork), abre um subagente Fable com um dossiê curto. No N3 e no N4, também o
  `moderador-final`, que lê a peça pronta como o julgador. O uso do Fable pode consumir
  créditos conforme o seu plano.

### Skills (13)

```
A. ORQUESTRADOR    analise-processual    → triagem N1–N4, agentes e roteamento
B. AQUISIÇÃO       obter-processo        → baixa os autos do PJe pelo Chrome ou consulta o andamento
C. ANÁLISE         analise-processo-pje  → extração seletiva do PDF (índice → ranking → extração)
D. SAÍDAS          peca-recurso, peca-especifica, peca-simples, memorial,
                   relatorio (interno|externo; inclui estratégia)
E. COMPARTILHADAS  plano-de-respostas, pesquisa-juridica, escrita-juridica,
                   formatacao-entrega, verificacao-citacoes
```

Dois agentes acompanham as skills (`agents/`): `sensibilidade-argumentativa` e
`moderador-final`, os revisores da peça pronta, que a `equipe-juridica` também usa.

Saíram na v1.3: `peca-processual-base` (esqueleto e coerência → `plano-de-respostas`;
antecipação de objeção → `escrita-juridica`) e `analise-estrategia` (→ `relatorio`, modo
interno com foco em estratégia).

---

## Persistência dos dados

Cada processo tem um **workspace** — extratos dos autos em `.md`, plano, rastro de
pesquisas, `.docx` — reaproveitado entre tarefas e sessões, desde que fique numa pasta
que não some com a sessão.

**Recomendado: fixe a pasta com `PRATICA_JURIDICA_DATA`.** Escolha uma pasta sua, que
você saiba onde está e inclua no backup, e defina a variável (no Windows):

```text
setx PRATICA_JURIDICA_DATA "C:\Users\<você>\Documents\dados-juridicos"
```

Feche e reabra o app (ou o terminal) para ela valer. Isso cobre a aba Code e o CLI. O
Cowork não guarda a variável entre sessões: ali a pasta fixa é `dados-juridicos/`
dentro da pasta montada na sessão, que o Claude cria na primeira análise e avisa.

Sem a variável, o `processo.py workspace` resolve nesta ordem: `CLAUDE_PLUGIN_DATA`
(Claude Code) → `dados-juridicos/` já existente na pasta de trabalho → `./outputs` da
sessão.

**O aviso de pasta temporária.** Quando o workspace cai em `./outputs`, o script avisa
que a pasta é temporária: não persiste entre sessões. Não é erro — o trabalho da sessão
segue —, mas os extratos somem com ela e o próximo pedido sobre o mesmo processo refaz
a extração. O Claude repassa o aviso em uma linha; para ele não voltar, defina
`PRATICA_JURIDICA_DATA` (no Cowork, mantenha `dados-juridicos/` na pasta montada).

---

## Privacidade

- O plugin não envia os autos a terceiros. Os scripts (leitura do PDF, geração do
  `.docx`) rodam no Python do seu ambiente, sem chamadas de rede.
- O índice de cada PDF fica em cache na pasta temporária do sistema, só com números de
  página e de documento — nenhum texto dos autos.
- O `@citacao-ref` lê só o registro da conversa atual (outro projeto, só se você o
  apontar com `--transcript`) e guarda as ementas citadas em `<workspace>/citacoes/`.
- O que o Claude lê vai para o Claude, como todo conteúdo da conversa: trechos
  extraídos dos autos, páginas renderizadas como imagem, telas do PJe, respostas dos
  conectores.
- Os subagentes são do próprio Claude: o plugin não repassa os autos a outro provedor
  de IA.
- Os conectores recebem o que o Claude manda a eles — os termos da pesquisa e, na
  consulta de andamento, o número do processo. O rastro das buscas fica no workspace do
  processo.
- O `equipe-juridica` (N4) é outro plugin, com regras próprias.

---

## Contribuições e status

Plugin em uso real, evoluindo a cada caso. *Issues* e sugestões são bem-vindos.
Consulte o [CHANGELOG](./CHANGELOG.md) para o histórico de versões.

Autoria e manutenção: **José Lázaro**.
Licença: **MIT** — ver [LICENSE](./LICENSE).
