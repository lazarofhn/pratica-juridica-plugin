# Adiciona variante Prática Jurídica para ChatGPT Work e Codex

O plugin dependia de comandos, caminhos e históricos de conversa do Claude.
Esta mudança adiciona uma variante OpenAI autocontida com 15 skills adaptadas
para Astra, preservando os arquivos operacionais da versão Claude.

O fluxo passa a concluir o escopo autorizado com checkpoints em arquivo, mantendo
aprovações editoriais quando solicitadas. Scripts usam workspace explícito e
citações por arquivo, SHA-256 e atribuição, em substituição à busca em transcripts.
Rascunhos antigos com `@citacao-ref` por número de processo precisam ser migrados
conforme o contrato de fontes da variante.

Validação: manifesto e 15 skills aprovados nos validadores oficiais; 11 testes
locais aprovados, com PDF e fontes sintéticos, DOCX, recortes e integridade.
Instalação e execução ponta a ponta no ChatGPT Work, conectores autenticados,
navegação PJe e inspeção visual do DOCX ainda exigem homologação.

Consulte `docs/ADAPTACAO-OPENAI.md` para constatações, organização das variantes
e critérios de homologação. Este arquivo é uma descrição preparada para revisão;
não representa um pull request publicado.
