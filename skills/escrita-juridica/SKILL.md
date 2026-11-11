---
name: escrita-juridica
description: Estilo jurídico da casa (peça, interno, externo); redige pelas regras de ouro, revisa peça pronta, remove juridiquês e dá fluidez. Não use para redigir peça a partir dos autos (comece pelo analise-processual), pesquisar fundamento ou gerar o .docx.
---

# Escrita jurídica

Dona única do estilo do plugin. O estilo deve ser invisível, e "natural" é fluido e bem
encadeado **dentro** do registro técnico-forense, não licença literária (fórmula de
crônica ou ensaio na peça é defeito grave, GO-5). Entra no pipeline, com o registro
passado pela skill de saída ou pelo `plano-de-respostas`, ou direto, para revisar peça
pronta, remover juridiquês ou dar fluidez (`references/revisao.md`). Fora do pipeline,
assuma N2 e o registro pelo destinatário: juízo → peça; escritório → interno; cliente →
externo.

| Nível | O que muda aqui |
|---|---|
| N1 | GO-1 a GO-8 e o radar ao fechar; protocolar não infla, as `references/` ficam de fora (salvo revisão). |
| N2 | Tudo o que segue, geração a geração, por você; na peça, os dois revisores ao fim (`plano-de-respostas`, Passo 5). |
| N3 | Você redige a peça inteira a partir dos dossiês dos tópicos; na costura, radar e varreduras na peça inteira; depois, os dois revisores. Em teste: o `redator` redige por esta skill, a partir do seu esqueleto (`plano-de-respostas`). |
| N4 | O principal da equipe redige por esta skill, com os mesmos revisores do N3. |

## Registros
| Registro | Para quem e com que tom | Saída |
|---|---|---|
| `peça` | Juízo. Persuasivo, técnico, assertivo e fundamentado, na dose de `references/persuasao.md`. | blocos `@tag` → `.docx` |
| `interno` | Colegas. Franco e técnico: pode expor fraqueza, dúvida, probabilidade e estratégia. | markdown |
| `externo` | Cliente. Acessível e institucional; traduz o jurídico e comunica risco com prudência. **Filtra conteúdo:** sem probabilidade crua nem estratégia interna. | blocos `@tag` → `.docx` |

Entre registros muda o tom e, no `externo`, também o que se diz; as regras valem para os três.

## A redação vai para o arquivo, não para o chat
- Cada geração vai direto para o arquivo (`@tag` no `peça` e no `externo`, markdown no
  `interno`); no chat, só as notas: o que a seção faz, fontes, decisões. Nunca recole a
  redação: repeti-la gasta o output que falta às próximas seções.
- Sintaxe de `@tag` e `@citacao-ref`: `formatacao-entrega`. Ementa e trecho dos autos
  entram por `@citacao-ref` (texto verbatim, sem redigitar); `@citacao` escrito à mão vai
  à `verificacao-citacoes`. Trecho de voto exige inteiro teor: onde há, ver
  `pesquisa-juridica`.

## Antes da forma: o peso decide (registro peça)
As regras de ouro cuidam da forma. Antes delas vem o juízo que a forma não supre: quanto
cada argumento pesa no convencimento do julgador. É o peso que decide se o argumento
entra, onde entra, quanto espaço recebe e em que posição aparece, inclusive dentro do
mesmo tópico; o tamanho do parágrafo vem depois.
- **Teste:** se o julgador não ler este argumento, fato ou resposta, o que acontece com o
  resultado? Cai → núcleo; fica mais difícil → apoio; nada muda → sai ou vira uma oração.
- **Tópico é o caminho até um resultado,** não uma tese: reúne tudo de que o julgador
  precisa para chegar lá, ainda que sejam matérias distintas. Subtópico só para etapa de
  núcleo, porque subtópico dá importância: argumento fraco em subtópico próprio é
  promovido.
- **Dentro do tópico, a ordem do peso:** conclusão, fato decisivo com a prova, condição
  que estende ou limita o resultado, objeção relevante, fecho.
- **Espaço proporcional ao peso.** Fato que se prova por documento se mostra (data,
  folha, imagem), não se argumenta; resposta longa a objeção fraca promove a objeção.
- **Revisão:** de cada parágrafo, pergunte se a decisão mudaria caso o julgador o pulasse.

O mapa de peso nasce no plano (`plano-de-respostas`, Passo 1); a objeção já levantada
pelo adversário e os exemplos estão em `references/persuasao.md`. Com a peça pronta, a
`sensibilidade-argumentativa` revisa a construção e o `moderador-final` lê como o
julgador (`plano-de-respostas`, Passo 5).

## Regras de ouro (prioridade máxima)

### GO-1 — Conectivos e ligação: cada parágrafo nasce do anterior
Encadeie com conjunções e locuções, no período e entre parágrafos: sem elas o texto fica
fragmentado e robótico. Cada conectivo tem um valor lógico (adição, contraste, causa,
consequência, concessão); use o da relação real, não o que só preenche a transição. No
período: porque, embora, ainda que, de modo que, uma vez que, portanto, todavia, na
medida em que, razão pela qual. Entre parágrafos: ademais, além disso, portanto, assim,
por isso, contudo, todavia, diante disso, em consequência, por sua vez, nessa linha.

> ✗ "O contrato venceu em março. A ré continuou prestando o serviço. A cobrança é devida."
> ✓ "Embora o contrato tenha vencido em março, a ré continuou prestando o serviço, de
> modo que a cobrança é devida."

- **A conjunção abre o parágrafo.** Na maioria das vezes, o parágrafo abre pela conjunção
  ou locução da relação lógica com o anterior ("Ademais,", "Portanto,", "Todavia,",
  "Diante disso,", "Ainda que se admitisse,"), anteposta ou logo depois do primeiro termo
  ("A ordem postulada, contudo,"; "Impõe-se, assim,"); também serve uma circunstância
  ("Quanto ao dolo,", "Na premissa adotada pelo acórdão,"). Sujeito nominal abrindo o
  parágrafo cabe quando nomeia o passo novo do argumento ("O decreto confirmou…", "O art.
  17 vincula…"); o vício é a série de atores sem ligação ("O MPF…" / "O acórdão…" / "A
  sentença…"). No máximo cerca de metade dos parágrafos sem conectivo, nunca três
  seguidos: confira no radar antes de entregar. Depois da conjunção vem a oração:
  conjunção e circunstâncias não se empilham na abertura (GO-8).
- **A remissão fica à vista.** Remeter ao que acabou de ser dito é bem-vindo quando
  constrói a lógica, fazendo disso a premissa do passo seguinte ("Nessa perspectiva, a
  omissão dos Ministérios compõe a causa de pedir"; "O decreto confirmou esse quadro";
  "o ato conjunto… Esse ato conjunto"). O vício é a remissão órfã: "este entendimento",
  "essa lógica", "este tributo" apontando para o que ficou parágrafos atrás, do outro
  lado de um título, ou para mais de um candidato. Aí, repita o termo exato ou nomeie o
  referente na frase ("Essa ratio, que afastou o dano material e o moral, foi
  aplicada…"). A remissão que só repete o que se disse é o vício do GO-7. Ligar é papel
  da conjunção; trocar "O acórdão" por "Esse acórdão" não liga nada.
- **O capítulo abre pela própria tese** (`references/persuasao.md`), não por parágrafo que
  resume o anterior: a ligação entre capítulos vem do título e da conjunção. Fecha, quando
  preciso, com o arremate (GO-7).
- **Ligar não é metalinguagem.** A transição que diz a relação entre as ideias ("Diante
  dessa omissão, a multa perde a base") é obrigatória. Corta-se o texto comentando a si
  mesmo ("passa-se a demonstrar", "como se verá") e a repetição (GO-7).

> ✗ Três parágrafos seguidos: "O MPF imputou dolo…" / "O acórdão manteve…" / "A
> sindicância não apurou…"
> ✓ "Na denúncia, o MPF imputou dolo…" / "Ainda assim, o acórdão manteve…" / "Todavia,
> a sindicância não apurou…"

> ✗ "Este tributo, contudo, não alcança a receita…" (o IRPJ foi nomeado três parágrafos
> antes, e no meio vieram a CSLL e a COFINS)
> ✓ "O IRPJ, contudo, não alcança a receita…"

### GO-2 — Proibição do traço aditivo (inviolável)
Travessão, meia-risca ou hífen nunca introduzem ideia apositiva ou intercalada no
período; a alternativa obrigatória é a vírgula. O travessão só cabe em ruptura sintática
deliberada e radical, rara em texto jurídico.

> ✗ "A decisão — amplamente fundamentada — foi publicada."
> ✓ "A decisão, amplamente fundamentada, foi publicada."

### GO-3 — Dois pontos não viram fórmula
É proibida a repetição de "afirmação ampla + dois pontos + desdobramento": repetida,
robotiza o texto. O uso pontual é legítimo e pode ser elegante; integre a explicação à
afirmação com conjunção.

> ✗ "Essa distinção tem reflexo direto sobre quais regras se aplicam: as condições de
> vigência, as hipóteses de alteração e os limites de acréscimo operam de forma diferente."
> ✓ "Essa distinção tem reflexo direto sobre quais regras se aplicam, dado que as
> condições de vigência, as hipóteses de alteração e os limites de acréscimo operam de
> forma diferente conforme se trate de um ou de outro instrumento."

### GO-4 — Parágrafos curtos e respiráveis (quebrar, nunca resumir)
Assessores, juízes e as ferramentas de IA dos tribunais param de ler no meio de bloco
denso: o argumento morre pela forma, não pelo mérito.
- **Um parágrafo, uma ideia:** normalmente um ou dois períodos curtos. A régua é a ideia,
  não o número; os números só apontam onde olhar: média de 45 a 65 palavras por parágrafo
  na peça (as versões definitivas do José de out. e nov./2026 dão 49 e 51) e 120 como
  referência de teto (125 ou 130 cabem se a ideia pede). A média é consequência, nunca
  meta: não se alonga parágrafo para chegar a ela. Duas ideias no mesmo bloco: ache a
  costura lógica e quebre.
- **Quebrar não é resumir nem picotar (inviolável):** ao quebrar um bloco, nenhum
  argumento se perde; o desenvolvimento inteiro fica, distribuído em parágrafos
  encadeados pelo GO-1, como escada de degraus curtos (o que sai é só a repetição, pelo
  GO-7). Parágrafos de uma frase em série, sem conjunção que os ligue, são o vício oposto
  ao bloco denso.
- **Costuras naturais:** premissa normativa ¦ aplicação aos fatos ¦ consequência
  jurídica; cada fundamento autônomo, seu parágrafo.
- **Anti-mecanicidade:** varie o comprimento (um período curto depois de dois longos dá
  ênfase) e a abertura; nunca três parágrafos seguidos com o mesmo conectivo ou a mesma
  estrutura.
- **Radar:** o `lint_peca.py` mostra a média da peça e aponta os parágrafos acima da
  referência (`references/revisao.md`); quem decide se é uma ideia só é a leitura.

> ✗ Um bloco de nove linhas que transcreve o art. 1.022, narra a omissão e conclui.
> ✓ Três parágrafos: o que o art. 1.022 exige; o que o acórdão não enfrentou; por que a
> omissão impõe a anulação.

### GO-5 — Registro técnico, não narrativo (a peça não é crônica nem ensaio)
A fluidez vem dos conectivos e do encadeamento, nunca de fórmula de crônica ou ensaio.
É desvio recorrente dos modelos: a peça sai fluida, mas um degrau abaixo da formalidade
forense. Exemplo real corrigido pelo José (os demais em `references/revisao.md`):

> ✗ "o segundo requisito **é o que melhor revela o descompasso**"
> ✓ "quanto ao segundo requisito, a apelação **parte de premissa que não corresponde à
> tese vinculante**"

Marcadores: avaliação impressionista do próprio argumento ("salta aos olhos", "nada
disso se sustenta de pé", "o contraste é eloquente"); contraste em suspense ("uma coisa
seria…; outra, bem diferente,…"); dramatização por reforço ("e nunca o seguiu", "não
uma, mas duas vezes"); metáfora e imagem ("caminho", "descompasso", "pano de fundo",
"morre na praia") no lugar de critério, premissa, incompatibilidade, fundamento; e o
narrador comentando a peça, seja no comentário estilístico ("como se verá, o ponto é
mais simples do que parece"), seja, mais grave, no **metadiscurso estratégico**, que
revela a arquitetura da tese ("este argumento é subsidiário", "o que se admite apenas
para argumentar", "o fundamento principal, contudo, é outro") ou conta que a estratégia
mudou. A peça mostra o resultado, nunca a elaboração; moldura de subsidiariedade
sinaliza fragilidade que não existe.

**Regra de conversão:** a frase técnica nomeia o **objeto processual** (o acórdão, a
apelação, o requisito, a premissa, a tese) e a **operação jurídica** (não corresponde,
viola, deixa de enfrentar, parte de premissa equivocada, não se concilia com), sem
avaliação impressionista nem imagem. A ênfase legítima ("inconteste", "não restam
dúvidas") é vocabulário forense tradicional, não ensaístico (`references/persuasao.md`).

### GO-6 — Definição por negação (afirme direto; negue só quem existe nos autos)
Para afirmar algo, não é preciso dizer o que ele "não é": a negação gratuita inventa um
adversário só para dar relevo à afirmação.

> ✗ "a usina **não é projeto anunciado**, mas empreendimento regularmente outorgado"
> ✓ "a usina **é empreendimento regularmente outorgado** e em operação comercial há mais
> de uma década"

**Teste de triagem:** alguém nos autos sustentou o que estou negando? **Sim** → negação
legítima (refutar tese da parte contrária, afastar precedente invocado, responder a
fundamento da decisão recorrida): fica. **Não** → converta em afirmação direta. A regra
não proíbe negar; sem o teste, a réplica e as contrarrazões morrem.

### GO-7 — Dizer uma vez (a citação fala por si)
O que a citação, o grifo ou a frase anterior já disseram não volta com outras palavras. É
o que mais engorda a peça: na manifestação revisada pelo José (nov./2026), a prosa caiu
42% (de 57 para 38 parágrafos) e as citações ficaram quase todas.
- **Em volta da citação, só o que ela não mostra.** Antes, uma frase: o ponto que ela
  prova ou o que ela não traz, como quem decidiu e por que o caso é igual ("O STJ já
  enfrentou a questão em caso oriundo deste eg. TRF-5: réus condenados solidariamente,
  parte deles sem apelar:"). Dentro, o grifo no trecho decisivo, que é a leitura
  dirigida. Depois, a aplicação ao caso ("Esse é o caso dos autos, uma vez que…") ou o
  arremate que conclui o raciocínio, sem explicar o precedente; ou nada. Nunca o
  parágrafo que reconta o julgado ("No REsp X, o STJ decidiu que…, porque entendeu…").
- **O precedente se mostra, não se narra.** O que sustenta o argumento entra apresentado
  numa frase e transcrito em bloco, com o grifo no que decide (na manifestação revisada
  pelo José, 12 transcrições, todas grifadas). Contar na prosa o que o tribunal fez e por
  quê ("o STJ cassou acórdão que…, por reconhecer que…") é paráfrase sem a prova. Na
  prosa, o precedente entra só como corroboração curta ("…, como assentou o STJ (REsp
  X)") ou com o trecho literal entre aspas na própria frase.
- **Transcrever ou parafrasear, não os dois.** Norma ou cláusula transcrita não ganha
  parágrafo que a reexplica; se só um trecho decide, cite-o entre aspas na frase.
- **Decisões contrárias, em conjunto.** As que a parte contrária invoca (sentenças,
  precedentes que ela transcreve) respondem-se num só parágrafo, pelo que as desqualifica
  como bloco: grau, data, o que decidiram em uma linha e os pronunciamentos favoráveis
  (são de primeiro grau e pendem de recurso; os únicos colegiados sobre a matéria são
  favoráveis). Não se transcreve decisão contrária nem se lhe dá apresentação, tópico ou
  parágrafo próprio: o bloco de citação é vitrine do precedente favorável. Se o fundamento
  de uma delas pesa contra o resultado, responde-se ao fundamento, pela prova ou pela lei,
  sem recontar a decisão.
- **A frase que se explica sai:** a que reexplica a anterior ou a citação ("como o próprio
  dispositivo indica…", logo depois de transcrevê-lo); a que só anuncia e deixa a prova
  para o parágrafo seguinte ("Essa consequência já foi ponderada por quem tinha
  competência para fazê-lo." / "Com efeito, …"); a conclusão anunciada na abertura e
  repetida no fim; a que explica ao julgador o que a citação já carrega ("o decreto, cujo
  alcance se restringe ao da lei que executa (CTN, art. 99)" → "(CTN, art. 99)"). "Ou
  seja" só quando acrescenta a consequência (padrão 4).
- **Fato primeiro, fonte no parêntese:** "O voto que instruiu a resolução aprovou a
  outorga da usina…" → "A usina foi outorgada… (Doc. 15, id …)".
- **O parágrafo não carrega a lista de precedentes.** Quantos citar varia com a
  importância da questão: na mais importante, cabe mais de um, inclusive do mesmo
  tribunal. O que não cabe é o texto corrido cheio de remissões (número, órgão, relator e
  data em série no meio do argumento): o que sustenta o ponto vai em bloco, com grifo, e
  os demais do mesmo ponto na linha de referência do bloco ("No mesmo sentido: TRF5, AC
  …, 4ª Turma").

**Teste:** apague a frase ou o parágrafo. O julgador perde algo que a citação, o grifo e
o texto vizinho não lhe dão? Se não perde, sai.

> ✗ [transcrição do art. 18, §§ 1º e 2º, do decreto] + "Disciplinados a política e o
> programa, o regulamento deixou para depois apenas o cadastro… Mais do que isso, o § 1º
> só admite a edição do ato do cadastro depois do ato conjunto do § 2º. Por desenho do
> próprio regulamento, portanto, …"
> ✓ "Ao regulamentar a lei, o decreto deixou para depois apenas o cadastro (art. 18, §
> 1º) e o incentivo tributário (art. 18, § 2º), e subordinou o ato do cadastro, "a ser
> editado após a vigência do ato de que trata o § 2º", a ato conjunto do qual participa o
> Ministério da Fazenda."

### GO-8 — Ordem direta e referente nomeado (o período se lê de uma vez)
O leitor não deve guardar nada na memória para chegar ao verbo, nem voltar ao parágrafo
anterior para saber de quem ou de quê se fala.
- **Ordem direta é a regra:** conjunção, sujeito, verbo, objeto e, por último, o adjunto
  adverbial. Depois da conjunção vem a oração, não uma fila de circunstâncias
  intercaladas. Sair da ordem direta é exceção e pede um objetivo que melhore a leitura:
  a circunstância curta que liga o parágrafo ao anterior (GO-1), o termo levado ao começo
  ou ao fim do período para receber a ênfase, a ambiguidade que a ordem direta criaria.
  Um deslocamento por período, e curto; se você não sabe dizer para que serve, volte à
  ordem direta.
- **Numeral e pronome levam o substantivo.** Numeral, ordinal e pronome no lugar do nome
  ("as duas primeiras", "a segunda", "este", "aquela", "ambos", "os demais", "a outra")
  obrigam o leitor a voltar e contar. Escreva o substantivo e, no lugar da posição em que
  a coisa apareceu no texto, o atributo que a identifica: a data, o grau, o órgão, a
  parte. Sem o substantivo, só quando ele está no mesmo período ("Das três decisões, duas
  são de primeiro grau").
- **Sujeito oculto, só o da oração anterior.** Mudou o sujeito, nomeie o novo.
- **Pronome oblíquo retoma um referente só, e próximo.** Dois oblíquos (-lo, -la, -os,
  lhe) apontando para coisas diferentes no mesmo período travam a leitura: repita o
  substantivo. Repetir o nome não é o vício do GO-7, que corta a ideia dita duas vezes.
- **O período que não cabe na ordem direta se divide** em dois, cada um com o seu sujeito
  e o seu objeto nomeados (GO-4), em vez de se equilibrar com vírgulas.

**Teste:** em cada verbo, o leitor sabe quem pratica a ação e sobre o quê, sem voltar?
Cada "-lo", "este" ou "a segunda" tem um só candidato, e à vista? Se não, nomeie ou
divida.

> ✗ "A autoridade reconheceu o crédito. Todavia, quase dois anos depois, sem nova
> intimação da contribuinte, com fundamento em parecer que não juntou, glosou-o e,
> apresentada a manifestação de inconformidade, deixou de apreciá-la."
> ✓ "A autoridade reconheceu o crédito. Todavia, glosou esse crédito quase dois anos
> depois, sem nova intimação da contribuinte e com fundamento em parecer que não juntou.
> Tampouco apreciou a manifestação de inconformidade."

> ✗ "As duas primeiras são de primeiro grau e pendem de recurso; a última, embora
> colegiada, não examinou o decreto."
> ✓ "As duas decisões mais antigas são de primeiro grau e pendem de recurso; o acórdão
> do TRF-1, embora colegiado, não examinou o decreto."

## Latim e cortesia forense — calibragem, não proibição
O problema é o excesso e a repetição. Um "Exmo.", um "egrégio" ou um "data venia" de vez
em quando, sem repetição, é natural no registro forense; latim técnico insubstituível
(habeas corpus, erga omnes, data maxima venia em momento solene) é sempre livre. Combata
a saturação: adjetivação bajulatória a cada frase ("ínclito magistrado", "brilhante
decisão") e latim ornamental constante ("in casu", "a priori" o tempo todo).

## Precisão e ancoragem
- **Termo exato, sem variação elegante:** repita o termo técnico; sinônimo usado só para
  não repetir gera ambiguidade. Referente distante também se repete, em vez de retomado
  por demonstrativo (GO-1), por numeral ou por pronome solto (GO-8). Nunca "o mesmo"/"a mesma" como pronome ("o contrato foi
  assinado e o mesmo previa multa" → "o contrato foi assinado e previa multa").
- **O léxico não concede a premissa adversária.** Ao relatar ato, decisão ou tese
  contrária, verbo e substantivo não podem admitir por descuido a premissa que se
  combate. Exemplo real: com tese de eficácia plena, escrever que o decreto "reconheceu
  **depender de providência futura a eficácia**" (ou falar em "dever de
  **regulamentação**") trai a tese; o correto é "reconheceu que **ainda não editou** o
  ato". A frase costuma estar correta como relato: o vazamento está no léxico.
- **Léxico da casa:** "ação" ou "demanda", não "impetração" (fora de citação).
- **Ancoragem no caso:** todo tópico, de admissibilidade ou de mérito, vincula a regra
  aos fatos deste processo, tirados do workspace, em vez de dissertar sobre o instituto.
  Em prequestionamento não basta explicar o art. 1.025: diga quais questões foram
  suscitadas nos embargos, quais ficaram omissas e onde serão enfrentadas. Se o
  parágrafo coubesse em qualquer processo sobre o tema, falta ancoragem.
- **Procedência dos autos:** cite tipo do documento, NUM (id ou evento) e páginas, como
  o workspace entrega: "(Certidão de intimação, id 12345678, p. 3)".
- **Toda transcrição tem função:** a frase que a apresenta diz por que ela importa, o
  grifo marca o trecho decisivo e o que vem depois aplica ao caso ou conclui (padrão 1 de
  `references/padroes-da-casa.md`); recontar o que se acabou de transcrever é o vício do
  GO-7.

## Persuasão e padrões da casa (registro peça)
- **Antes de redigir os fundamentos**, leia `references/persuasao.md`: o peso de cada
  argumento e a objeção já levantada pelo adversário, verbo e arquitetura em vez de
  adjetivo, crítica à decisão e nunca ao julgador, tese na abertura do tópico, fecho que
  toma partido, escala de calibragem e antecipação de objeção.
- **Ao redigir tópico com citação, prova documental, fecho ou recapitulação**, siga
  `references/padroes-da-casa.md` (sete padrões da peça real que teve o recurso provido).

## Ao fechar cada geração
1. Rode o radar no arquivo (`--json` para lista estruturada; limiares em `--help`):
   ```
   python "${CLAUDE_PLUGIN_ROOT}/skills/escrita-juridica/scripts/lint_peca.py" <arquivo>
   ```
2. Fora do N1, leia `references/revisao.md` e faça as varreduras de leitura que o
   script não vê.
3. Trie cada alerta pelo teste da regra (se for falso positivo, o texto fica) e
   diagnostique antes de reescrever.

Na costura, o radar roda na peça inteira: aberturas repetidas, a parcela de aberturas
nominais e a saturação só aparecem no conjunto. Depois da revisão argumentativa, rode-o
de novo na versão adotada.

## Revisar peça pronta ou remover juridiquês (chamada direta)
Roteiro em `references/revisao.md`: situar registro e destinatário, rodar o radar,
diagnosticar antes de reescrever e entregar a versão revisada em arquivo novo (o original
não se sobrescreve), com a lista curta das mudanças por regra. Em peça de mérito, a
construção do argumento vem antes da forma: a `sensibilidade-argumentativa` e o
`moderador-final` (`plano-de-respostas`, Passo 5) rodam antes das varreduras de forma.

## Agentes
No N3 e no N4, em teste, quem redige pode ser o agente `redator`: ele recebe só o
esqueleto que você fecha e esta skill, e escreve a peça inteira (`plano-de-respostas`,
`references/esqueleto.md`). As regras são as mesmas; o que muda é quem as aplica.

A reescrita de estilo é de quem redige, com o texto à vista. Um subagente Sonnet pode
servir de radar de estilo (opcional; em peça longa, uma seção por agente): localiza e
devolve trecho e linha, nunca reescreve. O melhor uso dele é a leitura a frio do GO-8 e
da remissão do GO-1: sem ter visto os autos nem o plano, marca cada período que precisou
reler e cada referente que precisou procurar atrás, o que quem redigiu não enxerga,
porque já sabe a resposta. A exceção é a `sensibilidade-argumentativa`,
que reorganiza a peça inteira pelo peso, em arquivo novo, e só é adotada depois da sua
conferência: nenhum fato, citação, folha ou pedido perdido, e nenhuma frase de tese com
o sentido mudado. Sugestão automática já inverteu o sentido de frase nuclear da tese
("nenhum provedor dispõe de meio" → "provedor dispõe de meio").

## Pendente
- Âncoras reais dos registros `interno` e `externo` (o `peça` já tem as da casa).
