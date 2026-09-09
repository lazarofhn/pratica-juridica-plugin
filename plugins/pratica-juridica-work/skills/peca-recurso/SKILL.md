---
name: peca-recurso
description: Redige recursos e contrarrazões com análise de cabimento, admissibilidade e fundamentos da decisão impugnada.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.


# Peça: Recurso (camada D)

Skill de output fina. A lógica comum às peças protocoladas está em
`peca-processual-base` (endereçamento, estrutura, método de pesquisa) — **puxe-a**.
Aqui ficam só a estrutura e as decisões próprias de recurso.

## 1. Quando ativar
Objetivo do usuário = recorrer de uma decisão/sentença/acórdão.

## 2. Perguntas antes de começar — identificar o recurso
O recurso pode vir de três formas:
- **Já indicado:** "faça uma apelação contra a sentença" → siga.
- **Omitido:** "faça o recurso dessa decisão" → **você define o cabível, mas
  confira o cabimento e informe a escolha. Pergunte se houver alternativas
  materiais que o contexto não permita resolver.**
- **Dúvida real do usuário** sobre qual cabe → ajude a decidir (pesquisa
  processual) antes de escrever.

## 2A. Estudo de viabilidade recursal — OBRIGATÓRIO em REsp/RE
Antes de definir a estrutura, faça um **estudo de como o STJ/STF vêm decidindo o
tema** (via `pesquisa-juridica`; em matéria tributária, cruzar também CARF e
Soluções de Consulta da RFB). Motivo: **o modo como a Corte decide define a
NATUREZA da peça**, não só o conteúdo.
- Se o **mérito esbarra em óbice de conhecimento** (Súmula 7/STJ — reexame de
  prova; Súmula 279/STF), o carro-chefe **não** pode ser o mérito. Migre o eixo
  central para **questões conhecíveis**: vícios processuais (negativa de prestação
  jurisdicional — art. 1.022 CPC), questões **de direito** puras, divergência.
- Identifique o **precedente qualificado** que rege o tema e eventuais **óbices
  sumulares** logo de saída.
- Este estudo pode ser **preliminar** (estratégia). Na redação, a pesquisa é
  **conferida** na fonte salva ou novamente consultada (ver `pesquisa-juridica`, regra do rastro) — não se
  apoie na memória da conversa.
- **Respeite a competência da via — não misture REsp com RE.** No REsp, evite erigir
  em tópico autônomo argumento de índole **constitucional** (isonomia, capacidade
  contributiva, art. 150 CF etc.): isso "cheira" a **matéria de recurso
  extraordinário** e enfraquece o especial. Se o ponto ajuda, **dilua-o como reforço**
  dentro das teses infraconstitucionais (ex.: a Solução de Consulta vinculante e o
  CARF que reconhecem o crédito entram para demonstrar que a **omissão era decisiva**,
  não como capítulo de isonomia). Espelhe o cuidado no RE (não travar tese
  infraconstitucional como se fosse constitucional).
- **O pedido segue o eixo.** Se o carro-chefe é a negativa de prestação jurisdicional
  (art. 1.022), o pedido é **anulatório/de retorno** à origem — **não** peça
  provimento direto do mérito, sob pena de reintroduzir o óbice (Súmula 7) que se
  contornou.

## 3. Estrutura do documento
- Se o usuário não especificar, **busque a estrutura no artigo do CPC que regula
  aquele recurso** (via `peca-processual-base` / Know-How) — não de memória (R1).
- Fallback comum: Fatos → Requisitos de Admissibilidade → Fundamentos → Pedidos.
- Subsegmentável conforme o `plano-de-respostas`.
- **Colacione a decisão recorrida (praxe em recurso):** transcreva a **ementa** e os
  **trechos cruciais** do julgado impugnado e, havendo, do **acórdão dos embargos** —
  é neles que se demonstra o vício. Use `@citacao-ref` com arquivo, hash e referência dos autos (verbatim do
  workspace), **não redigite**. Em recurso por negativa de prestação jurisdicional, a
  ementa dos ED costuma ser a **própria prova** da omissão/contradição (fundamentação
  genérica).

## 4. Plano de respostas (segmentação)
- **Ênfase média-alta em admissibilidade por padrão** (tempestividade, cabimento,
  preparo/custas).
- **REGRA DE OURO — RE e REsp:** os requisitos de admissibilidade são vários e os
  tribunais superiores muito exigentes; a falta de fundamentação **específica** de
  um requisito é causa de não conhecimento (ex.: faltar o tópico de Repercussão
  Geral no RE). Por isso, salvo comando em contrário, **dê fundamentação específica a cada
  requisito de admissibilidade** no `plano-de-respostas` — o **cabimento sempre em
  tópico isolado**; correlatos (tempestividade, prequestionamento) podem
  compartilhar. **Nunca** misture admissibilidade com a síntese fática nem com o
  mérito. Vale mesmo quando o eixo central do recurso for processual (art. 1.022).
- Confirme os requisitos do recurso concreto na fonte (CPC + Know-How), não de
  memória (R1).

## 5. Pesquisa (via peca-processual-base → pesquisa-juridica)
- **Duas linhas**, conforme os perfis:
  - `processual/admissibilidade` — cabimento e requisitos do recurso.
  - `mérito` — a(s) tese(s) de fundo, **segmentada(s) por fundamento**.
- Filtros sempre que possível (R2); nunca inventar julgado (R3); rastro em
  `pesquisas.jsonl`.

## 6. Escrita
`escrita-juridica`, registro `peça`. Saída no formato `@tag` (vira `.docx`).
Siga `plano-de-respostas`: pesquisa, redação, revisão e checkpoint em arquivo,
com aprovação intermediária apenas quando combinada com o usuário.

## 7. Entrega
Output externo → `formatacao-entrega` (`.docx`; timbre depende de asset fornecido), salvo no workspace.

## 8. Verificação
`verificacao-citacoes` **antes de fechar** (obrigatória). Em RE/REsp, confira
também que **cada requisito de admissibilidade** tem seu tópico fundamentado.

## 9. Regras de ouro / vícios a evitar
- Admissibilidade de RE/REsp: fundamentação específica de **cada** requisito é
  inegociável (um requisito sem tópico próprio pode derrubar o recurso inteiro).
- Não presumir requisitos de memória — confirmar na fonte.
- Coerência entre a decisão recorrida, os fundamentos do recurso e os pedidos.
