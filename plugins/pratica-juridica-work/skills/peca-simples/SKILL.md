---
name: peca-simples
description: Redige manifestações, juntadas e requerimentos guiados pelo comando do usuário ou do juízo, com extensão proporcional ao ato.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.


# Peça: Simples (camada D)

Skill de output fina. O comum às peças protocoladas está em `peca-processual-base`
(endereçamento, estrutura, método de pesquisa) — **puxe-a**. Aqui fica só o que é
próprio.

> ⚠️ **O porte é ditado pelo COMANDO, não pela skill — régua de duas pontas.**
> "Simples" não significa rasa: é chamada assim apenas por **não** ter nomenclatura
> nem requisitos próprios no CPC (diferente da `peca-especifica`), e **quando o
> comando exigir** pode ter densidade igual à de uma peça específica ou de um
> recurso. Mas o inverso também é defeito: **inflar uma petição protocolar de uma
> lauda é tão grave quanto rasar uma manifestação densa** — a divagação em peça de
> rotina irrita o juízo e enterra o requerimento. Não presuma o porte em nenhuma
> direção: decida pela **bifurcação do passo 2.1**.

## 1. Quando ativar
Petição de rotina sem previsão específica no CPC: manifestação, juntada, provas,
ciência, cumprimento de despacho, pedido incidental curto ou não.

## 2. Perguntas antes de começar — identificar o COMANDO
O driver é o comando. Antes de escrever, deixe claro **o que se está respondendo**:
- Comando do **usuário** ("manifeste sobre a proposta de acordo", "peça a produção
  de prova pericial"); **ou**
- **Despacho/decisão que intimou** a parte representada — leia essa decisão no
  workspace (`analise-processo-pje`) e extraia exatamente **o que o juízo pede**.
- Se o comando não estiver claro, pergunte.

### 2.1 Bifurcação de porte (decida ANTES de escrever)
Identificado o comando, classifique o trilho. **Teste objetivo: o leitor precisa
ser CONVENCIDO de algo?**
- **Protocolar** — a petição só comunica, requer o rotineiro ou cumpre: juntada de
  documentos, ciência, dilação de prazo, cumprimento de despacho, habilitação de
  patrono. Entregável: **de um parágrafo a uma lauda**. Fluxo curto: **sem
  pesquisa, 1 geração, sem segmentação do plano** — direto para escrita
  (`escrita-juridica`, registro `peça`) → entrega (`formatacao-entrega`);
  verificação só se houver alguma citação. Dizer mais do que o ato exige é vício
  (parente do "antecipar objeção que ninguém fez": sinaliza insegurança).
- **Substancial** — há mérito ou posição a defender: manifestação sobre laudo,
  sobre proposta de acordo com contrapontos, impugnação incidental. Segue o fluxo
  completo dos passos 3-8, como qualquer peça.
- **Na dúvida, pergunte o porte-alvo ao usuário** ("uma lauda ou desenvolvimento
  completo?") — pergunta barata que evita os dois vícios.

## 3. Estrutura do documento
- **Livre, guiada pelo comando** (não há forma imposta pelo CPC). Costuma ser mais
  atrelada a **fatos**.
- Ainda assim use o endereçamento e as boas práticas da `peca-processual-base`.
- Subsegmentável conforme o `plano-de-respostas`.

## 4. Plano de respostas (segmentação)
- **Depende do conteúdo, como as demais.** Manifestação simples → 1 geração;
  manifestação densa (várias questões, muitos fatos) → N gerações. Não force 1 —
  **nem force N**: petição **protocolar** (passo 2.1) é 1 geração por definição e
  dispensa o plano.

## 5. Pesquisa (via peca-processual-base → pesquisa-juridica)
- **Sob demanda:** só acione quando a manifestação tiver conteúdo de mérito
  jurídico. Muitas peças simples são só fáticas e dispensam pesquisa.
- Quando houver mérito, mesmas regras (filtros R2, nunca inventar R3, rastro).

## 6. Escrita
`escrita-juridica`, registro `peça`. Saída no formato `@tag` (vira `.docx`).

## 7. Entrega
Output externo → `formatacao-entrega` (`.docx`; timbre depende de asset fornecido), salvo no workspace.

## 8. Verificação
`verificacao-citacoes` **antes de fechar** — se houver qualquer citação de
lei/jurisprudência/autos.

## 9. Regras de ouro / vícios a evitar
- **Responder exatamente ao comando** — nem menos (deixar pedido do juízo sem
  resposta) nem divagar além do que foi pedido. O vício mais comum do modelo é o
  segundo: dizer mais do que o ato exige.
- **Não presumir porte em nenhuma direção**: nem simplicidade (rasar manifestação
  densa) nem complexidade (inflar petição protocolar). O esforço se dimensiona pelo
  comando, via bifurcação do passo 2.1.
