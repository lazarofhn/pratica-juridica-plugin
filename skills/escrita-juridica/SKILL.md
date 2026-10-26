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
| N1 | GO-1 a GO-6 e o radar ao fechar; protocolar não infla, as `references/` ficam de fora (salvo revisão). |
| N2 | Tudo o que segue, geração a geração, por você; na peça, os dois revisores ao fim (`plano-de-respostas`, Passo 5). |
| N3 | Você redige a peça inteira a partir dos dossiês dos tópicos; na costura, radar e varreduras na peça inteira; depois, os dois revisores. |
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
medida em que, razão pela qual. Entre parágrafos: com efeito, além disso, por sua vez,
nessa linha, desse modo, em consequência, diante disso, daí resulta.

> ✗ "O contrato venceu em março. A ré continuou prestando o serviço. A cobrança é devida."
> ✓ "Embora o contrato tenha vencido em março, a ré continuou prestando o serviço, de
> modo que a cobrança é devida."

- **A abertura do parágrafo faz a ligação.** Abra com o que amarra ao parágrafo anterior:
  o conectivo da relação lógica ("Diante disso,", "Ainda que se admitisse,"), uma
  circunstância ("Quanto ao dolo,", "Na premissa adotada pelo acórdão,") ou a retomada da
  ideia anterior ("Essa omissão", "Tal registro"). Sujeito nominal seco abrindo o
  parágrafo ("O MPF", "O acórdão", "A sentença") é exceção: no máximo cerca de 30% dos
  parágrafos e nunca mais de dois seguidos. É vício recorrente do modelo, com ou sem esta
  skill: confira no radar antes de entregar.
- **O capítulo também se liga:** abre situando-se no argumento e retomando o anterior, e
  fecha com a conclusão que conduz ao próximo (a micro-conclusão dos padrões da casa).
- **Ligar não é metalinguagem.** A transição que diz a relação entre as ideias ("Diante
  dessa omissão, a multa perde a base") é obrigatória, e o parágrafo de síntese que
  costura capítulos fica. Corta-se só o texto comentando a si mesmo ("passa-se a
  demonstrar", "como se verá") e a repetição pura.

> ✗ Três parágrafos seguidos: "O MPF imputou dolo…" / "O acórdão manteve…" / "A
> sindicância não apurou…"
> ✓ "Na denúncia, o MPF imputou dolo…" / "Ainda assim, o acórdão manteve…" / "Essa
> conclusão ignora a sindicância, que não apurou…"

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
  não o número; os números só apontam onde olhar: média de 70 a 90 palavras por parágrafo
  na peça e 120 como referência de teto (125 ou 130 cabem se a ideia pede). Duas ideias
  no mesmo bloco: ache a costura lógica e quebre.
- **Quebrar não é resumir nem picotar (inviolável):** nada se corta; o desenvolvimento
  inteiro fica, distribuído em parágrafos encadeados pelo GO-1, como escada de degraus
  curtos. Parágrafos de uma frase em série, sem ligação, são o vício oposto ao bloco
  denso, e a média abaixo de 70 palavras costuma denunciá-lo.
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

## Latim e cortesia forense — calibragem, não proibição
O problema é o excesso e a repetição. Um "Exmo.", um "egrégio" ou um "data venia" de vez
em quando, sem repetição, é natural no registro forense; latim técnico insubstituível
(habeas corpus, erga omnes, data maxima venia em momento solene) é sempre livre. Combata
a saturação: adjetivação bajulatória a cada frase ("ínclito magistrado", "brilhante
decisão") e latim ornamental constante ("in casu", "a priori" o tempo todo).

## Precisão e ancoragem
- **Termo exato, sem variação elegante:** repita o termo técnico; sinônimo usado só para
  não repetir gera ambiguidade. Nunca "o mesmo"/"a mesma" como pronome ("o contrato foi
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
- **Nenhuma transcrição órfã:** ementa, artigo, cláusula ou documento transcrito recebe
  leitura dirigida (padrão 1 de `references/padroes-da-casa.md`).

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
A reescrita de estilo é de quem redige, com o texto à vista. Um subagente Sonnet pode
servir de radar de estilo (opcional; em peça longa, uma seção por agente): localiza e
devolve trecho e linha, nunca reescreve. A exceção é a `sensibilidade-argumentativa`,
que reorganiza a peça inteira pelo peso, em arquivo novo, e só é adotada depois da sua
conferência: nenhum fato, citação, folha ou pedido perdido, e nenhuma frase de tese com
o sentido mudado. Sugestão automática já inverteu o sentido de frase nuclear da tese
("nenhum provedor dispõe de meio" → "provedor dispõe de meio").

## Pendente
- Âncoras reais dos registros `interno` e `externo` (o `peça` já tem as da casa).
