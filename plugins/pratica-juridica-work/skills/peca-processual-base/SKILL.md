---
name: peca-processual-base
description: Aplica endereçamento, requisitos e coerência entre fatos, fundamentos e pedidos na redação de peças processuais.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.


# Peça Processual — Base Comum (camada E)

Base compartilhada. **Não é chamada direto pelo usuário** — as skills de peça
(`peca-recurso`, `peca-especifica`, `peca-simples`) a puxam e sobrepõem a sua
ênfase própria. O `memorial` reaproveita partes (endereçamento, pesquisa), mas tem
regra própria (não inova ratio).

## 1. Endereçamento
Toda peça protocolada é dirigida ao **órgão competente**, e o endereçamento muda
conforme o tipo:
- **1º grau:** ao juízo da vara/competência onde tramita o feito.
- **Recursos:** conforme o recurso — ao juízo *a quo* (que fará o juízo de
  admissibilidade) ou diretamente ao tribunal *ad quem*, seguindo o que o CPC
  prevê para aquele recurso.
- Confirmar o órgão correto a partir dos autos (capa/andamento no workspace) e do
  tipo de peça. Na dúvida sobre competência, é questão processual → ver seção 3.

> TODO (José): colar aqui os modelos de endereçamento da casa (fórmulas exatas por
> instância/tribunal) + o padrão de papel timbrado (delegado à `formatacao-entrega`).

## 2. Estrutura padrão
Esqueleto genérico, **subsegmentável pelo `plano-de-respostas`**:

```
1. Endereçamento
2. Qualificação / referência ao processo
3. Fatos (síntese do necessário — puxar do workspace, sem reescrever o processo)
4. Admissibilidade / Cabimento (quando aplicável ao tipo de peça)
5. Fundamentos (jurídicos — um por tese/causa de pedir; subdivide se denso)
6. Pedidos (claros, específicos e coerentes com os fundamentos)
```

A **fonte da estrutura** definitiva vem de cada skill de peça (ex.: o artigo do
CPC que regula aquele recurso/peça); este é o fallback comum.

## 3. Pesquisa processual (admissibilidade / cabimento / incidentes)
Profundidade **variável** — calibre pelo contexto:
- Em regras processuais assentadas, confira a fonte aplicável no conector **Know-How Jurídico**: o artigo do CPC que
  rege o instituto + o capítulo de doutrina do tema (ver `pesquisa-juridica`,
  perfil `processual`).
- Acione **jurisprudência** (juris_br) quando: o usuário enfatizar a questão
  processual, **ou** ela estiver sendo muito discutida no processo.
- Aprofunde conforme a controvérsia e a evidência disponível; pergunte quando a dúvida alterar materialmente a estratégia.

> A profundidade da parte processual pode, em certos casos, exigir esforço **maior**
> que a do direito material. Não trate como sempre secundária.

## 4. Pesquisa material (mérito)
- **Segmentada por assunto** conforme o `plano-de-respostas` (uma linha de pesquisa
  por tese/causa de pedir).
- Buscar em **juris_br** (jurisprudência) + **Know-How Jurídico** (lei comentada +
  doutrina), via `pesquisa-juridica` (perfil `mérito`).
- Sempre ler a fonte inteira antes de citar; a conferência final é da
  `verificacao-citacoes`.

## 5. Ligação com o pipeline
- **Fatos e provas** vêm do workspace do processo (saída da `analise-processo-pje`),
  não de releitura do PDF inteiro.
- **Segmentação da escrita:** `plano-de-respostas` (roda antes; se N gerações,
  escrever seção a seção acumulando).
- **Escrita:** `escrita-juridica` com registro `peça`.
- **Entrega:** peça protocolada é output externo → `formatacao-entrega`
  (`.docx`; timbre depende de asset fornecido).
- **Antes de fechar:** `verificacao-citacoes` (obrigatório).

## 6. Boas práticas / vícios a evitar (comuns a toda peça)
- **Coerência fatos → fundamentos → pedidos**: cada pedido deve ter fundamento; cada
  fundamento deve amarrar num fato/direito.
- **Pedidos claros e específicos** (nada de pedido genérico que o juízo não consiga
  deferir objetivamente).
- **Citar a procedência** ao referir os autos: tipo do documento, evento (NUM) e
  páginas (como a `analise-processo-pje` já entrega).
- **Não reescrever o processo inteiro** na seção de fatos — só o necessário à tese.
- **Antecipação de objeção — oportunidade e lugar.** Duas regras:
  - *Oportunidade:* antecipa-se apenas a objeção **provável e específica** do caso
    concreto; **não** se antecipa o que é o desenho normal da ação. Defender o óbvio
    "só abre uma suspeita infundada e dá material" à parte contrária — a antecipação
    sinaliza dúvida onde não havia. Objeção meramente possível fica guardada para a
    réplica/contrarrazões, se levantada.
  - *Lugar:* quando couber antecipar, faz-se no corpo da **fundamentação**, nunca no
    capítulo de pedidos — **pedido que se defende é pedido que se confessa frágil**.
- Sem juridiquês vazio nem excesso de "data venia" (ver `escrita-juridica`).

## 7. O que cada skill de peça acrescenta (ênfase própria)
| Skill | Ênfase que sobrepõe a esta base |
|---|---|
| `peca-recurso` | Admissibilidade média-alta por padrão; **RE/REsp: tratamento específico dos requisitos**; estrutura do artigo do CPC do recurso. |
| `peca-especifica` | Previsão/nomenclatura própria no CPC; requisitos daquela peça; sem ênfase-padrão de admissibilidade. |
| `peca-simples` | Guiada pelo comando (usuário/despacho); atrelada a fatos; **porte ditado pelo comando** (bifurcação protocolar × substancial — não presumir em nenhuma direção). |
