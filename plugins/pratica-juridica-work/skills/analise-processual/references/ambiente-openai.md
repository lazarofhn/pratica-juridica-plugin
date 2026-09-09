# Contrato de ambiente

As instruções do usuário definem escopo e preferências, respeitadas as permissões
e regras do ambiente. Aplique este contrato também quando uma skill for usada
diretamente. O guia de construção da variante Claude não governa esta variante.

Execute até concluir o pedido autorizado. Aproveite respostas já dadas e não crie
aprovações por tamanho de texto, número de seções ou troca de skill. Pergunte por
parte representada, objetivo ou escolha material apenas quando não puder inferir
com segurança dos autos e do contexto. Se o usuário pediu revisão por etapas,
respeite os checkpoints combinados. Elaboração não equivale a autorização para
protocolar, assinar, enviar mensagem ou alterar sistemas externos.

## Ferramentas e arquivos
Descubra recursos pela capacidade e pelo esquema exposto na sessão. Não presuma
`Bash`, `Read`, `Write`, extensão Claude, navegador autenticado, ferramentas MCP
ou colaboração nativa disponíveis. Use as instruções de acesso fornecidas pelo
ambiente; referências a outras skills deste pacote são relativas à pasta `skills`.
Leia só as dependências relevantes e evite recursão no roteamento.

Resolva scripts e assets a partir da localização desta instalação, sem depender
de variáveis de raiz de plugin. Escreva dados em workspace autorizado, fora do
cache do plugin. Use o interpretador disponível; se existir ferramenta de descoberta
de dependências, consulte-a antes de instalar pacotes. Sem execução de código,
produza o conteúdo possível e declare o artefato técnico pendente.

No Codex local, os arquivos graváveis podem estar no computador do usuário. No Work,
podem estar em ambiente isolado. Verifique o que a sessão realmente expõe; não suponha
acesso a `C:\Users`, `/sessions`, `/mnt/data`, Word ou Downloads. Não traduza caminhos
host/container por adivinhação. Use links de artefato aceitos pelo ambiente.

Informe se os dados precisam ser exportados para retomada. Caminho gravável, variável
de ambiente ou arquivo salvo não comprovam persistência após o encerramento. Antes
de concluir tarefa longa, disponibilize documento, fontes e estado necessários à retomada,
respeitando o escopo e o sigilo. Não adicione dados de processos ao repositório do plugin.

## Conectores, fontes e modelos
Conectores instalados em uma conta não são automaticamente transferidos pelo pacote.
Verifique disponibilidade com leitura antes de depender de `juris_br` ou Know-How.
Sem fonte necessária, declare a lacuna e trabalhe nas partes independentes; não invente
resultados ou dispense conferência. Documentos internos não devem ser enviados a outro
provedor sem autorização específica. A execução na nuvem não é processamento local
no computador do usuário; não prometa isso.

Este pacote não seleciona nem troca o modelo da conversa. As instruções foram
preparadas tendo Astra como alvo, mas não dependem de um identificador de API.
Subagentes só entram se autorizados, disponíveis e úteis em subtarefas independentes.
Sem colaboração, execute sequencialmente. Não crie novas tarefas do usuário para
simular subagentes. Compartilhe apenas o contexto necessário e integre evidências.

## Verificação proporcional
Confirme leitura, identidade da fonte, fatos e coerência jurídica. Testes de software
validam os mecanismos, não a correção jurídica de uma peça. Quando uma pendência
impedir conclusão essencial, identifique a minuta como pendente e diga exatamente
o que falta; não apresente conclusão sem fonte como verificada.
