---
name: peca-simples
description: Redige petição sem forma própria no CPC (manifestação, juntada, ciência, cumprimento de despacho, requerimento de provas) no porte que o comando pede, de um parágrafo protocolar a uma manifestação desenvolvida. Não use para peça com previsão própria nem para recurso.
---

# Peça simples

"Simples" quer dizer sem previsão específica no CPC, não curta. O porte vem do
**comando** (do José ou do despacho que intimou a parte), por um teste: **o leitor
precisa ser convencido de algo?** Não → trilho protocolar (N1). Sim → trilho substancial
(N2/N3). Inflar a protocolar é defeito tão grave quanto rasar a substancial. Chamada fora
do pipeline, assuma N1 no protocolar e N2 no substancial.

## 1. Comando e porte
- Leia no workspace o despacho ou a decisão que intimou e extraia exatamente o que o
  juízo pede; o comando do José, se houver, prevalece.
- No máximo uma pergunta, só se o despacho não deixar claro, com comando e porte juntos
  (*"o despacho de id N pede X; petição de um parágrafo ou manifestação desenvolvida?"*).
- Responda exatamente ao comando: nem menos (pedido do juízo sem resposta), nem mais; o
  vício mais comum é o segundo.

## 2. Trilho protocolar (N1)
Só comunica, requer o rotineiro ou cumpre: juntada, ciência, dilação de prazo,
cumprimento de despacho, habilitação de patrono. Sem plano, sem pesquisa, uma geração,
direto ao `.docx` (`formatacao-entrega`). Não carregue a `escrita-juridica` inteira;
basta este modelo:

```
@enderecamento
[Juízo da causa, como consta da capa dos autos]
@identificacao
Processo nº 1234567-89.2024.4.05.8100
@corpo
[PARTE], já qualificada nos autos, vem, por seus advogados, em atenção ao despacho de
id [N], [informar ou requerer o ato, em uma frase].

[Se preciso, um segundo parágrafo: o documento ou o fato que sustenta o pedido, com o id.]
@fecho
Nestes termos, pede deferimento.
@data
[Local], [data].
@assinatura
[Advogado(a)]
OAB/[UF] [número]
```

Três vedações de estilo:
1. Nenhum traço para intercalar ideia; a intercalação vai entre vírgulas.
2. Cortesia e latim em dose única: nada de "data venia" em série nem adjetivo ao julgador.
3. Nada além do ato: sem fundamentar o rotineiro, antecipar objeção ou resumir o processo.

Verificação: as referências aos autos (id, datas) e a lei, se citada.

## 3. Trilho substancial (N2/N3)
Há mérito ou posição a defender: manifestação sobre laudo, sobre proposta de acordo com
contrapontos, impugnação incidental. Segue o `plano-de-respostas` como qualquer peça, com
estrutura livre guiada pelo comando e atrelada aos fatos. Pesquisa só se houver mérito
jurídico; escrita, entrega e verificação no padrão do nível.
