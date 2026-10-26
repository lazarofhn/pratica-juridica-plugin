# Guia de Construção das Skills — plugin pratica-juridica

Documento-mãe para construir e revisar as skills. Consolida a ideia bruta do José e as
decisões de arquitetura já travadas. **Revisar antes de construir.**

## Decisões travadas — v1.4 (out/2026)
Prevalecem sobre as da v1.3 onde divergem.

1. **O peso decide antes da forma.** O índice nasce do mapa de peso (resultado →
   núcleo, apoio, fora), pelo teste "se o julgador não ler, o que acontece com o
   resultado?". Tópico é o caminho até um resultado; subtópico só para núcleo; espaço
   proporcional ao peso; a objeção já levantada pelo adversário passa pela mesma régua.
   A exigência legal (admissibilidade, impugnação especificada, fundamento autônomo da
   decisão) entra sempre, e o peso decide só o espaço. Origem: a reescrita do José de uma
   petição em que a versão do Claude dissertava sobre a teoria da contagem do prazo,
   deixava a data sem prova e abria um tópico para cada ponto do adversário.
2. **Uma só mão escreve.** No N3, o subagente Opus prepara o dossiê do tópico (fatos com
   folha, precedentes com ID, o que o adversário disse, lacunas) e o coordenador redige a
   peça inteira. A redação por tópico da v1.3 inflava cada tópico e quebrava a coesão.
3. **Dois revisores com a peça pronta** (registro peça, N2 em diante):
   `sensibilidade-argumentativa` (Opus) reorganiza pelo peso, em arquivo novo, sem nada
   novo e com os cortes para o veto de quem redigiu; `moderador-final` faz o papel do
   julgador (Fable no N3 e no N4; Opus no N2). Uma rodada de cada; N1 não tem revisores.
4. **Os revisores moram no `pratica-juridica`** (`agents/`), e a `equipe-juridica` 0.5
   os usa: uma fonte só para a construção do argumento.

## Decisões travadas — v1.3 (out/2026)
Prevalecem sobre as decisões e especificações mais antigas deste guia.

1. **Triagem de complexidade é a primeira regra do pipeline.** O `analise-processual`
   classifica o pedido em N1 (simples), N2 (padrão), N3 (complexo) ou N4 (equipe),
   declara o nível em uma linha e segue; o José sobe ou desce. O nível decide o plano,
   quem redige, o conselheiro e a profundidade da verificação.
2. **Profundidade sem paradas.** A profundidade vem do ciclo por geração (pesquisa
   focada, volta aos autos, redação em arquivo), não da parada. N2: plano curto, sem
   paradas. N3: aprovação do plano e um subagente Opus por tópico, com costura do
   coordenador (na v1.4, o subagente prepara o dossiê e o coordenador redige). Revisão
   tópico a tópico só a pedido.
3. **Agentes nativos, modelo por tarefa.** Haiku para o mecânico; Sonnet para leitura,
   triagem e buscas com síntese; Opus para redação de tópicos e conferência de ratio;
   Fable como conselheiro nas decisões decisivas (quando a sessão principal não é
   Fable): o advisor da aba Code, se ligado (`/advisor fable`); senão, um subagente
   Fable com dossiê. O plugin não usa MCP de agentes externos.
4. **N4 → `equipe-juridica`**, sempre por proposta, nunca automático.
5. **Sem bloco "regra de uso".** Nenhuma skill pergunta "pipeline ou avulso"; cada uma
   declara suas precondições e, chamada fora do pipeline, assume N2 (N1 na peça
   protocolar).
6. **Descrição de skill com ~250 caracteres:** o que produz e quando não usar. Sem
   jargão interno ("camada D", "skill fina").
7. **Skill de saída = só o delta.** Diz o que diverge do padrão do nível; o comum fica
   nas compartilhadas e é citado em uma linha.
8. **Fatos voláteis não se copiam.** Bases, parâmetros e nomes de ferramenta dos
   conectores mudam: a fonte é a descrição viva da ferramenta e o `*_listar_filtros`.
9. **Fusões:** `peca-processual-base` sai (esqueleto e coerência → `plano-de-respostas`;
   antecipação de objeção → `escrita-juridica`); `analise-estrategia` entra no
   `relatorio` (modo interno com foco em estratégia).
10. **Dono único:** estilo = `escrita-juridica`; método de pesquisa =
    `pesquisa-juridica`. As skills antigas de conta (redação natural e método de
    pesquisa no juris_br) são aposentadas.
11. **Variante ChatGPT Work/Codex congelada** em 1.2.0 (`plugins/pratica-juridica-work`).
12. **Páginas sem texto → conector busca-autos, só quando relevante.** Decide-se pelo
    índice; no N3/N4 a indexação começa no início, em segundo plano; só a parte que é
    imagem (sem texto nem OCR) vai ao Colab; modo rápido por padrão.

## Decisões travadas — v1.0 (jul/2026)
1. **Relatórios unificados** em `relatorio` com modo `interno|externo`. O modo
   externo **filtra conteúdo** (não só suaviza o tom): não expõe probabilidade
   crua de êxito nem estratégia interna.
2. ~~`peca-processual-base` guarda as orientações comuns às peças protocoladas.~~
   Fundida na v1.3 (decisão 9).
3. ~~Aprovação do plano só em peças grandes.~~ Substituída pela decisão 2 da v1.3.

## Mapa de skills (v1.4)
```
A · analise-processual   (orquestrador: triagem N1–N4, agentes, roteamento)
B · obter-processo       (opcional, Chrome; também consulta de andamento)
C · analise-processo-pje (retrieval no PDF: índice → ranking → extração)

D · SAÍDAS:
    peca-recurso         (recursos e contrarrazões)
    peca-especifica
    peca-simples
    memorial
    relatorio            (interno|externo; inclui estratégia)

E · COMPARTILHADAS:
    plano-de-respostas   (N2/N3: mapa de peso, gerações, aprovação no N3, dossiê por
                          tópico, revisão argumentativa)
    pesquisa-juridica    (método único: lei e doutrina, depois jurisprudência)
    escrita-juridica     (o peso antes da forma; registros peça|interno|externo;
                          revisão de peça pronta)
    formatacao-entrega   (→ .docx)
    verificacao-citacoes (checagem contra as fontes)

F · AGENTES (agents/):
    sensibilidade-argumentativa (Opus: reorganiza a peça pronta pelo peso)
    moderador-final             (Fable no N3/N4, Opus no N2: lê como o julgador)
```

## Fluxo do orquestrador (v1.4)
1. Avaliar a complexidade (N1–N4) e declarar o nível.
2. Rotear para a skill de saída.
3. Garantir os autos (PDF do José; `obter-processo` se pedido) e resolver o workspace.
4. Ler seletivamente (`analise-processo-pje`), guiado pelo objetivo e pelo nível.
5. N2/N3: `plano-de-respostas`, com o mapa de peso (aprovação só no N3). N1 vai direto.
6. Produzir (skill D), que puxa a camada E.
7. N2 em diante, na peça: revisão argumentativa (`sensibilidade-argumentativa`, depois
   `moderador-final`), com as decisões de quem redigiu.
8. Radar, `verificacao-citacoes` na profundidade do nível e `.docx` pela
   `formatacao-entrega`.

---

## Template — skill de saída (D), só o delta
1. **Quando ativar** — e quando não (a descrição diz o mesmo em ~250 caracteres).
2. **Precondições** — o que precisa existir (workspace, plano), sem perguntar
   "pipeline ou avulso".
3. **Perguntas** — só o que os autos não respondem.
4. **Estrutura** — a fonte (artigo do CPC) e o que diverge do esqueleto padrão do
   `plano-de-respostas`.
5. **Segmentação e regras de ouro próprias do tipo.**
6. **Pesquisa, escrita, entrega e verificação** — só o que diverge do padrão do nível,
   uma linha cada.

> Histórico: até a v1.2 o template tinha 9 seções fixas, o que fazia cada skill repetir
> as compartilhadas.

---

## Especificação das skills D

### peca-recurso (recursos e contrarrazões)
1. **Ativar:** recorrer ou contrarrazoar. Nível típico: N3 em REsp/RE e apelação com
   várias teses; N2 em embargos de declaração simples.
2. **Perguntas — identificar o recurso:** se o José omitiu e houver mais de um recurso
   plausível, informe o cabimento que você vê e confirme antes de redigir; se só um
   couber (sentença → apelação), siga.
3. **Estrutura:** o artigo do CPC que regula o recurso; fallback = esqueleto do
   `plano-de-respostas`.
4. **Plano:** **REGRA DE OURO — RE/REsp:** uma geração por requisito de
   admissibilidade (repercussão geral, prequestionamento etc.); a falta de
   fundamentação específica de um requisito derruba o recurso.
5. **Viabilidade (REsp/RE):** estudo prévio do eixo (Súmula 7/STJ, 279/STF…); no N3 a
   decisão do eixo passa pelo conselheiro Fable.
6. **Contrarrazões:** admissibilidade invertida (apontar o não cabimento e os óbices) e
   resposta pelo peso: todo fundamento do recurso que, acolhido, mudaria o resultado; o
   resto, uma oração ou nada.
7. **Verificação:** obrigatória.

### peca-especifica
1. **Ativar:** peça com previsão/nomenclatura própria no CPC (contestação, réplica,
   impugnação ao cumprimento de sentença, embargos à execução, embargos de terceiro…).
   > ⚠️ **Embargos de declaração NÃO entram aqui** — é recurso → `peca-recurso`.
2. **Perguntas:** confirmar qual peça, se ambíguo; o marco processual (prazo,
   intimação) é dado dos autos, não pergunta.
3. **Estrutura:** onde a peça está prevista no CPC + doutrina; requisitos próprios.
4. **Plano:** um tópico por resultado (mapa de peso); toda causa de pedir enfrentada e,
   na contestação, todo fato impugnado (art. 341), no espaço que o peso pede.
5. **Pesquisa:** sem a ênfase de admissibilidade dos recursos; jurisprudência
   processual só se o José enfatizar a questão processual.
6. **Regra de ouro:** identificar a previsão/nomenclatura específica correta.

### peca-simples
1. **Ativar:** manifestação **sem** nomenclatura/requisitos específicos no CPC, guiada
   pelo **comando** (do José ou do despacho que intimou a parte).
2. **Porte pelo comando:** protocolar (só comunica ou requer o rotineiro → N1) ×
   substancial (precisa convencer → N2/N3). Teste: o leitor precisa ser convencido de
   algo?
3. **Regra de ouro:** "simples" = sem previsão específica no CPC, **não** = curta; e
   protocolar não infla.

### memorial
1. **Ativar:** processo **pendente de julgamento** (1º grau ou instância recursal).
2. **Estrutura:** resumo das alegações da peça-base em julgamento, com **ênfase nos
   precedentes decisivos**, por eixo argumentativo.
3. **Pesquisa:** reaproveita a fundamentação já nos autos; pode reforçar precedentes
   decisivos — **sem nova ratio**.
4. **Verificação:** obrigatória + matriz eixo → documento/página da peça-base,
   provando que nada saiu de fora dos autos.
5. **REGRA DE OURO:** o memorial **não inova** a argumentação; muda a *ênfase*, nunca a
   *ratio*.

### relatorio (interno|externo; inclui estratégia)
1. **Ativar:** informar sobre o processo ou planejar a estratégia, sem peça. A
   estratégia é o modo interno com foco em questões-chave, cenários e próximos passos —
   pode ser fase preliminar de uma peça.
2. **Perguntas:** destinatário (escritório/cliente), se não estiver claro.
3. **Estrutura:** situação atual → o que está em jogo → [interno: riscos, chance
   qualitativa com a base declarada, estratégia] → próximos passos.
4. **Regras de ouro:** externo **nunca omite** situação negativa, mas equilibra com o
   caminho de solução que de fato existe nos autos ou no plano do escritório; externo
   **não** expõe probabilidade crua nem estratégia interna; interno é franco. Antes de
   relatar a "situação atual", confira se o workspace não está defasado.

---

## Especificação das skills E (compartilhadas)

### plano-de-respostas
N2/N3. Mapa de peso (resultado → núcleo, apoio, fora) e índice por resultado; decisão de
segmentação (1 vs N gerações), com gatilho em ≥2 tópicos de núcleo, tutela + mérito ou
>~10 páginas. Aprovação só no N3. No N3, um subagente Opus por tópico prepara o dossiê e
o coordenador redige. Fecha com a costura, a revisão argumentativa (os dois agentes) e o
radar. Guarda o esqueleto da peça protocolada e as regras de coerência fatos →
fundamentos → pedidos.

### pesquisa-juridica
Método único de fundamentação: lei e doutrina (Know-How) antes da jurisprudência
(juris_br); profundidade conforme o nível; rastro em `pesquisas.jsonl` com ferramenta,
ID e parâmetros, para reabrir por ID. Bases e parâmetros: a descrição viva da
ferramenta.

### escrita-juridica
Dona única do estilo. O peso do argumento antes da forma; registros
`peça|interno|externo`; GO-1 a GO-6; persuasão calibrada (com a régua do peso e a
objeção já levantada) e padrões da casa em `references/`, lidos sob demanda; revisão de
peça pronta; varredura automática de padrões por script.

### formatacao-entrega
Tipografia e geração do `.docx` a partir de blocos `@tag`; `@citacao-ref` cola a ementa
verbatim; timbrado por modelo `.docx`.

### verificacao-citacoes
Confere jurisprudência (reabrindo pelo ID do rastro), lei/doutrina, referências aos
autos e números/datas antes de fechar. O mecânico vai a subagentes; o veredito sobre a
ratio fica com o coordenador.

## Especificação dos agentes F

### sensibilidade-argumentativa
Opus. Recebe a peça pronta, a mesa do julgador (peça adversária e decisão atacada), os
resultados e o plano; monta o mapa de peso e reescreve a peça inteira em arquivo novo,
reorganizada pelo peso. Nada novo (argumento, fato, citação, pedido); citações, folhas,
pedidos, sentido das frases de tese e exigências legais intocados. Devolve mapa,
mudanças, cortes para o veto e lacunas.

### moderador-final
Fable no N3/N4; Opus no N2 (o chamador passa `model`). Lê a mesa e depois a peça, como o
julgador; devolve a decisão simulada por pedido, onde a convicção se formou ou se perdeu,
até cinco ajustes por impacto e o que pularia. Não reescreve nem acrescenta tese.

---

## Histórico — ordem de construção da v1.0
1. `peca-processual-base` (destrava as 3 peças protocoladas).
2. `pesquisa-juridica` + `escrita-juridica` (compartilhadas, usadas por todas).
3. `verificacao-citacoes` (maior risco).
4. `peca-recurso` → `peca-especifica` → `peca-simples`.
5. `memorial`, `relatorio`, `analise-estrategia`.
6. `formatacao-entrega`.

`analise-processo-pje` foi migrada pronta; `obter-processo` foi construída na v1.1.0
(PJe mapeado ao vivo, com `references/pje.md`; novos sistemas entram como
`references/<sistema>.md` no mesmo formato).
