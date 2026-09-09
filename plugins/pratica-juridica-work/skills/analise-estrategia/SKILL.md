---
name: analise-estrategia
description: Analisa um processo e compara estratégias, cenários e riscos, sem redigir peça salvo pedido do usuário.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.


# Análise / Estratégia (camada D)

Skill de output fina. **Não é peça** → não puxa `peca-processual-base` nem
`formatacao-entrega`. Puxa o workspace da `analise-processo-pje`, a
`pesquisa-juridica` (sob demanda) e a `escrita-juridica` (registro `interno`).

## 1. Quando ativar
O usuário quer **entender** o processo ou **planejar estratégia**, sem pedir peça.
Também serve de **fase preliminar**: entender/planejar primeiro e, em seguida, o
orquestrador roteia para uma skill de peça.

## 2. Informações necessárias, aproveitar o contexto antes de perguntar
- Qual o **foco**? Dúvida pontual / panorama geral / avaliação de risco / definição
  de próximos passos.
- Se for **preliminar a uma peça**, confirme o objetivo final para orientar a
  análise (o que se vai fazer com o processo muda o que é relevante).

## 3. Estrutura do documento
Livre, tipicamente: panorama do processo → questões-chave → cenários e riscos →
recomendação → próximos passos. Fatos vêm do workspace.

## 4. Plano de respostas (segmentação)
- Normalmente **1 geração**. Segmente por questão se a estratégia for densa.

## 5. Pesquisa
- **Sob demanda.** Se a estratégia depende de uma tese (ex.: viabilidade de um
  recurso, chance de uma tutela), aciona `pesquisa-juridica`. Pode ser leve; nem
  toda análise precisa de pesquisa.

## 6. Escrita
`escrita-juridica`, registro `interno` (franco, técnico — é para você/o escritório).
Markdown simples.

## 7. Entrega
Interno; formato simples. Sem `.docx`/timbrado.

## 8. Verificação
`verificacao-citacoes` se a análise citar lei/jurisprudência/dados dos autos.

## 9. Regras de ouro
- **Não vira peça** — é análise/estratégia. Se o usuário decidir seguir para um
  documento, o resultado desta skill serve de **insumo**, e o orquestrador roteia
  para a skill de peça adequada.
- Seja franco sobre fraquezas e riscos (é uso interno) — o objetivo é decidir bem,
  não convencer ninguém.
