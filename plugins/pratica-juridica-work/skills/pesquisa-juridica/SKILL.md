---
name: pesquisa-juridica
description: Pesquisa fundamentos legais, doutrinários e jurisprudenciais com fontes integrais, registro reproduzível e exame de precedentes contrários.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.

# Pesquisa jurídica
Defina a questão e o perfil: admissibilidade, processual ou mérito. Use `juris_br`
e Know-How Jurídico quando disponíveis. Descubra ferramentas pelo nome/capacidade
e confira o esquema atual; nomes e parâmetros históricos são pistas, não contrato
executável. Não dependa de uma skill externa ausente.

## Fontes e método
Leia o dispositivo aplicável em fonte oficial e confira sua redação pertinente ao
período do caso. Use o acervo doutrinário conectado quando a interpretação exigir,
lendo integralmente o capítulo/seção relevante, não apenas o fragmento recuperado.
Se o acervo não estiver disponível, use fontes oficiais permitidas e explicite a
lacuna doutrinária. Em análise limitada a um acervo, respeite esse limite e não
introduza pesquisa externa sem autorização.

Para jurisprudência, combine descrição semântica e termos exatos quando a ferramenta
oferecer ambas as modalidades. Filtros de órgão e data devem servir à questão.
Pesquise entendimento recente e paradigmas históricos, súmulas e temas qualificados
sem corte que os exclua. Amplie filtros se não houver resultado ou aparecer divergência.
No direito federal, inclua o tribunal regional pertinente; CARF, RFB e TCU entram
quando a matéria justificar. Não imponha consulta a todas as bases em toda tarefa.

Leia a ementa completa e o inteiro teor dos precedentes decisivos. Confirme identidade,
órgão, relator, julgamento/publicação, contexto, resultado e aderência ao caso.
Acórdão principal e embargos são documentos distintos mesmo com número de processo
igual. Não escolha automaticamente o texto mais longo. Detalhes podem ser necessários
para resultados truncados; preserve IDs grandes como strings quando exigido pela API.

Registre decisões contrárias e explique distinção, superação comprovada ou risco.
Não descarte precedente apenas por ser desfavorável. Divergência recente, isoladamente,
não comprova superação. Se só houver ementa, limite a afirmação a ela; não atribua
ratio confirmada sem inteiro teor. Falha de acesso e busca sem resultado não provam
inexistência de precedente.

## Registro e citação
Em `pesquisas.jsonl`, registre data, ferramenta, parâmetros exatos, IDs, fontes
selecionadas e descartes relevantes com motivo. Salve respostas e arquivos por
mecanismo determinístico da ferramenta quando disponível. Não suponha acesso aos
históricos privados do produto e não reconstrua uma resposta como se fosse original.

Para transcrições, use o [contrato de fontes](../formatacao-entrega/references/fontes.md).
O pacote lê um arquivo identificado, verifica seu hash e recorta o texto literal.
O hash comprova integridade desde a captura, não autenticidade nem correção jurídica.
Se não houver exportação fiel, faça paráfrase atribuída após leitura e verificação,
ou declare a transcrição pendente; não prometa colagem automática.

Reutilize arquivos conferidos da tarefa; repita buscas somente para resolver lacunas,
conflitos ou atualização. Fonte oficial prevalece sobre metadado do conector.
Conclua com fundamento, evidência, alcance e limitações, usando `verificacao-citacoes`.
