---
name: pesquisa-juridica
description: (camada E — compartilhada) Método de pesquisa de FUNDAMENTAÇÃO jurídica para prática, cobrindo lei e doutrina (conector Know-How Jurídico) e jurisprudência (conector juris_br: STJ/STF + TCU/CARF/RFB/TRF5), com PERFIS parametrizáveis (admissibilidade|mérito|processual). Duas regras inegociáveis: (1) bloqueio de fonte — nunca afirmar sem antes abrir e ler a lei/doutrina aplicável; (2) filtros sempre que possível na jurisprudência (no mínimo data, para o entendimento vigente). As skills de output (camada D) a invocam com o perfil adequado.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Pesquisa Jurídica (camada E — prática)

Uma skill de pesquisa, várias FONTES e vários PERFIS. Não é chamada direto pelo
usuário — as skills de peça/relatório a puxam. Escopo: **prática** (peças,
pareceres, relatórios); não cobre pesquisa acadêmica/estudos.

## Regras globais (inegociáveis, acima dos perfis)

### R1 — Bloqueio de fonte: cheque ANTES do "conhecimento próprio"
Nunca afirme uma tese — nem mesmo o teor de um artigo de lei — sem antes **abrir e
ler a fonte**. Se há legislação aplicável, leia o(s) artigo(s) que incidem **e** a
seção de doutrina do tema no **Know-How Jurídico** antes de redigir. É proibido
partir direto para o conhecimento do modelo sem ter aberto a fonte, ainda que
pareça um simples texto de lei.

### R2 — Filtros sempre que possível (jurisprudência)
Toda busca de jurisprudência deve usar filtros para ganhar precisão. **No mínimo,
filtro de data**, para trazer o entendimento vigente e não citar precedente
superado (peça com precedente defasado é um risco). Quando couber, some filtro de
**órgão julgador** e, no STF, **repercussão geral**.

### R3 — Nunca inventar julgado
Cite apenas precedente que exista de fato no resultado da busca do MCP. Se não
houver, diga expressamente: "Não localizei precedentes sobre este ponto." Nunca
deduza ou reconstrua julgados. Na dúvida entre citar e não citar, **não cite**. (A
conferência final é da `verificacao-citacoes`.)

---

## Pilar 1 — Lei + doutrina (conector Know-How Jurídico)
Acervo organizado por área do Direito (doutrina em `.md` por capítulo; leis por
seção comentada). Navegue pelo índice, como na `analise-processo-pje`:

1. **`ler_orientacao` PRIMEIRO** — método + lista atual de matérias.
2. `listar_materias` → escolha a área.
3. `listar_fontes` → veja livros (doutrina) e leis (legislação) da área.
4. `buscar_fontes` → busca semântica pelo artigo/capítulo/seção certo.
5. `ler_fonte` → **LEIA** o artigo aplicável **+** a seção de doutrina do tema (R1).

Ordem natural: **lei → doutrina** (a lei fixa a premissa; a doutrina a desenvolve).

---

## Pilar 2 — Jurisprudência (conector juris_br)

### 2.1 Busca híbrida (preencher as duas camadas)
Cada busca combina duas camadas (Reciprocal Rank Fusion); preencha ambas:
- **`consulta`** (semântica): uma frase descritiva de 1–3 períodos, com fatos,
  partes e tese — o embedding rende mais com contexto que com palavras soltas.
- **`termos_texto`** (lexical): lista de termos exatos a casar na ementa (nº de
  súmula, artigo de lei, expressão técnica). Sempre lista, ainda que com um termo.

### 2.2 Filtros nativos (usar sempre que possível — R2)
- `ano_inicio` / `ano_fim`: faixa de ano (corte respeitado → janelas disjuntas).
- `orgao_julgador` (valores exatos):
  - STJ: `PRIMEIRA TURMA`…`SEXTA TURMA`, `PRIMEIRA SECAO`…`TERCEIRA SECAO`, `CORTE ESPECIAL`.
  - STF: `Tribunal Pleno`, `Primeira Turma`, `Segunda Turma`.
- STF: `repercussao_geral` (`Sim`/`Nao`) — isola precedente de RG.
- **Cobertura do inteiro teor do STJ:** `stj_inteiro_teor` só cobre publicações a
  partir de 04/01/2021. Para acórdãos anteriores, a ferramenta devolve só a URL do
  PDF — nas janelas antigas a ementa é o artefato principal.
  - **Fallback p/ inteiro teor antigo (pré-2021) via navegador:** quando o
    precedente é decisivo (ex.: voto do repetitivo), baixe o PDF pela skill
    `claude-in-chrome` (a "verificação automática" Cloudflare do STJ passa sozinha na
    sessão do usuário; `curl` cai em captcha). Atenção: o MESMO `numero_registro`
    tem vários documentos por `dt_publicacao` (acórdão principal × EDcl) — confira a
    data. O botão de download do visualizador de PDF salva direto em Downloads.
    Converta com `pdftotext -layout -enc UTF-8` para dentro do workspace e cite via
    `@citacao-ref fonte: autos` + `arquivo: <nome>.md` (o `citar.py` já remove o
    rodapé "Documento: N - Inteiro Teor..." do STJ).
- **Disponibilidade de inteiro teor por fonte:** confiável em **CARF, Soluções de
  Consulta (RFB) e TCU**; **STJ/STF** têm poucos; **TRF-5 não tem**. Logo, a citação
  padrão é pela **ementa**. Trecho de **voto** (que exige inteiro teor) só sob
  **pedido explícito** do usuário; se for colega usando o plugin, **avise** da
  limitação em vez de fingir cobertura.
- **Pegadinha do TRF-5 — ementa TRUNCADA na busca.** `trf5_buscar_jurisprudencia`
  corta ementas longas (some a fundamentação; sobra só o cabeçalho de palavras-chave).
  **Antes de citar, chame `trf5_detalhes_acordao` para a ementa íntegra** — o cabeçalho
  costuma **misturar itens deferidos e indeferidos**, e citar só ele engana. Ex. real:
  acórdão que no cabeçalho lista "SEGURO DE CARGAS EM GERAL, RCTR-C, RCF-DC E
  RASTREAMENTO … SENTENÇA CONFIRMADA", mas cuja ementa completa **defere** RCTR-C/RCF-DC
  e rastreamento e **indefere** o seguro de cargas em geral. Cite a **ratio** (o item
  numerado que decide), não o cabeçalho. Gotcha técnica: o `ponto_id` do TRF-5 estoura
  o inteiro seguro do JSON (perde dígitos) — **passe-o como string** no `detalhes`.
  (O `citar.py` já lê o formato do `detalhes` e, havendo busca truncada + detalhes,
  prefere automaticamente a ementa mais longa.)
- **Citação sem redigitação:** a ementa que sai da busca é gravada no transcript e
  colada verbatim na peça via `@citacao-ref` (`formatacao-entrega/scripts/citar.py`).
  Preferir `@citacao-ref` a reescrever a ementa (economiza output e garante fidelidade).

### 2.3 Escada temporal (começar restrito)
1. 1ª rodada nos **últimos 5 anos**. Se vierem resultados relevantes, encerre.
2. Se não achar, amplie para os **últimos 10 anos**.
3. Se ainda não achar, rode **sem corte temporal**.

### 2.4 Fracionamento por órgão (aponta o precedente qualificado)
- **STF:** 1 busca no Tribunal Pleno, 1 na Primeira Turma, 1 na Segunda Turma.
- **STJ**, conforme a matéria:
  - **Penal:** Terceira Seção, Quinta Turma, Sexta Turma.
  - **Direito Privado:** Segunda Seção, Terceira Turma, Quarta Turma.
  - **Direito Público:** Primeira Seção, Primeira Turma, Segunda Turma.
  - **Processual Civil:** Corte Especial, Primeira Seção, Segunda Seção + 1 busca
    sem filtro de órgão (a Corte Especial fixa a regra geral, mas Primeira Seção
    (público) e Segunda Seção (privado) revelam divergência conforme o direito
    material de fundo).

### 2.5 Vigência pela data + inteiro teor do paradigma
O juris_br contém os tribunais que fixam entendimento (STJ/STF). No recorte
recente, os acórdãos tendem a seguir e citar o precedente vinculante; se não
seguem, é sinal de overruling. Logo:
- O acórdão recente já revela, por referência, o precedente histórico que rege a
  matéria.
- Para escrever um tópico com densidade, busque o **inteiro teor do precedente
  qualificado** (REsp repetitivo, RE com repercussão geral, controle concentrado).
- Quando o que rege for **súmula**, pesquise atravessando os cortes de data,
  focalizando o enunciado (ex.: "Súmula 461 do STJ").

### 2.6 Combinar variáveis de busca — subsidiária
Só acione buscas com termos diferentes para o mesmo assunto se a 1ª rodada (órgão
+ data) não trouxer nada satisfatório; então, em conjunto com os filtros.

### 2.7 Outras fontes do juris_br (quando a matéria pedir)
Mesma lógica (filtros + ler inteiro teor + R3):
- **Tributário federal (processo administrativo):** CARF (`carf_*`) e Soluções da
  RFB/Cosit (`rfb_*`).
- **Federal de 2º grau:** TRF5 (`trf5_*`).
- **Contas / controle externo:** TCU (`tcu_*`).

**Não pare no STJ/administrativo — varra também o TRF-5.** Ao fundamentar que um
argumento é **decisivo** (ex.: reforçar que a omissão do acórdão tinha o condão de
alterar o julgado), um precedente **favorável do TRF-5** é reforço valioso: é
tribunal do **mesmo nível** do TRF recorrido, logo evidencia que a tese não é
excêntrica e que outro tribunal federal a acolheria. Em subgeração B de mérito
(RE/REsp), depois de RFB/CARF, **rode `trf5_*`** e cole o que houver de favorável.
Cuidado: **triar por resultado** — descartar acórdãos desfavoráveis, de atividade
diversa (não-transportadora, p.ex.) ou de histórico processual confuso; registrar
os descartados no rastro com o motivo.

### 2.8 Rastro de pesquisa (provenance — obrigatório)
Toda busca cujo resultado for citado **deve ser registrada** no workspace do
processo, em `<workspace>/pesquisas.jsonl` (o `<workspace>` é o diretório gravável
resolvido pela `analise-processo-pje` via `processo.py workspace <numero-cnj>` — não
hardcode `${CLAUDE_PLUGIN_DATA}`, que pode ser read-only no Cowork), uma linha por
busca contendo:
- a **ferramenta exata** e **TODOS os parâmetros** usados (`consulta`,
  `termos_texto`, `ano_inicio`/`ano_fim`, `orgao_julgador`, `repercussao_geral`…);
- os precedentes selecionados **exatamente como a ferramenta os retornou** (número
  no formato do tool, órgão, data, relator, trecho da ementa).

Duas razões:
- **O formato do tool é o autoritativo.** A peça deve citar o número no formato que
  a ferramenta retornou (evita o descasamento `2.132.145` vs `2132145`).
- **Permite reconferência fiel.** A `verificacao-citacoes` re-roda a MESMA busca
  (mesmos parâmetros) em vez de tentar uma busca nova por número de processo — que o
  juris_br não suporta de forma confiável e geraria falsos negativos.

---

## Perfis (parametrização vinda da skill de peça)
- **`processual` / `admissibilidade`:** cabimento, requisitos, preliminares,
  competência. Fonte primária = CPC comentado + doutrina no Know-How (R1);
  jurisprudência processual no STJ (Corte Especial/Seções) e STF. Ênfase alta em
  recursos, sobretudo RE/REsp.
- **`mérito`:** a tese de fundo. Lei + doutrina do tema (Know-How) **e**
  jurisprudência com fracionamento por órgão da matéria. **Segmentada por assunto**
  conforme o `plano-de-respostas` (uma linha de pesquisa por tese/causa de pedir).

## Ligação com o pipeline
- Puxada pela `peca-processual-base` (pesquisa processual vs. material) e pelas
  skills de output.
- Segmentar por assunto conforme o `plano-de-respostas`.
- Ler a fonte inteira antes de citar (R1); a `verificacao-citacoes` confere no fim.

## TODO
- [ ] Revisar os valores exatos de `orgao_julgador` se a API do juris_br mudar.
- [ ] Mapear gatilhos de matéria → priorizar CARF/RFB/TRF5/TCU.
