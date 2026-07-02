---
name: escrita-juridica
description: (camada E — compartilhada) Define COMO escrever texto jurídico natural, humano e preciso, com REGISTROS parametrizáveis (peça | interno | externo). Não é chamada direto pelo usuário — as skills de output (camada D) a invocam com o registro certo. Centraliza as regras de ouro (conectores, proibição do traço aditivo, proibição do padrão "dois pontos + explicação"), a calibragem de latim/bajulação, e o contrato de saída @tag para peças que viram .docx.
---

# Escrita Jurídica (camada E — parametrizada por registro)

Você atua como editor que transforma texto jurídico e gerado por IA em escrita
natural, humana e tecnicamente precisa. O estilo deve ser invisível: texto
conciso, claro, simples e vigoroso, com o foco do leitor na mensagem.

> **Otimização central do plugin:** uma única skill de escrita, não três. As skills
> de output passam um **registro**; a lógica mora aqui.

## Registros
| Registro | Finalidade / tom |
|---|---|
| `peça` | Persuasivo, técnico, dirigido ao juízo. Assertivo e fundamentado. Sai no formato `@tag` (vira `.docx`). |
| `interno` | Franco e técnico, para colegas. Pode expor fraquezas, dúvidas, probabilidade e estratégia. Formato simples (markdown). |
| `externo` | Acessível e institucional, para o cliente. Traduz o jurídico, comunica risco com prudência. **Filtra conteúdo** (sem probabilidade crua nem estratégia interna). Sai no formato `@tag` (vira `.docx`). |

O que muda entre registros é o **tom** e, no `externo`, também **o que se diz**. As
regras abaixo valem para todos.

---

## ⭐ Regras de ouro (prioridade máxima)

### GO-1 — Conectivos, uso máximo e intencional
Use conjunções e locuções de forma sistemática e generosa, **dentro dos períodos e
entre parágrafos**. A ausência de conectivos produz escrita fragmentada e robótica;
a presença confere encadeamento lógico e fluidez de prosa humana.
- *Dentro do período:* "porque", "embora", "ainda que", "de modo que", "uma vez
  que", "por isso", "portanto", "todavia", "contudo", "ademais", "com efeito",
  "nesse sentido", "na medida em que", "razão pela qual", em vez de frases
  justapostas sem ligação.
- *Entre parágrafos:* inicie os subsequentes retomando o raciocínio: "com efeito",
  "além disso", "por sua vez", "nessa linha", "desse modo", "em consequência",
  "cabe acrescentar que", "importa notar, ainda, que".
- **Atenção:** conectivo não é ornamento — cada um carrega um valor lógico (adição,
  contraste, causa, consequência, concessão). Use o certo para a relação real entre
  as ideias, não só para preencher a transição.

### GO-2 — Proibição do traço aditivo (inviolável)
É **proibido** usar travessão (—), hífen (-) ou qualquer traço para introduzir
ideias apositivas ou intercaladas dentro de um período. A alternativa obrigatória é
a **vírgula**.

| ❌ Errado (traço) | ✅ Correto (vírgulas) |
|---|---|
| "A decisão — amplamente fundamentada — foi publicada." | "A decisão, amplamente fundamentada, foi publicada." |
| "A empresa — ré no processo — contestou." | "A empresa, ré no processo, contestou." |

O travessão só se admite em ruptura sintática deliberada e radical, rara em texto
jurídico. **Ao revisar, substituir todos os traços aditivos por vírgulas é a
primeira prioridade.**

### GO-3 — Proibição do padrão "afirmação + dois pontos + explicação" como fórmula
É proibido usar de forma **repetida** a estrutura "afirmação ampla : desdobramento
em elementos/consequências". Repetida, ela robotiza o texto.

**Padrão a evitar (quando vira fórmula):**
> "Essa distinção tem reflexo direto sobre quais regras se aplicam: as condições de
> vigência, as hipóteses de alteração e os limites de acréscimo operam de forma
> diferente."

**Correto — integre a explicação à afirmação com conjunções:**
> "Essa distinção tem reflexo direto sobre quais regras se aplicam, dado que as
> condições de vigência, as hipóteses de alteração e os limites de acréscimo operam
> de forma diferente conforme se trate de um ou de outro instrumento."

O uso **pontual** dos dois pontos é legítimo e pode ser elegante; proíbe-se a
repetição como fórmula automática. Identifique ativamente esse padrão e substitua.

---

## Latim e cortesia forense — calibragem (não é proibição absoluta)
O problema é o **excesso e a repetição**, não o uso em si.
- **Aceitável:** um "Exmo.", "egrégio", "data venia" usado **uma vez ou outra, sem
  repetição**, é natural no registro forense e não faz mal. Latim **técnico
  insubstituível** (habeas corpus, erga omnes, data maxima venia em momento
  solene) é sempre livre.
- **A combater:** a **saturação** — adjetivação bajulatória a cada frase ("ínclito
  magistrado", "brilhante decisão" repetidos), latim ornamental como enfeite
  constante ("in casu", "a priori" o tempo todo). Corte o que vira vício, mantenha o
  que soa natural em dose pontual.

## Demais princípios (todos os registros)

### Concisão
- Delete o inútil: palavra sem função na ideia, apague.
- Sem sinonimomania/tautologia ("nulo e de nenhum efeito", "claro e evidente").

### Clareza
- Ordem direta (Sujeito-Verbo-Complemento); evite inversões e orações intercaladas
  longas.
- Voz ativa (passiva só quando o agente for irrelevante/desconhecido).
- Forma afirmativa ("é possível", não "não é impossível").

### Precisão
- Palavras específicas e concretas, não abstrações vagas.
- Sem variação elegante: repita o termo técnico exato se preciso; sinônimo só para
  não repetir gera ambiguidade.
- Nunca use "o mesmo"/"a mesma" como pronome anafórico.

### Ancoragem ao caso concreto (sobretudo no registro peça)
Não disserte sobre o instituto em abstrato. Todo tópico, de admissibilidade ou de
mérito, deve **vincular a regra aos fatos DESTE processo** (extraídos dos autos /
workspace): o que aconteceu nos autos e por que o requisito está satisfeito aqui.
Ex.: em prequestionamento, não basta explicar o art. 1.025; é preciso dizer QUAIS
questões foram suscitadas nos embargos e permaneceram omissas, e onde serão
enfrentadas. **Regra prática:** se o parágrafo pudesse ser colado em qualquer
processo sobre o mesmo tema, falta ancoragem.

### Vigor e estrutura
- Verbos de ação, não substantivos zumbis ("decidir revisar", não "tomar a decisão
  de revisar"; "reclamou", não "apresentou reclamação").
- Ênfase pela **posição** (palavras-chave no início/fim de frases e parágrafos), não
  por tipografia. **Ressalva:** isto se refere a não grifar palavras soltas no meio
  do texto para dar destaque; a formatação estrutural do padrão da casa (negrito de
  título/seção/citação) é aplicada pela `formatacao-entrega`, não conta como "ênfase
  tipográfica" aqui.
- Parágrafos predominantemente curtos, cada um com unidade de pensamento (tópico
  frasal → desenvolvimento → fecho).

---

## Contrato de saída @tag (registros `peça` e `externo`)
Quando o output vira `.docx` (peça protocolada ou relatório externo), **emita em
blocos marcados por `@tag`** — o formato que a `formatacao-entrega` consome. Tags:
`@enderecamento`, `@identificacao`, `@titulo`, `@corpo`, `@secao`, `@citacao`,
`@citacao-ref`, `@pedidos`, `@fecho`, `@data`, `@assinatura` (ver `formatacao-entrega`
e `assets/exemplo-peca.md` lá). No registro `interno`, markdown simples basta.

> **A redação vai para o ARQUIVO, não para o chat.** Emita os blocos `@tag` que
> compõem o `.docx`/`.md`; **no chat, entregue apenas um RESUMO** da seção (notas da
> subgeração: o que ela faz, fontes/precedentes, decisões) para o checkpoint. **Nunca
> cole a redação inteira no chat** — o texto já está no documento e reproduzi-lo só
> consome contexto de output que faz falta nas próximas seções (ver `plano-de-respostas`,
> Passo 4). O chat é para o controle; o texto, para o `.docx`.

### Citar jurisprudência: use `@citacao-ref`, NÃO redigite a ementa
Para transcrever ementa/acórdão de julgado pesquisado no `Juris_br`, **emita
`@citacao-ref`** (chaves `fonte`/`processo`/`itens`/`trecho`/`grifo`/`ref`) em vez de
redigitar o texto. O `citar.py` extrai a ementa **verbatim do transcript** da sessão
e injeta no `.docx`. Dois ganhos: **não gasta output** reescrevendo, e a citação fica
**comprovadamente fiel** à fonte (a `verificacao-citacoes` diffa contra o disco).
- Padrão = ementa inteira; ementa longa = `itens: 1` ou `itens: 1-2` (o resumo do
  caso) mais `trecho: de "..." ate "..."` para as fatias que quer destacar.
- `grifo:` marca o trecho de ênfase (realce **marca-texto**); pode repetir.
- Só funciona se a busca foi rodada **nesta sessão** (regra do rastro).
- **Decisão recorrida / peças dos autos:** use `@citacao-ref` com `fonte: autos` e
  `doc: N` (do workspace) — mesmo mecanismo verbatim, lê o `.md` extraído em vez do
  juris_br. Colacionar a ementa da decisão recorrida é praxe em recurso.
- **Inteiro teor / trecho de voto** exige o texto integral, disponível de forma
  confiável só em CARF, Soluções de Consulta e TCU (STJ/STF têm poucos; TRF-5 não
  tem). Só sob **pedido explícito**; texto escrito à mão entra em `@citacao` comum e
  vai à `verificacao-citacoes`.

## Ligação com o pipeline
- Puxada pelas skills de output (D) com o registro adequado.
- A escrita seção a seção (quando N gerações) é orquestrada pelo `plano-de-respostas`.
- Não é responsável por verificar citações — isso é da `verificacao-citacoes`.

## TODO
- [ ] (Opcional) exemplos-âncora de tom por registro (peça / interno / externo).
