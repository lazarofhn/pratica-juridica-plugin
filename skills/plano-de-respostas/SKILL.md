---
name: plano-de-respostas
description: (camada E — compartilhada, SEMPRE roda ANTES de escrever) Monta o PLANO DE RESPOSTAS de qualquer output — o índice numerado do documento e a decisão de em QUANTAS gerações a redação será segmentada. Distingue seções (estrutura) de gerações (passes de escrita): documento simples = 1 geração; complexo = N gerações (uma por seção/causa de pedir/requisito), acumulando no documento final. Em peças grandes (N gerações), apresenta o plano ao usuário para aprovação antes de escrever.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Plano de Respostas (camada E — passo obrigatório antes de escrever)

> Insight do José: antes de construir o documento, a IA precisa saber **em quantas
> respostas a tarefa será segmentada**. O plano revela a complexidade — não o
> contrário. Roda SEMPRE, mesmo em peça simples.

## O que este passo faz (e o que NÃO faz)
- **NÃO inventa a estrutura da peça.** A estrutura vem da skill de output (D), que a
  busca na `peca-processual-base` / no artigo do CPC do tipo de peça. Aqui a gente
  **organiza** esse índice e **decide a segmentação**.
- **Distinção central — seções ≠ gerações.** Uma seção é uma parte da *estrutura*
  do documento; uma geração é um *passe de escrita* da IA. **Não é 1:1**: várias
  seções curtas podem sair numa geração só; uma causa de pedir densa pode exigir
  várias gerações (subseções). É essa a decisão que se toma aqui.

## Passo 1 — Montar o índice numerado
Liste as seções do documento, na ordem, a partir da estrutura definida pela skill de
peça. Os **fatos** vêm do workspace do processo (saída da `analise-processo-pje`),
não de releitura. Exemplo (recurso — admissibilidade individualizada, sem mistura):
```
1. Endereçamento
2. Cabimento
3. Tempestividade e prequestionamento
4. Síntese fática
5. Fundamento 1 (mérito)
6. Fundamento 2 (mérito)
7. Pedidos
```
Causas de pedir / fundamentos densos podem virar subseções (5.1, 5.2…).
> Note: NÃO junte "Endereçamento e Fatos" nem lumpe a admissibilidade num tópico
> só (ver regra de ouro abaixo).

## Passo 2 — Decidir a segmentação (quantas gerações)
Para cada item, marque se entra na mesma geração ou em geração própria. Gatilhos
para segmentar (N gerações):
- ≥ 2 fundamentos/causas de pedir de mérito; **ou**
- tutela de urgência + mérito; **ou**
- documento projetado > ~10 páginas.

Regras de ouro herdadas das skills de peça (respeitar quando aplicável):
- **RE/REsp — admissibilidade individualizada (regra dura):** cada requisito de
  admissibilidade em foco próprio. O **cabimento sempre em geração isolada**;
  requisitos correlatos (tempestividade, prequestionamento) podem compartilhar uma
  geração. **NUNCA** lumpe todos num só tópico e **NUNCA** misture admissibilidade
  com a **síntese fática** ou com o mérito. Isso vale **inclusive** quando o
  carro-chefe do recurso for processual (ex.: art. 1.022 CPC) — não rebaixe a
  admissibilidade a formalidade.

Se nenhum gatilho → **1 geração** (escrita de uma vez). Ainda assim o plano é
explicitado, só que com um item.

## Passo 3 — Aprovação (só em peças grandes) — DECISÃO TRAVADA
- **Se N > 1 gerações:** apresente o plano (índice + segmentação) ao usuário e
  **aguarde o ok** antes de escrever — não gaste as gerações sem aval.
- **Se 1 geração:** siga direto, sem checkpoint.

## Passo 4 — Executar UMA geração por vez (quando N > 1)
> ⚠️ **ERRO FATAL a evitar:** escrever todas as gerações num único output (um só
> `Write`/uma só resposta). Isso derrota a segmentação e produz peça **RASA**,
> mesmo em modelo de contexto longo (Opus 1M). Cada geração é um **ciclo próprio**,
> executado em **passo separado** — não em lote.

Para cada geração N, na ordem do plano:
1. **Pesquisa focada** no tema daquela seção (`pesquisa-juridica`, perfil/assunto
   próprios, **re-rodada na fonte** — regra do rastro). A pesquisa material é
   segmentada aqui. Quando a seção invoca **lei/doutrina** (e não só jurisprudência),
   consulte os **DOIS pilares** — leia o dispositivo e a doutrina no Know-How antes
   de afirmar (R1), inclusive em seções processuais como cabimento/admissibilidade.
   **Volte também aos autos** (workspace, via `analise-processo-pje`: `find`/`extract`)
   para **ancorar a seção aos fatos concretos** do processo. A análise inicial não
   esgota o uso: cada geração costuma exigir uma consulta pontual aos autos (ex.:
   quais questões os embargos suscitaram, o que a decisão recorrida disse).
2. **Redação profunda** apenas daquela seção (`escrita-juridica`, registro da
   peça), escrita **direto no arquivo** (`@tag`/`.md` → `.docx` via
   `formatacao-entrega`), acumulando no documento com o contexto das anteriores.
3. **Finalizar + CHECKPOINT:** grave a seção no documento e, **no chat, apresente só
   um RESUMO** — as "notas da subgeração": o que a seção faz, fontes/precedentes
   usados e decisões tomadas. **NÃO reproduza a redação inteira no chat** — o texto já
   está no `.docx`; recolá-lo só queima contexto de output que faz falta para escrever
   as próximas seções (a redação boa é longa; o chat é para o controle, não para o
   texto). Então pergunte **"Como ficou a G{N}?"** e só avance para a G{N+1} depois do
   retorno dele.

Nunca pule o checkpoint nem agrupe gerações. Concluídas todas, faça uma passada
final de **costura** (transições e coerência fatos ↔ fundamentos ↔ pedidos).

### Gerações densas — duas subgerações (ideia do José)
Quando a seção combina **lei/doutrina E jurisprudência de peso**, quebre a geração
em dois passes, para não empilhar consulta demais num só turno:
- **Subgeração A — fundação (lei + doutrina):** consulte o Know-How, escreva a seção
  ancorada no dispositivo e na doutrina. Finalize **no arquivo** e, no chat (resumo, não
  a redação — Passo 3), pergunte: *"Posso seguir com a complementação da jurisprudência?"*.
- **Subgeração B — jurisprudência (confirmar/corrigir):** com o ok, rode a pesquisa
  de jurisprudência conforme o método (escada temporal, filtros, fracionamento,
  rastro) e **complemente ou corrija** a seção conforme os tribunais decidem. Feche
  com *"Como ficou a G{N}?"*.

Ordem é **doutrina → jurisprudência** (a lei/doutrina fixa a tese; a jurisprudência
mostra a aplicação e pode derrubá-la — é a camada de correção). Aplique só nas
seções densas; as curtas seguem em passe único.
> Não confundir com o **estudo de viabilidade recursal** (peca-recurso, 2A): aquele
> é PRÉVIO, no nível do plano, e pode até PARTIR da jurisprudência para definir a
> natureza da peça. A subgeração B é DENTRO da geração, com a arquitetura já decidida.

## Saída deste skill
Um plano executável: o índice + a marcação de segmentação + por seção, qual **perfil
de pesquisa** e qual **registro de escrita**. Salve o plano aprovado no workspace do
processo (`${CLAUDE_PLUGIN_DATA}/processos/<numero-cnj>/`) como blueprint — útil em
peças grandes e para retomar o trabalho depois.

## Não confundir com o "plano de leitura"
Este é o **plano de respostas** (como *escrever*, roda antes da redação). É diferente
do **plano de leitura** da `analise-processo-pje` (quais documentos *extrair*, roda
antes, na análise).

## Nota (Claude Code)
Seções independentes podem ser escritas por subagentes em paralelo, mas em peça
jurídica a **coerência** pesa mais que a velocidade: repasse o contexto acumulado e
faça a costura final num único passe.

## TODO
- [ ] Calibrar o limiar de páginas do gatilho (~10) com o uso real.
