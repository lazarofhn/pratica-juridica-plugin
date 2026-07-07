---
name: verificacao-citacoes
description: (camada E — compartilhada, CRÍTICA) Confere TODA asserção verificável de um output jurídico contra a fonte real, antes de fechar — jurisprudência (juris_br), legislação e doutrina (Know-How), referências aos autos (workspace do processo) e números/datas. É a defesa contra citação alucinada, mal atribuída ou superada em documento que leva a assinatura do advogado. Obrigatória em peças; nos relatórios, sempre que houver citação.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Verificação de Citações (camada E — o maior risco do plugin)

Numa peça assinada, citação errada não é bug: é risco ético e reputacional. Toda
skill de output passa por aqui **antes de fechar**. Esta skill não redige — audita.

## Princípios
- **P1 — Contra a FONTE, nunca contra a memória do modelo.** Cada item é reconferido
  abrindo a fonte real (inteiro teor no juris_br, `ler_fonte` no Know-How, workspace
  do processo). "Eu me lembro que é assim" não confere nada.
- **P2 — Inventário antes de verificar.** Primeiro varra o texto e liste TODAS as
  asserções verificáveis; só então confira uma a uma. O que não entra na lista não
  é conferido, e é justamente aí que mora o erro.
- **P3 — Postura adversarial.** Tente **refutar** cada citação ("será que existe
  mesmo? será que diz isso mesmo?"), não confirmá-la por inércia. O default é
  desconfiar.
- **P4 — Na dúvida, não cite.** Se uma citação não puder ser confirmada na fonte,
  trate-a como inexistente e retire-a (alinha com a R3 da `pesquisa-juridica`).

## Passo 1 — Inventário de asserções verificáveis
Extraia do rascunho, em lista, cada ocorrência de:
1. **Jurisprudência** — acórdãos, súmulas, precedentes, enunciados.
2. **Legislação** — artigos, parágrafos, incisos, alíneas citados ou transcritos.
3. **Doutrina** — teses atribuídas a autor/obra.
4. **Referências aos autos** — fls., ID/evento de documento, nomes, qualificações.
5. **Números e datas** — valores, prazos, datas, marcos temporais.

## Passo 2 — Conferir cada item contra a fonte

### A. Jurisprudência (via RASTRO de pesquisa, não por número de processo)
⚠️ **Não reconfira criando uma busca nova por número de processo.** O juris_br não
tem busca confiável por número, e uma reformulação (ex.: "REsp 2132145" vs
"2.132.145") pode não achar um precedente que existe — falso negativo que levaria a
remover jurisprudência boa. Em vez disso, use o `pesquisas.jsonl` (rastro gravado
pela `pesquisa-juridica`):

1. **Localize o registro** da busca que originou a citação no `pesquisas.jsonl`.
   - **Se não houver registro** para aquele precedente, é sinal de que a citação não
     veio de uma busca real → trate como não verificada (⚠️/❌, P4).
2. **Re-rode a MESMA busca** (mesmos parâmetros exatos), se possível via subagente,
   e confirme que o precedente citado está no resultado.
   - Se a re-rodada não o trouxer (ranking mudou), **não remova de imediato**:
     investigue/amplie e, persistindo a dúvida, sinalize ⚠️ para decisão humana.
3. **Confira a forma da citação** contra o registro (número, órgão, data, relator)
   **como a ferramenta retornou** — o formato do tool é o autoritativo; corrija a
   peça se divergir.
   - **Transcrição via `@citacao-ref`:** se a ementa foi colada por referência
     (`citar.py` extrai verbatim do transcript), o **texto** já é fiel por
     construção — não há transcrição manual a auditar. Resta confirmar que o
     `processo` casa com um registro do rastro e que a *ratio* (passo 4) sustenta o
     ponto. Só há transcrição manual a conferir em `@citacao` escrito à mão.
4. **Diz o que se afirma?** Leia o **inteiro teor** (não a ementa isolada) e confirme
   que a tese atribuída é a *ratio decidendi* — não um obiter nem leitura invertida.
5. **Está vigente?** Não foi superado/overruled? Cruze com jurisprudência recente
   (filtro de data). Súmula: enunciado transcrito ao pé da letra e não cancelada.

### B. Legislação (via Know-How Jurídico)
- **Existe e está vigente?** O dispositivo não foi revogado nem teve a redação
  alterada. Conferir no Know-How (lei comentada) a redação **atual**.
- **Transcrição fiel?** O texto citado bate literalmente com a fonte.
- **Interpretação sustentável?** O sentido atribuído ao dispositivo se sustenta.

### C. Doutrina (via Know-How Jurídico)
- **A obra/autor existe e a passagem diz aquilo?** Confira com `ler_fonte`. Não
  atribuir a um autor tese que ele não sustenta.

### D. Referências aos autos (via workspace do processo)
- Cada fls./ID/evento/documento citado bate com a saída da `analise-processo-pje`
  (`${CLAUDE_PLUGIN_DATA}/processos/<numero-cnj>/`)? Nomes e qualificações corretos?

### E. Números, datas e coerência
- Valores, prazos e datas conferem com os autos.
- Coerência interna: pedidos ↔ fundamentos ↔ fatos; datas de tempestividade
  consistentes com o marco de intimação.

## Passo 3 — Relatório de verificação (com veredito)
Para cada item do inventário, um veredito com evidência:
- **✅ CONFERIDO** — com a fonte/onde foi confirmado.
- **⚠️ SUSPEITO** — com o motivo (ementa não confirma a ratio, redação divergente,
  possível superação…).
- **❌ NÃO LOCALIZADO / DIVERGENTE** — a fonte não confirma ou contradiz.

**Regra dura (gate):** nenhum item ⚠️ ou ❌ vai para o documento final sem
resolução. Para cada um: (a) corrigir citando a fonte real, (b) remover a
alegação, ou (c) sinalizar ao usuário para decisão humana. Em peça, a entrega
(`formatacao-entrega`) só ocorre depois de o relatório estar limpo ou os pontos
sinalizados terem sido decididos pelo usuário.

## Como rodar (higiene de contexto)
- A verificação pode ser **delegada a subagente(s)**, um por citação ou por lote,
  cada um com a postura adversarial do P3 e devolvendo o veredito. Isso mantém o
  contexto principal limpo e adiciona independência.
- Mas o veredito "a ratio corresponde" exige **ler o inteiro teor** — não aceite
  resumo de resumo para esse ponto.

## Ligação com o pipeline
- Puxada por toda skill de output antes de fechar (obrigatória em peças).
- Reaproveita as mesmas fontes da `pesquisa-juridica` (juris_br, Know-How) e o
  workspace da `analise-processo-pje`.

## TODO
- [ ] (Opcional) formato-padrão do relatório de verificação para anexar ao workspace.
