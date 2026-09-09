---
name: verificacao-citacoes
description: Confere afirmações jurídicas, transcrições, dados processuais, valores e datas contra fontes identificadas e registra pendências.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.

# Verificar o documento
Inventarie afirmações verificáveis no rascunho, incluindo jurisprudência, legislação,
doutrina, dados dos autos, números e datas. Confira contra as fontes efetivamente
lidas, buscando também incompatibilidades com a tese. Conhecimento do modelo e
resumo da conversa não são prova da verificação.

Para jurisprudência, abra o documento associado ao ID e ao registro da pesquisa.
Confira identidade e decisão específica, não só o número do processo. Leia inteiro
teor para afirmar ratio de precedente decisivo. Se só houver ementa, declare esse
alcance. Verifique atualização conforme o tema. Não imponha repetir a mesma busca
sem necessidade: mudança de ranking não invalida uma fonte salva e autenticada.

Para lei, confira texto oficial, vigência e versão aplicável aos fatos; para doutrina,
obra, edição, localização e contexto. Para autos, compare evento, páginas, partes,
documento e versão do PDF. Para prazos, confira marco de intimação, regra de contagem
e calendário aplicáveis antes de concluir tempestividade. Não invente dado ausente.

O [contrato de fontes](../formatacao-entrega/references/fontes.md) permite conferir
integridade e recorte literal. Isso não dispensa verificar origem e aderência jurídica.
Não aceite um resultado automático como auditoria completa da tese.

Grave `verificacao.md` com afirmação/localização, fonte e veredito: conferido,
pendente ou divergente, explicando a correção ou limite. Corrija ou retire alegações
sem suporte quando isso preservar o objetivo. Se a lacuna atingir premissa essencial,
entregue apenas minuta identificada como pendente e destaque o ponto ao usuário.
A decisão do usuário sobre o risco não transforma fonte inexistente em verificada.
Não rotule como pronto para protocolo documento com pendência material.
