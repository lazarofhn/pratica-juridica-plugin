---
name: memorial
description: (camada D) Produz MEMORIAL — peça híbrida entregue ao(s) julgador(es) com o processo pendente de julgamento (1º grau ou instância recursal). Resume as alegações e fundamentos da peça-base em julgamento (inicial, recurso…), com ênfase nos precedentes decisivos. REGRA DE OURO: não inova a argumentação — pode mudar a ênfase, mas não introduz ratio que não esteja nos autos. Skill fina que puxa (em parte) a camada E.
---

# Memorial (camada D)

Skill de output fina. Puxa **parcialmente** a `peca-processual-base` (endereçamento
ao julgador, boas práticas, método de pesquisa) — mas tem **estrutura e regra
próprias**, porque não é uma peça de estrutura livre nem uma protocolada comum.

## 1. Quando ativar
Processo **pendente de julgamento** e o usuário quer entregar um memorial ao(s)
julgador(es) (juízo de 1º grau às vésperas da sentença, ou relator/turma/câmara na
instância recursal).

## 2. Perguntas antes de começar
- **Qual a peça-base em julgamento** que o memorial resume (petição inicial,
  contestação, o recurso em julgamento…)? O memorial é sempre atrelado a ela.
- Alguma **ênfase estratégica diferente** da peça original (mudar o peso dos
  argumentos é permitido; introduzir argumento novo não — ver Regra de ouro).

## 3. Estrutura do documento
- **Endereçamento** ao julgador (relator/juízo), via `peca-processual-base`.
- **Síntese** das alegações e fundamentos da peça-base, organizada por eixo
  argumentativo, com **destaque aos precedentes decisivos** para o caso.
- Fecho pedindo o julgamento no sentido defendido.
- Enxuto: memorial é resumo persuasivo, não repetição integral da peça.

## 4. Plano de respostas (segmentação)
- Por **eixo argumentativo** já constante dos autos. Costuma ser mais enxuto que a
  peça-base; segmente só se houver muitos eixos densos.

## 5. Pesquisa (via peca-processual-base → pesquisa-juridica)
- **Reaproveita a fundamentação já nos autos.** A pesquisa aqui serve para
  **reforçar os precedentes decisivos** das teses **já sustentadas** — não para
  achar teses novas.
- Filtros (R2), nunca inventar (R3), rastro em `pesquisas.jsonl`.

## 6. Escrita
`escrita-juridica`, registro `peça` (persuasivo, dirigido ao julgador), enxuto.
Saída no formato `@tag` (vira `.docx`).

## 7. Entrega
Output externo → `formatacao-entrega` (`.docx`/timbrado), salvo no workspace.

## 8. Verificação
`verificacao-citacoes` **antes de fechar**, com **checagem especial**: confirmar que
**nenhum argumento/ratio está fora dos autos** — todo eixo do memorial deve ter
correspondência na peça-base ou no que já foi debatido no processo.

## 9. Regra de ouro
- **O memorial NÃO inova a argumentação.** É legítimo **mudar a ênfase** (dar mais
  peso a um argumento, menos a outro), mas é proibido **introduzir uma ratio nova**
  que não esteja nos autos. Reforçar precedentes de uma tese já sustentada = ok;
  criar tese não deduzida = não.
