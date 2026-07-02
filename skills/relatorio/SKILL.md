---
name: relatorio
description: (camada D) Produz RELATÓRIO sobre o processo, em modo interno (para o escritório — franco, "raw", com riscos, probabilidade de êxito e estratégia) ou externo (para o cliente — acessível, institucional). O modo externo FILTRA conteúdo (sem probabilidade crua nem estratégia interna) e equilibra a situação negativa com a solução, sem omitir. Use quando o objetivo é informar sobre o processo, não redigir peça.
---

# Relatório (camada D, modo interno|externo)

Skill de output fina. **Não é peça protocolada** → **não puxa** `peca-processual-base`
(sem endereçamento/estrutura de peça). Puxa `escrita-juridica` (registro
`interno`/`externo`), `pesquisa-juridica` (quando necessário) e, no modo externo,
`formatacao-entrega`.

## 1. Quando ativar
Objetivo = **informar** sobre a situação do processo, não produzir peça.

## 2. Perguntas antes de começar
- **Destinatário:** escritório (`interno`) ou cliente (`externo`)? Se não estiver
  claro, pergunte — muda o conteúdo, não só o tom.

## 3. Estrutura do documento
- Situação atual do processo → o que está em jogo → próximos passos.
- **Só no `interno`:** riscos, **probabilidade de êxito** e recomendação
  estratégica.
- Fatos vêm do workspace (`analise-processo-pje`), não de releitura.

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
- `externo` → `formatacao-entrega` (`.docx`/timbrado), usando o **subconjunto**
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
