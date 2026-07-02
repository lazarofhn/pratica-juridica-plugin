---
name: analise-processual
description: PORTA DE ENTRADA do fluxo de prática jurídica. Use quando o usuário quiser fazer QUALQUER coisa a partir de um processo — compreender/planejar estratégia, redigir peça (recurso, contestação, réplica, manifestação, impugnação, embargos à execução…), fazer um memorial, ou gerar um relatório (para o escritório ou para o cliente). Esta skill lê o objetivo, garante o acesso ao processo, dispara a análise seletiva, monta o plano de respostas e roteia para a skill de output correta.
---

# Análise Processual — Orquestrador (camada A)

Esta skill **não escreve o output final**: ela **decide o caminho** e chama as
skills certas na ordem certa. O objetivo do usuário guia tudo.

## Fluxo

### 1. Definir o objetivo e rotear
Identifique o output desejado (pergunte ao usuário se ambíguo) e roteie:

| Objetivo do usuário | Skill de output |
|---|---|
| Só **entender** o processo ou **planejar estratégia** (sem peça) | `analise-estrategia` |
| **Recurso** — incl. **embargos de declaração** (é recurso!), apelação, agravo, RE/REsp | `peca-recurso` |
| Peça **específica** com previsão própria no CPC — contestação, réplica, impugnação ao cumprimento de sentença, **embargos à execução / de terceiro** | `peca-especifica` |
| Petição **simples** — sem nomenclatura/requisitos próprios no CPC; guiada pelo comando (do usuário ou do despacho que intimou) | `peca-simples` |
| **Memorial** (entregue ao julgador, processo pendente de julgamento) | `memorial` |
| **Relatório** para o escritório ou para o cliente | `relatorio` (modo `interno`\|`externo`) |

Notas de roteamento:
- ⚠️ **Embargos de declaração = recurso** → `peca-recurso`. Só embargos que são
  incidentes/ações (à execução, de terceiro) vão para `peca-especifica`.
- `analise-estrategia` pode ser **fase preliminar**: entender/planejar primeiro e,
  em seguida, rotear para uma skill de peça.

### 2. Garantir acesso ao processo (camada B)
- **Default:** o usuário aponta o PDF da íntegra já baixado.
- Se pedir download automático → `obter-processo` (opcional, por sistema).
- Antes de reprocessar, verifique se já existe workspace deste processo (ver
  "Persistência").

### 3. Analisar seletivamente (camada C)
Chame `analise-processo-pje` COM o objetivo já definido — ele guia quais peças são
estratégicas, extrai só o necessário para `.md` e as lê a fundo. Não leia o
processo inteiro no contexto.

### 4. Montar o PLANO DE RESPOSTAS (sempre, antes de escrever)
Chame `plano-de-respostas`: índice numerado do documento + decisão de **quantas
gerações** a redação terá.
- **Se N > 1 gerações (peça grande):** apresente o plano ao usuário e **aguarde
  aprovação** antes de escrever.
- **Se 1 geração:** siga direto.
- `analise-estrategia` e a maioria dos `relatorio` tendem a 1 geração.

### 5. Produzir o output (camada D → puxa camada E)
Entregue o controle à skill de output escolhida, executando o plano da etapa 4.
Conforme o caso, a skill de output puxa da camada E:
- `peca-processual-base` — orientações comuns às peças protocoladas (recurso,
  específica, simples; parcialmente o memorial);
- `pesquisa-juridica` — perfis `processual|material`, fontes juris_br + know-how;
- `escrita-juridica` — registro `peça|interno|externo`;
- `plano-de-respostas` — para escrever seção a seção quando N > 1;
- `formatacao-entrega` — só outputs externos (→ `.docx`/timbrado);
- `verificacao-citacoes` — **antes de fechar** (obrigatório em peças).

## Persistência (workspace do processo)
Cada processo tem uma pasta reutilizável (peças convertidas em `.md`, `resumo.md`,
`linha-do-tempo.md`). O caminho **não é fixo**: é resolvido pela `analise-processo-pje`
(`processo.py workspace <numero-cnj>`) para um diretório **gravável** conforme o ambiente
(`PRATICA_JURIDICA_DATA` → `$CLAUDE_PLUGIN_DATA` → `dados-juridicos/` auto-detectada →
`./outputs`; no Cowork o `.claude/plugins/data` é read-only). Antes de reprocessar,
cheque e reaproveite. **No Cowork, a persistência é automática desde a primeira
sessão**: havendo pasta do usuário montada, crie nela `dados-juridicos/` (se ainda não
existir) antes de resolver o workspace — o script a detecta sozinho dali em diante
(regra detalhada em `analise-processo-pje`, "Ambiente e caminhos"). Sem pasta montada,
os dados valem só na sessão, salvo `PRATICA_JURIDICA_DATA` definido.

## TODO
- [ ] Definir o formato do número CNJ como chave do workspace.
- [ ] Escrever a heurística de "objetivo ambíguo → o que perguntar" (ex.: recurso
      omitido → confirmar cabimento antes de confeccionar).
- [ ] Fixar o gatilho automático de segmentação em `plano-de-respostas`.
