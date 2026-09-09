# Prática Jurídica Work

Variante OpenAI 0.1.0, derivada de `pratica-juridica` 1.2.0, revisão
`2b16ab2cd00b8e5774e9e3a2aba1c47eb229f711`. Preserva 15 skills, extração seletiva
de PDFs PJe e geração de DOCX no padrão da casa. As instruções foram adaptadas
para Astra; o pacote não seleciona o modelo nem instala conectores.

## Uso

Descreva o objetivo e forneça os autos ou o arquivo relevante. Exemplo: “Analise
estes autos e prepare um memorial a partir da apelação, destacando a questão já
deduzida sobre prova documental.” A skill de entrada é `analise-processual`.
Skills específicas também podem ser usadas diretamente.

No ChatGPT, selecione a skill pelo menu `@`; no Codex, pelo seletor ou `$`.
O nome visível depende do namespace mostrado na instalação. Fontes:
[skills](https://learn.chatgpt.com/docs/build-skills) e
[empacotamento](https://developers.openai.com/plugins/build/plugins).

## Instalação e limites de portabilidade

O pacote contém `.codex-plugin/plugin.json`, formato de compatibilidade ainda
suportado, e `skills/`. Pode ser integrado a um marketplace local ou de repositório
pelo criador de plugins do ambiente. Forneça a pasta deste plugin ao `plugin-creator`
e peça a instalação no marketplace desejado. Teste em uma nova conversa.

Esta entrega não altera seu marketplace pessoal nem instala o plugin. O ZIP é uma
cópia transportável do pacote; não pressupõe que toda tela de importação de skill
aceite um plugin completo. Um fluxo de criação de skill individual recebe uma pasta
de skill; um fluxo de plugin precisa da estrutura de pacote e do catálogo pertinente.
Disponibilidade de marketplace local varia entre desktop e superfícies de nuvem.

ChatGPT Work deve receber os arquivos e ter as ferramentas necessárias disponíveis
naquela sessão. Instalação no Codex local não comprova instalação no Work remoto.
O suporte documentado ao formato não comprova execução ponta a ponta na sua conta.

## Dependências

Python 3.10+ com `pypdfium2` para PDFs e `python-docx` para DOCX. Descubra os runtimes
do ambiente antes de instalar dependências. Sem Python, as instruções de análise
podem ser usadas com leitores disponíveis, mas os scripts não executam.
`juris_br` e Know-How Jurídico são conexões externas a configurar e verificar na
sessão; este pacote não contém credenciais, `.mcp.json` ativo ou IDs de apps.

Aquisição automática no PJe depende de navegador e sessão autenticada disponíveis.
Sem acesso, forneça o PDF. O timbre gráfico ainda depende de implementação e asset;
o conversor preserva margens e tipografia, não insere uma imagem de timbre.

## Dados e citações

Execute os scripts fora da pasta do plugin. `PRATICA_JURIDICA_DATA` é a raiz explícita
dos dados; sem ela, usa-se `dados-juridicos` no diretório de trabalho. A pasta por
processo usa CNJ com 20 dígitos; a validação é sintática, sem cálculo do dígito verificador.
Não há busca em pastas ancestrais ou redirecionamento silencioso de saída.
Confirme persistência/exportação conforme o ambiente real.

`@citacao-ref` usa arquivo explícito, SHA-256 e atribuição. Consulte
[o contrato de fontes](skills/formatacao-entrega/references/fontes.md).
A captura precisa vir da ferramenta ou arquivo original; o hash não certifica
autenticidade. A verificação jurídica continua obrigatória. A sintaxe antiga por
processo/transcript não é aceita. Dados do caso e documentos gerados não devem
ser versionados junto ao plugin.

No Work em nuvem, a execução ocorre no ambiente do serviço; não se promete
processamento no computador do usuário. Scripts deste pacote não enviam arquivos
pela rede, mas a conversa e os conectores seguem o ambiente em que forem usados.
