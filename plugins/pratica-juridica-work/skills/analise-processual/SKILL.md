---
name: analise-processual
description: Coordena análise de autos e produção de peças ou relatórios conforme o objetivo jurídico solicitado.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.

# Análise processual
Identifique resultado esperado, parte representada, decisão ou ato relevante e
documentos disponíveis. Aproveite o que já estiver definido. Se faltar informação
essencial, avance nas tarefas independentes e formule uma pergunta objetiva.

## Roteamento
| Objetivo | Skill |
|---|---|
| Entender o processo ou escolher estratégia | `analise-estrategia` |
| Recurso, embargos de declaração ou contrarrazões | `peca-recurso` |
| Contestação, réplica, impugnação, embargos à execução/de terceiro | `peca-especifica` |
| Manifestação, juntada ou cumprimento de despacho | `peca-simples` |
| Memorial para julgamento | `memorial` |
| Relatório ao escritório ou cliente | `relatorio` |

Se o PDF já estiver disponível, use `analise-processo-pje`. Use `obter-processo`
quando o pedido exigir aquisição dos autos. Não descarte anexos relevantes só
porque o índice não os classifica como peças.

Para trabalho substancial, organize `plano-de-respostas`, pesquise as questões
necessárias e aplique a skill de entrega com `escrita-juridica`. Peças usam também
`peca-processual-base`. Uma juntada sem tese dispensa pesquisa e plano formal.
Confira fatos, números e citações antes de concluir; use `verificacao-citacoes`
para registrar evidências e pendências. Gere DOCX com `formatacao-entrega` quando
couber ao pedido. Se o usuário pediu só revisão ou extração, conclua esse escopo.

## Estado e conclusão
Em trabalhos longos, mantenha no workspace `estado.md`, com objetivo, insumos,
documentos lidos, decisões, seções concluídas, fontes e pendências. Atualize após
cada bloco substantivo e retome daí, sem repetir pesquisas já verificadas.
Informe o local dos arquivos e a cobertura efetivamente analisada. Entrega concluída
significa documento produzido e verificações descritas, nunca protocolo judicial.
