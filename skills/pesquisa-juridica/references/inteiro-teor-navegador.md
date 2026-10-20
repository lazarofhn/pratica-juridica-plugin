# Inteiro teor antigo do STJ pelo navegador

Quando usar: o precedente é decisivo (ex.: o voto do repetitivo) e foi publicado antes da
cobertura do `stj_inteiro_teor`, que então devolve só a URL do PDF. Confira a data de
início da cobertura na descrição da ferramenta; ela muda.

1. **Abra a URL pelo navegador (Claude in Chrome), na sessão do José.** A verificação
   automática do STJ passa sozinha ali; `curl` e cliente HTTP caem no desafio.
2. **Confira a data.** O mesmo número de registro tem vários documentos por data de
   publicação (acórdão principal × embargos de declaração): escolha o que corresponde ao
   julgado citado.
3. **Baixe.** O botão de download do visualizador de PDF salva direto na pasta
   Downloads.
4. **Converta para texto dentro do workspace** (o caminho de `processo.py workspace
   <cnj>`), por exemplo `pdftotext -layout -enc UTF-8 <arquivo.pdf> <workspace>/<nome>.md`
   se o Poppler estiver instalado.
5. **Cite como documento do workspace**, pelo `@citacao-ref` de leitura dos autos (sintaxe
   na `formatacao-entrega`), e registre no `pesquisas.jsonl` a URL, a data de publicação e
   o arquivo gerado, para a `verificacao-citacoes` conferir.
