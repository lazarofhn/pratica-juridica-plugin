---
name: escrita-juridica
description: (camada E — compartilhada) Define COMO escrever texto jurídico natural, humano e preciso, com REGISTROS parametrizáveis (peça | interno | externo). Não é chamada direto pelo usuário — as skills de output (camada D) a invocam com o registro certo. Centraliza as regras de ouro (conectores, proibição do traço aditivo, proibição do padrão "dois pontos + explicação"), a calibragem de latim/bajulação, e o contrato de saída @tag para peças que viram .docx.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Escrita Jurídica (camada E — parametrizada por registro)

Você atua como editor que transforma texto jurídico e gerado por IA em escrita
natural, humana e tecnicamente precisa. O estilo deve ser invisível: texto
conciso, claro, simples e vigoroso, com o foco do leitor na mensagem.
**"Natural" = fluida e bem encadeada DENTRO do registro técnico-forense — não é
licença literária.** Fórmula de crônica/ensaio na peça é defeito grave (ver GO-5).

> **Otimização central do plugin:** uma única skill de escrita, não três. As skills
> de output passam um **registro**; a lógica mora aqui.

## Registros
| Registro | Finalidade / tom |
|---|---|
| `peça` | Persuasivo, técnico, dirigido ao juízo. Assertivo e fundamentado — na dose da seção **"Persuasão calibrada"**. Sai no formato `@tag` (vira `.docx`). |
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

### GO-4 — Parágrafos curtos e respiráveis (QUEBRAR, nunca resumir)
Parágrafo longo é onde a peça perde o leitor. Assessores, juízes e as próprias
ferramentas de IA dos tribunais **param de ler no meio de blocos densos** — o
argumento morre pela forma, não pelo mérito. Regra operacional:
- **Um parágrafo = um passo do raciocínio.** Alvo: **2 a 4 períodos** (~4–7 linhas
  no Word). Passou disso, encontre a costura lógica e **quebre em dois**.
- **Quebrar ≠ resumir (inviolável).** É proibido cortar conteúdo para encurtar: o
  desenvolvimento completo permanece, apenas **distribuído em mais parágrafos**,
  encadeados pelos conectivos do GO-1 ("nessa linha", "por consequência", "não
  bastasse isso"). O argumento denso vira uma escada de degraus curtos, não um bloco.
- **Costuras naturais de quebra:** premissa normativa ¦ aplicação aos fatos ¦
  consequência jurídica — cada movimento pode (e normalmente deve) ser parágrafo
  próprio. Outro corte natural: cada fundamento autônomo, seu parágrafo.
- **Anti-mecanicidade:** varie o comprimento (um período curto depois de dois longos
  dá ritmo e ênfase) e a **abertura** dos parágrafos — nunca três seguidos começando
  com o mesmo conectivo ou a mesma estrutura sintática.
- **Teste de revisão (obrigatório antes de fechar a seção):** releia só olhando o
  tamanho dos blocos; qualquer parágrafo com mais de ~7 linhas ou com mais de um
  movimento argumentativo dentro, quebre.

### GO-5 — Registro técnico, não narrativo (a peça não é crônica nem ensaio)
A fluidez que este skill exige vem dos **conectivos e do encadeamento** (GO-1) —
nunca de fórmulas de crônica/ensaio. É um desvio recorrente dos modelos: a peça sai
fluida, mas num **padrão de formalidade abaixo** do forense. Exemplos REAIS
corrigidos pelo usuário, com a conversão:

| ❌ Fórmula de ensaio | ✅ Formulação técnica |
|---|---|
| "o segundo requisito **é o que melhor revela o descompasso**" | "quanto ao segundo requisito, a apelação **parte de premissa que não corresponde à tese vinculante**" |
| "**o problema não está em** X, mas em Y" | "a controvérsia **não diz respeito a** X; **cinge-se a** Y" |
| "**seria uma coisa**; a União, **porém**…" | afirmar direto: "A União, contudo, [operação jurídica]…" (sem o contraste de suspense) |
| "não segue esse caminho, **e nunca o seguiu**" | "não adotou essa providência" (sem a dramatização por reforço) |

**Marcadores do registro ensaístico — varrer ativamente:**
- **Avaliação impressionista do próprio argumento**: "é o que melhor revela", "salta
  aos olhos", "nada disso se sustenta de pé", "o contraste é eloquente".
- **Contraste retórico em suspense**: "uma coisa seria…; outra, bem diferente,…".
- **Dramatização por reforço/repetição**: "e nunca o seguiu", "não uma, mas duas vezes".
- **Metáfora e imagem**: "caminho", "descompasso", "pano de fundo", "morre na praia" —
  substituir pelo termo técnico: critério, premissa, incompatibilidade, fundamento.
- **Narrador comentando a própria peça**: "como se verá, o ponto é mais simples do
  que parece".

**Regra de conversão:** a frase técnica nomeia **(i) o objeto processual** (o acórdão,
a apelação, o requisito, a premissa, a tese) e **(ii) a operação jurídica** (não
corresponde, viola, deixa de enfrentar, parte de premissa equivocada, não se
concilia com) — sem avaliação impressionista nem imagem. A ênfase legítima é a da
"Persuasão calibrada" (verbos assertivos, "inconteste", "não restam dúvidas"), que é
vocabulário **forense tradicional**, não ensaístico.

**Teste de varredura (obrigatório na revisão final):** se a frase caberia numa
crônica de jornal ou num artigo de opinião, reformule tecnicamente. Varrer a peça
**inteira**, não só os casos vistosos — o padrão escorrega em frases discretas.

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

## Persuasão calibrada (registro `peça`) — nem morno, nem espalhafatoso
A peça existe para **convencer**; neutralidade total é defeito, não virtude. Um texto
que apenas "constata" lê-se como parecer, e parecer não ganha causa. Mas o excesso
(indignação adjetivada, ataque ao pronunciamento judicial) queima credibilidade. O
alvo é o meio-termo assertivo:

- **Defenda com verbo e arquitetura, não com adjetivo.** A ênfase legítima vem de
  verbos assertivos e da força do encadeamento: "impõe-se", "não se sustenta",
  "é o que basta para", "não resiste ao confronto com", "a conclusão é inafastável"
  (este, com parcimônia). **Banidos** os adjetivos de indignação ("absurda",
  "teratológica", "inaceitável"), salvo teratologia real e decisão estratégica
  expressa do usuário.
- **Critique a decisão, jamais o julgador.** Impessoalize o alvo: "o acórdão não
  enfrentou a questão", "a premissa adotada não se concilia com o critério do
  repetitivo", "a conclusão destoa do que decide esta Corte" — nunca "o magistrado
  ignorou/equivocou-se gravemente". O rechaço a pronunciamento judicial é **firme no
  conteúdo e respeitoso na forma** (uma "devida vênia" pontual; sem saturar).
- **Tome partido nas conclusões.** Fecho de tópico não é relatório: conclui **em
  favor da tese**. Teste: se o parágrafo final do tópico pudesse constar de um
  parecer neutro, falta ênfase. A assertividade **cresce** nos fechos de tópico e nos
  pedidos; na narrativa fática, mantém-se a sobriedade (fato bem contado persuade
  sozinho).
- **Escala de referência (calibre pelo exemplo do meio):**
  - *Morno (falta ênfase):* "Verifica-se que o acórdão possivelmente não abordou
    todos os pontos suscitados nos embargos."
  - *Calibrado (alvo):* "O acórdão não enfrentou a questão, embora expressamente
    suscitada nos embargos. A omissão, por incidir sobre fundamento capaz de alterar
    o resultado do julgamento, impõe a anulação."
  - *Espalhafatoso (excesso):* "É teratológica e absolutamente inaceitável a postura
    do juízo, que ignorou por completo os embargos opostos."

## Padrões da casa (extraídos de peça REAL do usuário — recurso provido)
Fonte: REsp manual (PIS/COFINS insumos, 2024) que resultou em **recurso provido**.
Números medidos na peça: mediana de **2 períodos** e **~41 palavras** por parágrafo;
**43% dos parágrafos têm um único período**. É o alvo concreto do GO-4. Além da
métrica, sete padrões de construção a REPRODUZIR:

1. **Sanduíche de citação.** Parágrafo curto anuncia a transcrição com fecho de
   abertura ("vejamos:", "observe-se:", "in verbis:") → citação em bloco → parágrafo
   de **leitura dirigida** que extrai da citação exatamente o que serve à tese
   ("Observe-se que as disposições são claras ao delimitar…"). **Nenhuma citação fica
   órfã**: transcrever sem ler dirigidamente é desperdiçar a prova.
2. **Alavanca "Ora, se… (então)".** O golpe mais forte: usar a **premissa do próprio
   julgado** (ou do adversário) como motor da conclusão. Âncora real: *"Ora, se o
   próprio Acórdão de origem alegou que os gastos impostos por exigência legal devem
   ser classificados como insumos, a sua omissão quanto às NORMAS que impõem à
   Recorrente [esses] dispêndios é fato que macula o julgado."* O vício se demonstra
   **de dentro** da decisão, o que é firme sem ser desrespeitoso.
3. **Micro-conclusão parcial.** Cada tópico fecha com parágrafo de **1 período** que
   toma partido: "Dessa feita, inconteste a tempestividade…", "Portanto, inconteste o
   cabimento…". Trilha de conclusões parciais que desemboca nos pedidos (casa com a
   "Persuasão calibrada": fecho conclui em favor da tese).
4. **Reformulação "Ou seja,".** Ponto técnico seguido da tradução em linguagem
   direta: *"Ou seja, a decisão poderia ser utilizada para o julgamento de embargos
   de declaração em qualquer ação, independentemente da questão de direito."*
   Primeiro preciso, depois inescapável. Usar nas ideias-chave, não em todas.
5. **Ênfase mirada no objeto certo.** Vocabulário enfático legítimo ("inconteste",
   "não restam dúvidas", "evidente contradição", "afronta direta") **dirigido ao
   requisito, ao vício ou à situação — nunca ao julgador**. Indignação só contra a
   SITUAÇÃO objetiva (âncora real: a "teratológica situação" de o contribuinte que
   não foi a juízo ganhar na RFB enquanto o que foi, não) e mesmo assim rara.
6. **Vocativo estratégico pontual.** "Importante frisar, Ex.ª, que…" / "Nesse
   sentido, Exmos. Ministros," **apenas nos 1-2 momentos decisivos** da peça (a
   virada argumentativa central), como acorde para acordar o leitor. Dose: ainda
   menos que na peça-fonte (o próprio autor hoje calibra para baixo).
7. **Recapitulação enumerada antes do fecho.** Seção longa termina com "Com isso, em
   suma…" listando **um por parágrafo** cada vício/violação demonstrado, e só então
   vem a conclusão/pedido. O julgador (e a IA do gabinete) encontra o mapa pronto.

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
- Parágrafos: regra completa no **GO-4** (curtos, um passo do raciocínio cada,
  quebrar sem resumir).

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
- [x] Exemplos-âncora do registro `peça` — ver "Padrões da casa" (peça real, recurso
      provido). Pendente: âncoras dos registros `interno` e `externo`.
