---
name: peca-especifica
description: Redige peça com previsão própria no CPC a partir dos autos, como contestação (com a reconvenção, se houver), réplica, impugnação ao cumprimento de sentença, embargos à execução ou de terceiro. Não use para embargos de declaração (recurso) nem petição sem forma própria.
---

# Peça específica

Nível típico: N2; N3 com várias causas de pedir densas ou risco alto. Chamada fora do
pipeline, assuma N2. Precondições: workspace com a peça ou o ato a que se responde
extraído, e plano pelo `plano-de-respostas` antes de redigir.

## 1. Identificar a peça (regra de ouro)
A previsão e a nomenclatura corretas definem a estrutura e os requisitos. Pergunte só se o
pedido for ambíguo; citação, intimação e prazo que autorizam a peça são dados dos autos
(anote-os no `plano.md`). Bordas:
- Embargos de declaração são recurso → `peca-recurso`. Aqui, só os embargos que são ação
  ou incidente (à execução, de terceiro).
- Reconvenção não é peça à parte: vai na própria contestação (CPC, art. 343).
- Não há mais "exceções" autônomas: a incompetência é preliminar da contestação (art.
  337, II); impedimento e suspeição se arguem em petição específica (art. 146).
- A exceção de pré-executividade não tem artigo no CPC, mas tem nomenclatura e requisitos
  firmados pela jurisprudência (Súmula 393/STJ: matéria conhecível de ofício, sem
  dilação probatória). Trate-a aqui, com a estrutura vinda da jurisprudência e da doutrina.

## 2. Estrutura e segmentação
- Localize a previsão da peça e leia os requisitos próprios na fonte, não de memória.
  Ex.: contestação = preliminares + mérito rebatendo cada causa de pedir + resposta a
  eventual tutela + pedidos; impugnação ao cumprimento, só as matérias que a lei admite.
- Uma geração por tópico de núcleo (`plano-de-respostas`, Passo 1); cada preliminar ou
  matéria com a sua base legal.
- Peça de resposta (contestação, réplica, impugnação): nenhuma causa de pedir fica sem
  enfrentamento e, na contestação, todo fato alegado se impugna (impugnação
  especificada, art. 341: o fato não impugnado se presume verdadeiro). O espaço, porém,
  segue o peso: o que decide a causa se desenvolve, o fato secundário se impugna numa
  oração ou numa lista, e a resposta não copia o índice da peça adversa.
- Sem a ênfase de admissibilidade dos recursos; os requisitos próprios da peça, sim.

## 3. Pesquisa
Mérito: uma linha por causa de pedir ou matéria. Processual: CPC comentado e doutrina
bastam; jurisprudência processual só se o José enfatizar a questão ou ela for muito
discutida no processo. Escrita (registro `peça`), entrega (`.docx`) e verificação seguem
o padrão do nível.
