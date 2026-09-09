---
name: peca-especifica
description: Redige contestação, réplica, impugnação e embargos à execução ou de terceiro. Embargos de declaração seguem peca-recurso.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.


# Peça: Específica (camada D)

Skill de output fina. O comum às peças protocoladas está em `peca-processual-base`
(endereçamento, estrutura, método de pesquisa) — **puxe-a**. Aqui fica só o que é
próprio de cada peça específica.

## 1. Quando ativar
Peça com **previsão e nomenclatura próprias no CPC**, cuja dica vem do prompt do
usuário: contestação, réplica, impugnação ao cumprimento de sentença, embargos à
execução, embargos de terceiro, exceção de pré-executividade, reconvenção, etc.

> ⚠️ **Embargos de declaração NÃO entram aqui** — é recurso → `peca-recurso`. Aqui
> só cabem embargos que são incidentes/ações (à execução, de terceiro).

## 2. Informações necessárias, aproveitar o contexto antes de perguntar
- Confirmar **qual peça** quando o prompt for ambíguo (a nomenclatura costuma
  identificar; na dúvida, pergunte).
- Confirmar o marco processual (prazo/intimação) que autoriza a peça.

## 3. Estrutura do documento
- **Localize a previsão da peça no CPC** e leia seus **requisitos/pressupostos
  próprios** (via `peca-processual-base` / Know-How) — não de memória (R1). Cada
  peça tem sua estrutura (ex.: contestação organiza-se por preliminares + mérito
  rebatendo cada causa de pedir da inicial + resposta a eventual tutela + pedidos;
  impugnação ao cumprimento, pelas matérias que a lei admite).
- Subsegmentável conforme o `plano-de-respostas`.

## 4. Plano de respostas (segmentação)
- Tende a **N gerações**: uma por causa de pedir a rebater / matéria arguida /
  preliminar relevante.
- **Sem** a ênfase-padrão de admissibilidade dos recursos — mas respeite os
  **requisitos próprios** da peça (não confundir).

## 5. Pesquisa (via peca-processual-base → pesquisa-juridica)
- `mérito` — segmentada por causa de pedir / matéria.
- `processual` — para as preliminares/requisitos próprios; **jurisprudência
  processual só quando o usuário enfatizar** a questão processual ou ela for muito
  discutida (caso contrário, CPC comentado + doutrina bastam).
- Filtros (R2); nunca inventar (R3); rastro em `pesquisas.jsonl`.

## 6. Escrita
`escrita-juridica`, registro `peça`. Saída no formato `@tag` (vira `.docx`).

## 7. Entrega
Output externo → `formatacao-entrega` (`.docx`; timbre depende de asset fornecido), salvo no workspace.

## 8. Verificação
`verificacao-citacoes` **antes de fechar** (obrigatória).

## 9. Regras de ouro / vícios a evitar
- **Identificar a peça e sua previsão específica corretas** — inclusive não tratar
  embargos de declaração como peça específica.
- Endereçar cada preliminar/matéria à sua base legal própria.
- Coerência: se é resposta (contestação/impugnação), rebater **cada** ponto da peça
  adversa, sem deixar causa de pedir sem enfrentamento.
