# Revisão — método, varreduras e roteiro de peça pronta

Leia ao fechar cada geração, depois de rodar o `lint_peca.py`, e sempre que o pedido for
revisar peça pronta, remover juridiquês ou dar fluidez a um texto.

## Método
1. **Diagnostique antes de reescrever.** Separe o que peca na frase: (i) a estrutura
   lógica, (ii) o registro ou o vocabulário, (iii) o conteúdo jurídico. Se só o vocábulo
   peca, troque o vocábulo e **preserve a arquitetura**: não se joga fora um bom
   argumento por defeito que era só de léxico.
2. **Agente auxiliar é radar, nunca revisor.** O script e o subagente Sonnet localizam
   ocorrências; a reescrita é sempre de quem redige, com o texto à vista. Sugestão
   automática já inverteu o sentido jurídico de frase nuclear da tese ("nenhum provedor
   dispõe de meio" → "provedor dispõe de meio").
3. **O radar é amostra.** Falso positivo é aceitável e a ausência de alerta não prova
   qualidade; as varreduras marcadas *leitura* o script não vê.

## O radar
```
python "${CLAUDE_PLUGIN_ROOT}/skills/escrita-juridica/scripts/lint_peca.py" <arquivo|pasta>
    [--json] [--max-palavras 120] [--limite-palavras 130] [--max-periodos 2]
    [--media 45-65] [--aberturas 3] [--max-abertura-nominal 50]
    [--max-nominais-seguidas 2] [--max-cortesia 2] [--ignorar GO-6,cortesia]
```
Lê markdown ou blocos `@tag` e ignora citação em bloco (`@citacao`, `@citacao-ref`,
linhas `>`), trecho entre aspas, títulos, tabelas e código. Saída: `arquivo:linha:
[regra] mensagem | trecho` e, por arquivo, a média de palavras por parágrafo e a parcela
de aberturas por sujeito nominal; ou JSON com `alertas`, `resumo` e `paragrafos`.

| Regra | Aponta | Triagem |
|---|---|---|
| `GO-2` | travessão, meia-risca ou hífen com espaços | vira vírgula; só a ruptura sintática radical fica |
| `GO-4/paragrafo` | acima de 120 palavras (referência), acima de 130 (quase sempre duas ideias), ou mais de dois períodos num parágrafo acima de 90 palavras | uma ideia só? mantenha; duas? quebre na costura, nunca resuma |
| `GO-4/media` | média de palavras por parágrafo fora de 45 a 65 (peça com seis ou mais parágrafos) | acima: parágrafos juntando ideias; abaixo: frases soltas em série? Nunca alongue parágrafo para chegar à faixa |
| `GO-4/aberturas` | três parágrafos seguidos com a mesma abertura | varie conectivo ou estrutura |
| `GO-1/abertura` | mais de cerca de metade dos parágrafos abrindo sem conectivo, por sujeito nominal ("O MPF") ou demonstrativo ("Esse acórdão"), ou três seguidos (peça com seis ou mais parágrafos); a frase que apresenta citação não conta, e título e citação reiniciam a sequência | abra pela conjunção da relação lógica (Ademais, Portanto, Todavia…); sujeito nominal fica se nomeia o passo novo do argumento |
| `GO-1/remissao` | remissão órfã: demonstrativo que retoma termo de dois ou mais parágrafos atrás, ou que abre o capítulo apontando para o anterior | repita o termo exato ou nomeie o referente na frase ("Essa ratio, que afastou…"); a remissão ao que acabou de ser dito, que constrói o passo seguinte ("Nessa perspectiva, …"), fica |
| `GO-5/ensaio`, `GO-5/metadiscurso` | léxico da lista do GO-5 | regra de conversão do GO-5 |
| `GO-6` | "não é X, mas Y", "não se trata de", "longe de ser" | teste de triagem do GO-6 |
| `GO-7/parafrase` | parágrafo vizinho de citação que reconta o julgado ("Nesse julgado, o STJ entendeu…") ou repete metade ou mais do vocabulário dela | fica só o que a citação não mostra: a aplicação ao caso ou o arremate |
| `GO-7/repeticao` | parágrafo com 75% ou mais do vocabulário de outro, não vizinho (conclusão anunciada e repetida) | diga uma vez, no fim do tópico |
| `GO-7/precedente-narrado` | frase que conta o que o tribunal fez e por quê ("o STJ cassou…, por reconhecer que…"), com a referência do julgado e sem trecho entre aspas | mostre: frase de apresentação e trecho em bloco, com grifo; na prosa, só a corroboração curta |
| `GO-7/decisao-contraria` | decisão invocada pela parte contrária transcrita em bloco, ou decisões contrárias tratadas em três ou mais parágrafos | um parágrafo de conjunto: grau, data, o que decidiram em uma linha, os pronunciamentos favoráveis |
| `GO-7/reformulacao` | "ou seja", "vale dizer", "em outras palavras" mais de uma vez | fica a que acrescenta a consequência; a que repete sai |
| `precisao/o-mesmo` | "o mesmo" seguido de verbo ou pontuação | repita o termo ou reorganize |
| `persuasao/*` | adjetivo de indignação; julgador como sujeito do erro | `persuasao.md` |
| `revisao/metalinguagem`, `revisao/andaime` | as duas lentes abaixo | idem |
| `cortesia/saturacao`, `padrao/vocativo` | vênia, latim, cortesia ou vocativo acima da dose | corte o excedente |
| `casa/lexico` | "impetração" | "ação" ou "demanda" |

## Varreduras, nesta ordem
**Antes delas, o peso** (peça de mérito) — *leitura*. A construção do argumento vem antes
da forma: o teste do parágrafo (a decisão mudaria se o julgador o pulasse?), a ordem
dentro do tópico e o espaço proporcional ao peso (`persuasao.md`). Na peça inteira, essa
revisão é da `sensibilidade-argumentativa`, seguida do `moderador-final`
(`plano-de-respostas`, Passo 5); as varreduras abaixo rodam na versão adotada.

1. **Dizer uma vez (GO-7)** — *radar e leitura*. Antes de polir a forma, corte o que o
   texto diz duas vezes. Em volta de cada citação fica só o que ela não mostra: a frase
   que a apresenta e, depois, a aplicação ao caso ou o arremate; sai o parágrafo que
   reconta o julgado ou reexplica a norma transcrita. Sai também a frase que reexplica a
   anterior, a que anuncia o que o parágrafo seguinte prova, a conclusão anunciada na
   abertura do capítulo e repetida no fim, a explicação ao julgador do que a citação do
   dispositivo já carrega e o relato, uma por uma, de decisões contrárias, que se
   respondem num parágrafo de conjunto e não se transcrevem. O precedente que sustenta o
   argumento se mostra (apresentação e bloco com grifo), não se conta na prosa. Teste:
   apague a frase ou o parágrafo; o julgador perde algo que a citação, o grifo e o texto
   vizinho não lhe dão?
2. **Traço aditivo (GO-2)** — *radar*. Primeira prioridade: todos os traços aditivos
   viram vírgula.
3. **Uma ideia por parágrafo (GO-4)** — *radar e leitura*. A régua é a ideia, não o
   número: cada parágrafo diz uma coisa só, normalmente em um ou dois períodos curtos. O
   radar dá a média da peça (alvo de 45 a 65 palavras, consequência e não meta) e aponta
   os que passam de 120; a leitura decide. Uma ideia que precisa de 125 ou 130 palavras
   fica; dois movimentos argumentativos no mesmo bloco se separam (o movimento a mais, só
   a leitura vê).
   **Ligação e remissão (GO-1)** — *radar e leitura*. O radar dá a parcela de parágrafos
   abertos sem conectivo (teto de cerca de metade, nunca três seguidos) e aponta as
   remissões que saem da vista do leitor; a leitura confere se cada parágrafo abre pela
   conjunção da relação real com o anterior, se cada demonstrativo retoma o que o leitor
   acabou de ler, sem ambiguidade nem repetição, e se o capítulo abre pela própria tese. Corrija com a conjunção ou
   repetindo o termo exato; nunca com frase que resume o parágrafo anterior, nem trocando
   o artigo por demonstrativo ("Esse acórdão" no lugar de "O acórdão").
4. **Dois pontos em série (GO-3)** — *leitura*. Conte, por seção, as frases "afirmação:
   desdobramento"; repetidas, integre com conjunção. O anúncio de transcrição
   ("vejamos:", "in verbis:") não conta.
5. **Registro (GO-5)** — *radar e leitura*. Varra a peça **inteira**, não só os casos
   vistosos: o padrão escorrega em frases discretas. Teste: se a frase caberia numa
   crônica de jornal ou num artigo de opinião, reformule. Conversões reais do José:

   | ✗ Fórmula de ensaio | ✓ Formulação técnica |
   |---|---|
   | "o segundo requisito **é o que melhor revela o descompasso**" | "quanto ao segundo requisito, a apelação **parte de premissa que não corresponde à tese vinculante**" |
   | "**o problema não está em** X, mas em Y" | "a controvérsia **cinge-se a** Y" (se a parte contrária sustentou X, refute X expressamente: GO-6) |
   | "**seria uma coisa**; a União, **porém**…" | afirmar direto: "A União, contudo, [operação jurídica]…", sem o contraste de suspense |
   | "não segue esse caminho, **e nunca o seguiu**" | "não adotou essa providência", sem a dramatização por reforço |
6. **Negação (GO-6)** — *radar*. O padrão sempre contém uma negação, então a busca tem
   recall alto; a triagem do GO-6 é que separa vício de refutação (em peça real, de 31
   negações, 23 eram o vício).
7. **Premissa adversária (precisão)** — *leitura*. Identifique a premissa nuclear da tese
   e procure, na peça inteira, palavras que a contradigam por descuido.
8. **Enumeração-andaime** — *radar e leitura*. Fundamentos numerados sem que a ordem
   signifique algo no argumento: a enumeração organiza quem escreve, não o raciocínio.
   > ✗ "A pretensão se sustenta por duas razões. Primeiro, porque o contrato não previu
   > reajuste. Segundo, porque a parte anuiu com o preço por dois anos."
   > ✓ "O contrato não previu reajuste e a parte anuiu com o preço por dois anos, de modo
   > que a revisão não encontra apoio nem no ajuste nem no comportamento das partes."

   Numere quando a ordem for do argumento: requisitos legais percorridos um a um,
   pedidos, itens de uma lista da lei, a recapitulação do padrão 7. Não numere para
   arrumar parágrafo.
9. **Metalinguagem** — *radar e leitura*. O texto anuncia o que vai fazer ou avalia a
   própria força, em vez de fazê-lo.
   > ✗ "Disso decorrem dois efeitos reais e favoráveis à consulente." · "Como se
   > demonstrará adiante, o argumento é robusto." · "Passa-se agora à análise da segunda
   > tese."
   > ✓ Escrever o efeito: "A cláusula transfere o encargo ao contratante, o que desloca
   > para ele a legitimidade para pedir a devolução."

   Adjetivo sobre o próprio argumento ("robusto", "irrefutável", "reais e favoráveis") é
   sempre corte: se o argumento é forte, o leitor percebe pelo argumento. A frase que
   apresenta a citação (padrão 1), inclusive o "vejamos:", não é metalinguagem e fica.

   **Cuidado inverso:** a transição que diz a relação lógica entre as ideias ("Diante
   dessa omissão, a multa perde a base") é ligação (GO-1), não metalinguagem: nunca
   proponha cortá-la, porque o corte que picota o texto é tão vício quanto o anúncio
   vazio. Já o parágrafo que resume o que acabou de ser dito é repetição (GO-7) e sai;
   fica a recapitulação enumerada do padrão 7, antes do pedido, em seção longa.
10. **Persuasão (peça)** — *leitura*. O tópico abre pela tese? O fecho toma partido (teste
   do parecer neutro)? A crítica mira a decisão, não o julgador? A objeção já levantada
   recebe resposta na medida do peso? Objeção antecipada só a provável, e nunca nos
   pedidos? (`persuasao.md`)
11. **Padrões da casa (peça)** — *leitura*. Cada citação tem a frase que diz por que ela
    importa e o grifo no trecho decisivo, sem parágrafo que a reconte? Arremate no fecho de
    cada tópico, dito uma vez? Recapitulação antes do pedido em seção longa? Vocativo só
    nos momentos decisivos? (`padroes-da-casa.md`)
12. **Latim e cortesia** — *radar*. Saturação de vênia, latim ornamental ou bajulação.
13. **Registro externo** — *leitura*. Probabilidade crua ou estratégia interna vazando
    para o cliente: gravidade alta, corrige sempre.
14. **Ancoragem e procedência** — *leitura*. Parágrafo que caberia em qualquer processo
    sobre o tema; referência aos autos sem tipo do documento, NUM e página.

## Roteiro — revisar peça pronta (chamada direta)
1. **Situe:** tipo de peça, registro e destinatário, tirados do próprio texto; pergunte
   só o que ele não responde. Havendo CNJ, resolva o workspace (`processo.py workspace
   <cnj>`) e use os extratos para conferir ancoragem e procedência.
2. **Prepare a cópia:** nunca sobrescreva o original. Se vier em `.docx`, extraia o texto
   para `.md` na ordem dos parágrafos (ex.: `python-docx`) e trabalhe em
   `<nome>-revisada.md`.
3. **Radar e leitura de estrutura:** rode o `lint_peca.py` e leia a peça inteira uma vez.
   A tese abre os tópicos? Há coerência fatos → fundamentos → pedidos? Algum pedido sem
   fundamento?
4. **Varreduras** na ordem acima. O diagnóstico (estrutura, registro ou conteúdo) decide
   o tamanho da intervenção; conteúdo jurídico duvidoso não se "melhora": anote para o
   José.
5. **Entregue** a versão revisada em arquivo e, no chat, só a lista curta: o que mudou,
   por regra, e as questões de conteúdo deixadas para decisão. Havendo citações, rode a
   `verificacao-citacoes`; `.docx`, pela `formatacao-entrega`, se pedido.
6. **Profundidade:** trecho curto ou ajuste pontual (N1) → radar e leitura; peça comum
   (N2) → os dois revisores e depois o roteiro completo; peça longa (N3) → os dois
   revisores, depois um subagente Sonnet por seção como radar, com a reescrita sua.

### Remover juridiquês e dar fluidez
Mesmo roteiro, com foco em:
- latim ornamental e bajulação, na calibragem da skill (dose pontual é natural; a
  saturação é o vício);
- sinonímia e tautologia ("nulo e de nenhum efeito", "claro e evidente");
- substantivo no lugar do verbo ("tomar a decisão de revisar" → "decidir revisar";
  "apresentou reclamação" → "reclamou");
- ordem indireta e intercalação longa; voz passiva sem razão (só quando o agente é
  irrelevante ou desconhecido); dupla negação ("não é impossível" → "é possível");
- ênfase por negrito ou maiúsculas soltas no meio do texto, em vez da posição
  (palavra-chave no início ou no fim da frase); a formatação estrutural é da
  `formatacao-entrega`;
- frases justapostas sem conectivo, parágrafos abertos em série sem conjunção e remissões
  fora da vista do leitor (GO-1), repetição e paráfrase de citação (GO-7) e ritmo
  monótono (GO-4).

Escreva para se expressar, não para impressionar, sem descer do registro técnico (GO-5).
