---
name: relatorio
description: Relata a situação de um processo para o escritório ou o cliente, com fatos comprovados, riscos e próximos passos.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.


# Relatório (camada D, modo interno|externo)

Skill de output fina. **Não é peça protocolada** → **não puxa** `peca-processual-base`
(sem endereçamento/estrutura de peça). Puxa `escrita-juridica` (registro
`interno`/`externo`), `pesquisa-juridica` (quando necessário) e, no modo externo,
`formatacao-entrega`.

## 1. Quando ativar
Objetivo = **informar** sobre a situação do processo, não produzir peça.

## 2. Informações necessárias, aproveitar o contexto antes de perguntar
- **Destinatário:** escritório (`interno`) ou cliente (`externo`)? Se não estiver
  claro, pergunte — muda o conteúdo, não só o tom.

## 3. Estrutura do documento
- Situação atual do processo → o que está em jogo → próximos passos.
- **Só no `interno`:** riscos, **probabilidade de êxito** e recomendação
  estratégica.
- Fatos vêm do workspace (`analise-processo-pje`), reabrindo os documentos relevantes quando necessário.

## 4. Plano de respostas (segmentação)
- Normalmente **1 geração**. Segmente se cobrir vários processos ou muitos temas.

## 5. Pesquisa
- Serve de **base interna** do que se afirma (ex.: embasar a avaliação de risco no
  modo interno). Ao **cliente**, normalmente **não se cita** jurisprudência/lei — a
  pesquisa fica nos bastidores.

## 6. Escrita
`escrita-juridica`:
- `interno` → franco, técnico, "raw"; pode expor probabilidade e estratégia.
- `externo` → acessível, institucional; **filtra conteúdo** (sem probabilidade crua
  nem estratégia interna) e comunica risco com prudência.

## 7. Entrega
- `externo` → `formatacao-entrega` (`.docx`; timbre depende de asset fornecido), usando o **subconjunto**
  aplicável de `@tag` (ex.: `@titulo`, `@corpo`, `@secao`, `@data`, `@assinatura` —
  sem `@enderecamento`/`@identificacao`/`@pedidos`).
- `interno` → markdown simples; dispensa `.docx`/timbrado.

## 8. Verificação
`verificacao-citacoes` se afirmar algo que dependa de fonte (lei, jurisprudência,
dados dos autos).

## 9. Regras de ouro / vícios a evitar
- **Externo nunca omite** a situação negativa, mas **equilibra com a solução** (ex.:
  "a decisão foi desfavorável, mas já preparamos o recurso cabível, inclusive com
  tema de repercussão geral favorável").
- **Externo não expõe** probabilidade crua de êxito nem a estratégia interna.
- **Interno é franco:** descrição direta, sem verniz de cliente.

Não atribua percentuais de êxito sem base explícita; apresente avaliação qualitativa e suas razões. Não afirme recurso preparado ou solução existente sem evidência.
