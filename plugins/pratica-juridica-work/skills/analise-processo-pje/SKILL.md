---
name: analise-processo-pje
description: Extrai e lê documentos de PDFs processuais grandes usando o índice PJe, com cobertura documentada e leitura integral dos documentos decisivos.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.

# Análise de autos em PDF
O script [processo.py](scripts/processo.py) usa Python e `pypdfium2`.
Resolva seu caminho a partir desta skill instalada. Descubra o interpretador e
as dependências disponíveis; evite reinstalar pacotes existentes.

```text
python processo.py workspace <numero-cnj>
python processo.py index <pdf> --json
python processo.py peek <pdf> --docs 0,2 --chars 400
python processo.py extract <pdf> --docs 0,2 --out <workspace>
python processo.py find <pdf> --id <evento>
```

Execute a partir de uma pasta de trabalho gravável, fora do pacote instalado.
`PRATICA_JURIDICA_DATA` define a raiz explícita; na ausência, o script usa
`./dados-juridicos`. O diretório é `processos/<CNJ-normalizado>` nessa raiz.
A existência da pasta não comprova persistência entre sessões do Work.

Leia o índice e selecione documentos pelo objetivo, incluindo provas contrárias
e anexos determinantes. `seq` começa em zero. Use `peek` para triagem, nunca como
prova suficiente. Informe a cobertura planejada nos trabalhos extensos, sem criar
uma aprovação obrigatória para leitura já autorizada. Extraia os documentos e leia
cada documento decisivo integralmente, em lotes contínuos se necessário. Registre
eventos e páginas lidos; siga referências cruzadas relevantes com `find`.

Antes de reaproveitar um workspace, compare o PDF com o insumo anterior por hash
e registre a versão. Não use arquivos antigos como se fossem autos atualizados.
Para relatório completo, cubra todas as peças e anexos relevantes; declare qualquer
exclusão. Para peça pontual, concentre-se na decisão, manifestações e prova do tema.

Se não houver bookmarks, o índice vazio não significa autos vazios: use sumário
visível e extração por páginas com ferramenta disponível. Para páginas escaneadas,
use OCR disponível e confira visualmente passagens decisivas. Não há comando `ocr`
neste script. Rotule texto de OCR e registre páginas ilegíveis ou não examinadas.

Delegação é opcional, apenas se autorizada no ambiente e útil para triagem ou lotes
independentes. Mantenha o modelo selecionado; não imponha substitutos por nome.
O responsável pela conclusão deve ler os documentos que sustentam a tese; resumo
de subagente não substitui a leitura das passagens e do contexto relevantes.
