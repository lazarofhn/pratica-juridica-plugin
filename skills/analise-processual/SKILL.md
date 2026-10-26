---
name: analise-processual
description: Porta de entrada do pratica-juridica. Avalia a complexidade (N1 a N4) e conduz o trabalho a partir dos autos — recurso, contrarrazões, peça, memorial, relatório ou consulta. Não use para contrato, parecer sem processo ou pesquisa avulsa de jurisprudência.
---

# Análise Processual — orquestrador

Decide o caminho e chama as skills certas, na ordem certa. Não escreve o output final.

## 1. Avaliar a complexidade (primeira regra do pipeline)
**Declare o nível em uma linha antes de ler qualquer documento dos autos.** A única
ferramenta permitida antes é o índice do PDF (`processo.py index`), que mostra o volume e
as páginas escaneadas; sem PDF à mão, classifique só pelo pedido. Exemplo: *"Nível N2
(padrão): manifestação com dois fundamentos; pesquisa focada; sem paradas — diga se quer
subir ou descer."* Se a leitura mudar o quadro, redeclare em uma linha. Não pergunte:
declare e siga; o José ajusta.

| Sinal | N1 simples | N2 padrão | N3 complexo | N4 equipe |
|---|---|---|---|---|
| O que se pede | comunicar ou requerer o rotineiro (juntada, ciência, prazo, resposta a despacho simples) | peça ou relatório com 1 a 3 fundamentos | REsp/RE, apelação ou contrarrazões com várias teses; memorial decisivo; relatório estratégico detalhado | várias frentes ou processos; parecer amplo; tese que precisa ser atacada antes de ir |
| Leitura dos autos | 1 a 3 documentos | seletiva | dezenas de documentos ou autos volumosos | conforme a equipe |
| Pesquisa | nenhuma (só a lei, se citar) | uma linha focada | por tópico: lei, doutrina e jurisprudência | conforme a equipe |

Desempate: entre dois níveis, suba quando houver tese a convencer e desça quando a peça
só comunica. Risco alto (valor, prazo fatal, recurso excepcional) sobe um nível.

O que cada nível aciona:

| | N1 | N2 | N3 | N4 |
|---|---|---|---|---|
| Plano de respostas | não | curto, com o mapa de peso: mostra e segue | mapa de peso e plano aprovados pelo José antes de redigir | o seu, no protocolo da equipe |
| Redação | você, de uma vez | você, geração a geração, sem paradas | você, a partir de um dossiê Opus por tópico | você, a partir do que o operacional da equipe apurou |
| Conselheiro Fable | — | — | nas decisões decisivas | nas decisões decisivas |
| Revisão argumentativa | — | `sensibilidade-argumentativa` e `moderador-final`, este em Opus | os dois, com o moderador em Fable | os dois, com o moderador em Fable |
| Verificação | referências aos autos | `verificacao-citacoes` completa | completa, com subagentes | verificador da equipe |

- **N4:** proponha `/equipe-juridica:iniciar` e espere o ok; não abra a equipe sozinho.
- Paradas tópico a tópico só quando o José pedir ("revisar tópico a tópico").

## 2. Agentes e modelos
Delegue triagem e volume; o juízo e a redação ficam com você: escolha de tese, mapa de
peso, coerência final, veredito sobre a ratio de um precedente, o que dizer ao cliente.
Uma só mão escreve a peça; os revisores opinam e você decide.

- **Haiku** — mecânico: localizar documentos no índice, inventário de citações, conferir
  números, datas, IDs e referências "id N / fls.", varreduras de padrão no texto.
- **Sonnet** — ler e triar documentos extraídos; rodar buscas de jurisprudência e
  sintetizar; primeira revisão de estilo.
- **Opus** — dossiê de tópico no N3, a `sensibilidade-argumentativa` (reorganiza a peça
  pelo peso) e conferência de ratio.
- **Fable** — conselheiro nas decisões decisivas de N3/N4 quando a sessão principal não
  for Fable: cabimento e eixo do recurso, escolha e ordem das teses, risco num relatório,
  conflito entre precedentes.
  - Com o advisor ligado (`/advisor fable` na aba Code), consulte o advisor antes de
    decidir: ele vê a conversa inteira.
  - Sem advisor (ex.: Cowork), abra um subagente com `model: fable` e mande um dossiê
    curto: a pergunta, as opções, os fatos e os precedentes com IDs.
  - Em qualquer caso, você decide e registra a decisão no `plano.md`.
  - O `moderador-final`, que lê a peça pronta como o julgador, roda em Fable no N3 e no
    N4 (no N2, em Opus), qualquer que seja o modelo da sessão principal.

Subagentes nativos rodam no próprio Claude: o texto dos autos não sai para outro
provedor. Se o ambiente não oferecer subagentes, faça você mesmo, em passos separados.

## 3. Rotear

| Pedido | Skill |
|---|---|
| Recurso — inclusive embargos de declaração, apelação, agravo, REsp/RE — e contrarrazões | `peca-recurso` |
| Peça com previsão própria no CPC: contestação, réplica, impugnação ao cumprimento de sentença, embargos à execução ou de terceiro; também a exceção de pré-executividade | `peca-especifica` |
| Manifestação sem previsão própria no CPC, guiada pelo comando (do José ou do despacho) | `peca-simples` |
| Memorial (processo pendente de julgamento) | `memorial` |
| Relatório ou estratégia — para o escritório (interno) ou para o cliente (externo) | `relatorio` |
| Pergunta pontual sobre os autos ou localizar um documento | `analise-processo-pje` (N1) |
| Revisar uma peça já escrita | `escrita-juridica` (revisão; em peça de mérito, com a `sensibilidade-argumentativa` e o `moderador-final`) + `verificacao-citacoes` |
| Andamento atual do processo | conectores de andamento disponíveis (ex.: Legal One, DataJud/DJEN) antes do navegador; `obter-processo` em modo consulta |

- Embargos de declaração são recurso (`peca-recurso`); embargos à execução ou de
  terceiro são ação (`peca-especifica`).
- Peça que nasce sem autos (inicial, mandado de segurança, ação anulatória, cumprimento
  de sentença) ainda não tem rota própria: avise o José e use a estrutura legal da peça
  com `escrita-juridica` e `pesquisa-juridica`.
- Pedido ambíguo: pergunte só o que os autos não respondem.

## 4. Garantir os autos
- Padrão: o José aponta o PDF da íntegra.
- Sem PDF: `obter-processo` baixa pelo navegador (PJe TRF-1 e TRF-5; login e
  certificado são sempre do José).
- Resolva o workspace com `processo.py workspace <cnj>` (`analise-processo-pje`) e
  reaproveite o que já foi extraído. Se o script avisar que a pasta é temporária, diga
  isso ao José em uma linha: a pasta fixa vem da variável `PRATICA_JURIDICA_DATA`.

## 5. Ler seletivamente
Chame `analise-processo-pje` com o objetivo e o nível já definidos: ele decide o que
extrair e lê a fundo só isso. Nunca carregue o processo inteiro no contexto. Se o índice
mostrar parte relevante sem texto (escaneada), a `analise-processo-pje` diz quando usar o
conector busca-autos; no N3/N4, a indexação começa já, em segundo plano.

## 6. Planejar e produzir
- **N1:** vá direto à skill de saída.
- **N2 e N3:** `plano-de-respostas` (mapa de peso, segmentação, aprovação e dossiês por
  tópico no N3, revisão argumentativa ao fim).
- A skill de saída puxa `pesquisa-juridica` e `escrita-juridica`, entrega o `.docx` por
  `formatacao-entrega` e fecha com `verificacao-citacoes`.
