# Esqueleto para o redator (N3 e N4, em teste)

Leia quando a peça for escrita pelo agente `pratica-juridica:redator`. O esqueleto é tudo
o que o redator recebe: ele não lê os autos, a pesquisa nem o plano. O que não estiver
aqui não entra na peça, e o que estiver vago ele escreve vago.

## O que o esqueleto é
É a peça inteira decidida, sem a prosa: o que se quer com ela e como, e, tópico por
tópico, cada passo do argumento na ordem do peso, com a frase de tese já na redação
final, cada fato com a prova e cada citação já montada. Notas, não parágrafos: em prosa
final ficam só as frases de tese e as partes fixas. Se você se pegar redigindo a peça no
esqueleto, parou de planejar e começou a escrever duas vezes.

Fica em `<workspace>/redacao/esqueleto.md` (na equipe, `_equipe\produto\<nome>-esqueleto.md`).

## Modelo
```
# Esqueleto — <peça> (<processo>)

## Contexto
- **O que a peça quer:** <o resultado, de quem, e o que muda para o cliente>
- **Quem julga e em que momento:** <juízo ou relator; o que ele acabou de ler; o que já decidiu>
- **Como quero que soe:** <firme, sóbrio, técnico…; o que a peça não faz: não ataca o juízo, não concede X, não soa defensiva em Y>
- **Premissa nuclear:** <a tese em uma frase; vale para a peça inteira>
- **Termos da peça:** <como chamar cada parte, ato, decisão e tribunal, sempre do mesmo jeito; diga se a sigla vale na prosa>
- **Termos proibidos:** <palavra ou expressão — por que trai a tese>
- **Registro:** peça

## Partes fixas
<endereçamento, identificação, título, o parágrafo de abertura, a linha que introduz os
pedidos, os pedidos e o fecho, já em @tag, na redação final>

## Tópico 1 — <título, na redação final>
Resultado: <o que o dispositivo deve dizer> | Peso: núcleo | Espaço: ~<n> parágrafos | Geração: 1
1. [tese] "<frase literal, na redação final>"
2. [fato] <o fato, em nota> — (<tipo do documento>, id <n>, p. <n>)
3. [norma] <o dispositivo e o que dele se extrai> — transcrever na frase: "<trecho curto, literal>" | em bloco (o @citacao vem montado, como no item de citação) | só citar
4. [citacao] apresenta: <o que ela prova, quem decidiu, por que o caso é igual> | aplica: <o passo seguinte, no caso>
   @citacao-ref
   fonte: …
   processo: …
   grifo: …
   ref: …
5. [argumento] <o passo do raciocínio, em nota: premissa → consequência>
6. [objecao] <o que o adversário disse, com a página> → <a resposta> | espaço: uma oração | um parágrafo
7. [fecho] <a conclusão do tópico, que toma partido>
```

## Regras para quem monta
- **O Contexto vem primeiro e não é formalidade.** É por ele que o redator escolhe entre
  duas palavras de carga diferente. Diga o que você quer do julgador, o tom e o que a
  peça não pode conceder. Premissa nuclear e termos proibidos saem da varredura de
  premissa adversária (`escrita-juridica`, "Precisão e ancoragem").
- **Os itens estão na ordem em que o julgador deve lê-los.** É a ordem do mapa de peso:
  conclusão, fato decisivo com a prova, condição, objeção relevante, fecho. O redator
  não reordena.
- **A densidade vem do esqueleto.** O redator articula o que o item diz e não inventa
  desenvolvimento: no teste de nov./2026, um tópico de núcleo com um só item `[argumento]`
  saiu fiel e raso. Tópico de núcleo pede cerca de um item por parágrafo previsto, e cada
  `[argumento]` traz a premissa e a consequência. O custo é real: no teste com uma
  manifestação de 47 parágrafos, o esqueleto ficou do tamanho da peça.
- **Todo tópico abre por um item `[tese]`,** inclusive o de apoio.
- **Frase de tese, literal.** Toda afirmação em que a palavra decide (o que a decisão
  disse, o que a lei exige, o que se pede) vem escrita como deve sair. O redator a liga
  e a desenvolve; não a reformula.
- **Citação montada.** O bloco `@citacao-ref` (ou `@citacao`) vem pronto, com o grifo, e
  o item diz o que a frase de apresentação afirma e qual é a aplicação ao caso. A
  apresentação diz o que o bloco não mostra; se você repetir nela o trecho grifado, o
  redator fica entre a sua instrução e o GO-7. Decisões
  invocadas pelo adversário entram como um item `[objecao]` só, de conjunto (GO-7).
- **Fato com a prova.** Documento, id e página em cada fato; fato sem referência volta do
  redator como lacuna.
- **Espaço por tópico e por objeção.** É o do mapa de peso, em parágrafos de prosa, sem
  contar a frase que só apresenta uma citação; "uma oração" quer dizer uma oração.
- **O Contexto não contradiz os itens.** Se ele diz que todo capítulo abre pela tese, o
  primeiro item de cada tópico é a tese; onde houver conflito, o redator segue os itens.
- **Termo proibido é da voz da peça.** No item que relata a tese adversária, escreva o
  termo do adversário como ele deve sair (atribuído ou entre aspas), para o redator não
  ter de escolher entre a fidelidade e a proibição.
- **O que a lei exige** (admissibilidade, impugnação especificada, fundamento autônomo)
  entra como item, no espaço que o peso pede.

## Sequência
1. Você monta o esqueleto a partir do mapa de peso aprovado, dos dossiês e da pesquisa.
2. **`sensibilidade-argumentativa` sobre o esqueleto:** passe o esqueleto como `PECA`. Ela
   devolve o mapa de peso, as mudanças, os cortes e as lacunas, e grava
   `esqueleto-sensibilidade.md` com os itens reordenados, sem prosa. Você confere (nada
   perdido, frases de tese e blocos intactos), veta os cortes que quiser e fecha o
   esqueleto. A revisão do peso acontece aqui, antes de existir texto: com o redator, a
   sensibilidade não reescreve a peça pronta.
3. **`redator`:** `ESQUELETO`, `SAIDA` e `REGISTRO`. Um só agente para a peça inteira; se
   ele parar antes do fim, retome o mesmo agente (ou abra outro com a mesma `SAIDA`, que
   ele lê e continua).
4. **Conferência de fidelidade, sua:** cada item do esqueleto está na peça, no lugar e no
   espaço dele; frases de tese e blocos idênticos; nenhum fato, número, precedente ou
   termo proibido que o esqueleto não trouxe. Lacuna devolvida pelo redator se resolve no
   esqueleto e volta a ele; não se remenda a peça por fora.
5. **`moderador-final`** sobre a peça, depois o radar e a `verificacao-citacoes`, como no
   Passo 5 do plano. Ajuste que mude conteúdo, ordem ou espaço entra no esqueleto e volta
   ao redator; ajuste de uma frase, você mesmo faz.
