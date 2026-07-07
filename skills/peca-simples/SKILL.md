---
name: peca-simples
description: (camada D) Produz petições SEM nomenclatura ou requisitos próprios no CPC — manifestações, juntada de documentos, requerimento/especificação de provas, ciência, cumprimento de despacho, pedidos incidentais. Guiada pelo COMANDO (do usuário ou do despacho/decisão que intimou a parte). "Simples" = sem previsão específica, NÃO = rasa: pode ser tão densa quanto um recurso. Skill fina que puxa a camada E.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Peça: Simples (camada D)

Skill de output fina. O comum às peças protocoladas está em `peca-processual-base`
(endereçamento, estrutura, método de pesquisa) — **puxe-a**. Aqui fica só o que é
próprio.

> ⚠️ **"Simples" não significa rasa.** É chamada assim apenas por **não** ter
> nomenclatura nem requisitos próprios no CPC (diferente da `peca-especifica`).
> Pode ter densidade igual à de uma peça específica ou de um recurso. **Não presuma
> baixa complexidade** — deixe o `plano-de-respostas` decidir.

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

## 3. Estrutura do documento
- **Livre, guiada pelo comando** (não há forma imposta pelo CPC). Costuma ser mais
  atrelada a **fatos**.
- Ainda assim use o endereçamento e as boas práticas da `peca-processual-base`.
- Subsegmentável conforme o `plano-de-respostas`.

## 4. Plano de respostas (segmentação)
- **Depende do conteúdo, como as demais.** Manifestação simples → 1 geração;
  manifestação densa (várias questões, muitos fatos) → N gerações. Não force 1.

## 5. Pesquisa (via peca-processual-base → pesquisa-juridica)
- **Sob demanda:** só acione quando a manifestação tiver conteúdo de mérito
  jurídico. Muitas peças simples são só fáticas e dispensam pesquisa.
- Quando houver mérito, mesmas regras (filtros R2, nunca inventar R3, rastro).

## 6. Escrita
`escrita-juridica`, registro `peça`. Saída no formato `@tag` (vira `.docx`).

## 7. Entrega
Output externo → `formatacao-entrega` (`.docx`/timbrado), salvo no workspace.

## 8. Verificação
`verificacao-citacoes` **antes de fechar** — se houver qualquer citação de
lei/jurisprudência/autos.

## 9. Regras de ouro / vícios a evitar
- **Responder exatamente ao comando** — nem menos (deixar pedido do juízo sem
  resposta) nem divagar além do que foi pedido.
- Não presumir simplicidade: dimensionar o esforço pelo conteúdo real, via plano.
