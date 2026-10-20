---
name: pesquisa-juridica
description: Pesquisa o fundamento de peça ou relatório, lei e doutrina no Know-How antes da jurisprudência no juris_br, com rastro por ID e profundidade pelo nível. Não use para conferir citações prontas (verificacao-citacoes) nem para estudo acadêmico.
---

# Pesquisa jurídica

Dona única do "como buscar". Roda por geração, chamada pelo `plano-de-respostas` ou pela
skill de saída; fora do pipeline, assuma N2.

## Regras
- **R1 — Fonte antes de afirmar.** Nenhuma tese, nem o teor de um artigo de lei, sai do
  conhecimento do modelo: abra e leia a fonte. Lei e doutrina no Know-How antes da
  jurisprudência; a lei fixa a premissa, a doutrina a desenvolve e a jurisprudência
  confirma ou corrige (passes A e B do `plano-de-respostas`).
- **R2 — Data quando o tema exigir.** Onde o entendimento pode ter mudado, filtre por
  data e suba a escada: últimos 5 anos; sem resultado relevante, 10; depois, sem corte.
  Súmula se pesquisa atravessando os cortes, focada no enunciado ("Súmula 461 do STJ").
- **R3 — Não inventar julgado.** Só se cita o que veio da busca; sem resultado, diga "Não
  localizei precedentes sobre este ponto." Na dúvida entre citar e não citar, não cite.

## Profundidade pelo nível
| Nível | Pesquisa |
|---|---|
| N1 | Nenhuma; se a peça citar lei, leia o dispositivo. |
| N2 | Uma linha focada por geração: dispositivo e doutrina; jurisprudência quando o ponto pedir. |
| N3 | Por tópico: lei, doutrina e jurisprudência, com busca do precedente qualificado. |
| N4 | Conforme a equipe. |

Perfil de pesquisa, anotado no plano de cada geração (não é o reranking das ferramentas):
- `processual` (admissibilidade, cabimento, preliminares, competência): profundidade
  variável. Em regra assentada, o artigo do CPC e a doutrina no Know-How bastam;
  jurisprudência quando o José enfatizar a questão ou ela estiver em disputa nos autos.
  Pode exigir mais esforço que o mérito, sobretudo em RE/REsp; na dúvida, declare a
  profundidade em uma linha e siga.
- `mérito`: a tese de fundo, uma linha de pesquisa por tese ou causa de pedir do plano.

## Lei e doutrina — Know-How Jurídico
`ler_orientacao` primeiro: confirma que o conector é o Know-How Jurídico (há outro com os
mesmos nomes de ferramenta) e traz método e matérias. `buscar_fontes` é a entrada
principal; `listar_materias` e `listar_fontes` só quando a busca não acertar. Com
`ler_fonte`, leia o dispositivo e a seção de doutrina antes de redigir (R1).

## Jurisprudência — juris_br
Cobre tribunais superiores, TRFs, tribunal estadual e órgãos administrativos, conforme a
lista viva. Bases, parâmetros, filtros e pausas mudam: antes da primeira busca numa base,
leia a descrição da ferramenta e, para valores exatos de filtro, o `*_listar_filtros`.
- **Consulta:** a questão jurídica em 1 a 3 frases, com fatos, partes e tese, nunca
  palavra-chave solta; termos exatos (súmula, artigo, tema) no campo lexical.
- **Base pela matéria:** tributário federal administrativo → CARF e Soluções de Consulta;
  controle externo → TCU; segundo grau → o TRF ou o TJ da causa.
- **Precedente qualificado (N3):** a prática não pode perder o vigente. Use o reranking
  por importância que a ferramenta oferecer ou fracione por órgão: STF, Pleno e Turmas;
  STJ, Seção e Turmas da matéria (público: 1ª Seção, 1ª e 2ª Turmas; privado: 2ª Seção,
  3ª e 4ª; penal: 3ª Seção, 5ª e 6ª; processual: Corte Especial, 1ª e 2ª Seções e uma
  busca sem órgão, porque a regra geral se aplica conforme o direito material de fundo).
- **Vigência:** no recorte recente, os acórdãos seguem e citam o precedente que rege; se
  não seguem, suspeite de superação. Para escrever com densidade, leia o inteiro teor do
  qualificado (repetitivo, repercussão geral, controle concentrado).
- **Variar os termos** só se a primeira rodada (órgão e data) não trouxer o que se busca.
- **Reforço do mesmo nível:** para sustentar que um argumento é decisivo, precedente
  favorável de tribunal do nível do recorrido mostra que a tese não é excêntrica. Trie
  pelo resultado (fora o desfavorável, o de atividade diversa, o de histórico confuso) e
  anote o motivo do descarte no rastro.
- **Inteiro teor:** a cobertura varia por base e período (a descrição de cada
  `*_inteiro_teor` diz qual). Onde não há, cite a ementa e diga a limitação. Precedente
  decisivo antigo do STJ fora da cobertura → `references/inteiro-teor-navegador.md`.

Armadilhas conhecidas (confira na descrição da ferramenta):
- o `ponto_id` do STJ é inteiro grande: passe-o como string, senão a reabertura falha;
- ementa longa pode vir truncada na busca: reabra por `*_detalhes_*` antes de citar, e
  cite a ratio (o item que decide), não o cabeçalho, que pode misturar deferido e
  indeferido;
- o conector do STJ às vezes entrega "?" no lugar da aspa de abertura: anote no rastro.

## Rastro — `pesquisas.jsonl`
Toda busca e toda leitura do Know-How que sustentarem o texto viram uma linha JSON em
`<workspace>/pesquisas.jsonl` (o caminho que `processo.py workspace <cnj>` imprime; fora
de processo, ao lado do texto, dizendo onde), com `geracao`, `ferramenta` (nome exato),
`parametros` (todos, como enviados), `usados` (por precedente: o `id` que a busca mostrou,
o `numero` como a ferramenta devolveu, órgão, data, relator) e `descartados` (com o
`motivo`). O ID é a chave: a `verificacao-citacoes` reabre cada precedente por
`*_detalhes_*`, sem repetir a busca nem buscar por número. E o número sai como a
ferramenta o devolveu (evita `1.234.567` × `1234567`).

## Volume
Buscas em lote (várias bases, órgãos ou janelas) vão a um subagente Sonnet, que roda,
grava o rastro e devolve a síntese (por precedente: ID, número, órgão, data, a frase da
ementa que importa e se serve). A confirmação dos precedentes decisivos, reabertos por ID
e lidos na íntegra, fica com você; a conferência final, com a `verificacao-citacoes`.
