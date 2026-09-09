---
name: obter-processo
description: Obtém autos no sistema judicial com navegador autorizado ou trabalha com PDF fornecido, verificando processo, cobertura e download.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.

# Obter autos
Use o navegador ou conector disponível na sessão e leia sua documentação antes de
operá-lo. O plugin não instala navegador nem transfere sessões autenticadas.
Sem esse acesso, solicite o PDF e prossiga no trabalho independente possível.

Confira número CNJ, tribunal e grau atual a partir do pedido e dos dados observados.
O órgão de origem no CNJ não determina sozinho a instância de tramitação atual.
Leia [referências PJe](references/pje.md) apenas para PJe; são pistas históricas,
não comprovação do layout atual. Localize controles pela interface observada.

Login, senha, token e certificado ficam a cargo do usuário. Se a sessão expirar,
peça que autentique e retome. Trate confirmações pelo mecanismo oficial da ferramenta;
não sobrescreva `window.confirm` ou aceite indiscriminadamente avisos judiciais.
Se a ferramenta não controlar o diálogo, peça a intervenção necessária.

Baixe conforme o escopo autorizado, preservando índice/bookmarks. Use a ordenação
pedida; se ausente, crescente. Antes de aplicar recorte que exclua documentos
solicitados, esclareça o escopo. Aguarde evidência da conclusão da geração do PDF.
Verifique caminho, tamanho e identificação se houver acesso ao download. Caso só
o navegador local do usuário receba o arquivo, diga que falta acesso ao PDF e peça
que o disponibilize; não afirme ter analisado o download.

Entregue identificação do processo, cobertura e arquivo acessível quando disponível.
Continue a análise ou peça se isso já integrar o pedido. Aquisição não autoriza
peticionar, assinar, alterar cadastro ou enviar documentos a terceiros.
