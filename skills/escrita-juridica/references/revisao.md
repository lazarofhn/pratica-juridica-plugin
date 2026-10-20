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
    [--media 70-90] [--aberturas 3] [--max-cortesia 2] [--ignorar GO-6,cortesia]
```
Lê markdown ou blocos `@tag` e ignora citação em bloco (`@citacao`, `@citacao-ref`,
linhas `>`), trecho entre aspas, títulos, tabelas e código. Saída: `arquivo:linha:
[regra] mensagem | trecho` e a média de palavras por parágrafo de cada arquivo, ou JSON
com `alertas`, `resumo` e `paragrafos`.

| Regra | Aponta | Triagem |
|---|---|---|
| `GO-2` | travessão, meia-risca ou hífen com espaços | vira vírgula; só a ruptura sintática radical fica |
| `GO-4/paragrafo` | acima de 120 palavras (referência), acima de 130 (quase sempre duas ideias), ou mais de dois períodos num parágrafo acima de 90 palavras | uma ideia só? mantenha; duas? quebre na costura, nunca resuma |
| `GO-4/media` | média de palavras por parágrafo fora de 70 a 90 (peça com seis ou mais parágrafos) | acima: parágrafos juntando ideias; abaixo: raciocínio picotado |
| `GO-4/aberturas` | três parágrafos seguidos com a mesma abertura | varie conectivo ou estrutura |
| `GO-5/ensaio`, `GO-5/metadiscurso` | léxico da lista do GO-5 | regra de conversão do GO-5 |
| `GO-6` | "não é X, mas Y", "não se trata de", "longe de ser" | teste de triagem do GO-6 |
| `precisao/o-mesmo` | "o mesmo" seguido de verbo ou pontuação | repita o termo ou reorganize |
| `persuasao/*` | adjetivo de indignação; julgador como sujeito do erro | `persuasao.md` |
| `revisao/metalinguagem`, `revisao/andaime` | as duas lentes abaixo | idem |
| `cortesia/saturacao`, `padrao/vocativo` | vênia, latim, cortesia ou vocativo acima da dose | corte o excedente |
| `casa/lexico` | "impetração" | "ação" ou "demanda" |

## Varreduras, nesta ordem
1. **Traço aditivo (GO-2)** — *radar*. Primeira prioridade: todos os traços aditivos
   viram vírgula.
2. **Uma ideia por parágrafo (GO-4)** — *radar e leitura*. A régua é a ideia, não o
   número: cada parágrafo diz uma coisa só, normalmente em um ou dois períodos curtos. O
   radar dá a média da peça (alvo de 70 a 90 palavras) e aponta os que passam de 120; a
   leitura decide. Uma ideia que precisa de 125 ou 130 palavras fica; dois movimentos
   argumentativos no mesmo bloco se separam (o movimento a mais, só a leitura vê).
3. **Dois pontos em série (GO-3)** — *leitura*. Conte, por seção, as frases "afirmação:
   desdobramento"; repetidas, integre com conjunção. O anúncio de transcrição
   ("vejamos:", "in verbis:") não conta.
4. **Registro (GO-5)** — *radar e leitura*. Varra a peça **inteira**, não só os casos
   vistosos: o padrão escorrega em frases discretas. Teste: se a frase caberia numa
   crônica de jornal ou num artigo de opinião, reformule. Conversões reais do José:

   | ✗ Fórmula de ensaio | ✓ Formulação técnica |
   |---|---|
   | "o segundo requisito **é o que melhor revela o descompasso**" | "quanto ao segundo requisito, a apelação **parte de premissa que não corresponde à tese vinculante**" |
   | "**o problema não está em** X, mas em Y" | "a controvérsia **cinge-se a** Y" (se a parte contrária sustentou X, refute X expressamente: GO-6) |
   | "**seria uma coisa**; a União, **porém**…" | afirmar direto: "A União, contudo, [operação jurídica]…", sem o contraste de suspense |
   | "não segue esse caminho, **e nunca o seguiu**" | "não adotou essa providência", sem a dramatização por reforço |
5. **Negação (GO-6)** — *radar*. O padrão sempre contém uma negação, então a busca tem
   recall alto; a triagem do GO-6 é que separa vício de refutação (em peça real, de 31
   negações, 23 eram o vício).
6. **Premissa adversária (precisão)** — *leitura*. Identifique a premissa nuclear da tese
   e procure, na peça inteira, palavras que a contradigam por descuido.
7. **Enumeração-andaime** — *radar e leitura*. Fundamentos numerados sem que a ordem
   signifique algo no argumento: a enumeração organiza quem escreve, não o raciocínio.
   > ✗ "A pretensão se sustenta por duas razões. Primeiro, porque o contrato não previu
   > reajuste. Segundo, porque a parte anuiu com o preço por dois anos."
   > ✓ "O contrato não previu reajuste e a parte anuiu com o preço por dois anos, de modo
   > que a revisão não encontra apoio nem no ajuste nem no comportamento das partes."

   Numere quando a ordem for do argumento: requisitos legais percorridos um a um,
   pedidos, itens de uma lista da lei, a recapitulação do padrão 7. Não numere para
   arrumar parágrafo.
8. **Metalinguagem** — *radar e leitura*. O texto anuncia o que vai fazer ou avalia a
   própria força, em vez de fazê-lo.
   > ✗ "Disso decorrem dois efeitos reais e favoráveis à consulente." · "Como se
   > demonstrará adiante, o argumento é robusto." · "Passa-se agora à análise da segunda
   > tese."
   > ✓ Escrever o efeito: "A cláusula transfere o encargo ao contratante, o que desloca
   > para ele a legitimidade para pedir a devolução."

   Adjetivo sobre o próprio argumento ("robusto", "irrefutável", "reais e favoráveis") é
   sempre corte: se o argumento é forte, o leitor percebe pelo argumento. O anúncio de
   transcrição do sanduíche de citação ("vejamos:") não é metalinguagem e fica.
9. **Persuasão (peça)** — *leitura*. O tópico abre pela tese? O fecho toma partido (teste
   do parecer neutro)? A crítica mira a decisão, não o julgador? Objeção antecipada só a
   provável, e nunca nos pedidos? (`persuasao.md`)
10. **Padrões da casa (peça)** — *leitura*. Alguma citação ou documento órfão de leitura
    dirigida? Micro-conclusão no fecho de cada tópico? Recapitulação antes do pedido em
    seção longa? Vocativo só nos momentos decisivos? (`padroes-da-casa.md`)
11. **Latim e cortesia** — *radar*. Saturação de vênia, latim ornamental ou bajulação.
12. **Registro externo** — *leitura*. Probabilidade crua ou estratégia interna vazando
    para o cliente: gravidade alta, corrige sempre.
13. **Ancoragem e procedência** — *leitura*. Parágrafo que caberia em qualquer processo
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
   (N2) → roteiro completo; peça longa (N3) → um subagente Sonnet por seção como radar,
   com a reescrita sua.

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
- frases justapostas sem conectivo (GO-1) e ritmo monótono (GO-4).

Escreva para se expressar, não para impressionar, sem descer do registro técnico (GO-5).
