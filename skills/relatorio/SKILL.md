---
name: relatorio
description: Redige relatório sobre o processo, interno para o escritório (franco, com riscos, chance qualitativa e estratégia, inclusive antes de decidir a peça) ou externo para o cliente, que filtra estratégia e chance. Não use para peça processual nem para parecer sem processo.
---

# Relatório (interno | externo)

Informa sobre o processo ou planeja a estratégia; não é peça (sem endereçamento,
admissibilidade nem pedidos). Nível típico: N2, com plano curto de uma geração; N3 no
relatório estratégico detalhado. Chamada fora do pipeline, assuma N2.

## 1. Precondições e perguntas
- **Workspace em dia.** Antes de relatar a situação atual, compare a data do documento
  mais recente extraído com o andamento de agora (conectores de andamento ou
  `obter-processo` em modo consulta, como no `analise-processual`). Se houve movimento
  depois, atualize os autos ou relate com a data de corte expressa.
- Pergunte só o que o pedido não disser: o destinatário (escritório ou cliente), porque
  muda o conteúdo e não só o tom; na estratégia, o foco e, se ela antecede uma peça, o
  objetivo final.

## 2. Estrutura
Situação atual → o que está em jogo → [só no interno: riscos, chance, estratégia] →
próximos passos. Segmente por processo ou por questão-chave se cobrir vários.

**Interno com foco em estratégia:** situação atual → questões-chave → cenários e riscos →
recomendação → próximos passos.
- Chance de êxito qualitativa (alta, razoável, baixa, remota), sempre com a base
  declarada: o precedente, o fato dos autos ou o óbice que a sustenta. Nunca percentual.
- Pesquisa sob demanda, quando a chance ou a recomendação dependem de uma tese
  (viabilidade de recurso, chance de tutela); é ela a base declarada.
- **N3:** risco e recomendação passam pelo conselheiro Fable (advisor, se ligado; senão,
  subagente Fable com dossiê); você decide.
- Fase prévia de uma peça: grave em `<workspace>/estrategia.md`; o plano da peça parte das
  decisões dele (ex.: o eixo do REsp, na `peca-recurso`).

## 3. Regras de ouro
- **Externo nunca omite** situação negativa, mas a equilibra com o caminho de solução que
  de fato existe nos autos ou no plano do escritório.
- **Externo filtra conteúdo**, não só o tom: sem chance de êxito nem estratégia interna;
  risco comunicado com prudência; lei e jurisprudência ficam nos bastidores.
- **Externo só afirma o que está nos autos ou no `plano.md`.** Providência ainda não
  tomada entra como próximo passo, não como feito.
  - ❌ "A decisão foi desfavorável, mas já preparamos o recurso, com tema de repercussão
    geral favorável." (nada disso consta dos autos nem do plano)
  - ✅ "A sentença julgou o pedido improcedente. Ainda cabe apelação, no prazo que termina
    em [data], e nela o tribunal pode rever o fundamento que levou à improcedência."
- **Interno é franco:** descrição direta, sem verniz de cliente, também sobre fraquezas e
  riscos; o objetivo é decidir bem, não convencer.

## 4. Escrita, entrega e verificação
- Externo: registro `externo` da `escrita-juridica` e `.docx` pela `formatacao-entrega`,
  só com as `@tag` que cabem (`@titulo`, `@secao`, `@corpo`, `@data`, `@assinatura`).
- Interno: registro `interno`, em markdown no workspace, sem `.docx`.
- `verificacao-citacoes` sempre que o relatório afirmar algo que dependa de fonte (lei,
  jurisprudência, dados dos autos).
