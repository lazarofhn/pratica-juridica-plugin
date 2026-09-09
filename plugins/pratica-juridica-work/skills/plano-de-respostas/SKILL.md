---
name: plano-de-respostas
description: Organiza a redação jurídica por questões e evidências, com segmentação proporcional à complexidade e checkpoints em arquivo.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.

# Plano de redação
Organize as seções a partir do ato solicitado e dos requisitos conferidos na fonte.
Para cada questão substancial, associe fatos, documentos, fundamento, objeção
relevante e consequência pretendida. Evite impor enumeração à prosa final.

Segmente quando a densidade das questões justificar leitura e revisão próprias.
Número de seções, chamadas de ferramenta e turnos de conversa são coisas distintas;
nenhuma quantidade fixa comprova profundidade. Em RE/REsp, dê tratamento específico
aos requisitos de admissibilidade pertinentes, separando-os dos fatos e do mérito,
sem exigir uma resposta do usuário por requisito.

Salve `plano.md` nos trabalhos longos e informe brevemente o encaminhamento.
Prossiga até a entrega autorizada. Se o usuário pedir revisão etapa a etapa,
combine checkpoints editoriais e aguarde nos pontos combinados. Preserve essa
escolha durante toda a tarefa. Uma mudança que altere pedido, parte ou estratégia
de modo material exige esclarecer a intenção; extensão do texto, por si, não.

Em cada bloco, leia os documentos relevantes integralmente, consulte ou reabra
as fontes salvas, redija e revise. Pesquise novamente quando houver lacuna, mudança
temporal ou conflito de evidências. Grave a redação e atualize `estado.md`.
Ao final, revise a coerência entre fatos, fundamentos e pedidos e confira citações.
Se não houver ferramenta de arquivos, entregue no chat no formato pedido e declare
essa limitação; não afirme ter salvo um documento.
