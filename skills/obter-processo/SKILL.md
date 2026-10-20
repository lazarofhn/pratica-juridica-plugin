---
name: obter-processo
description: Baixa a íntegra dos autos no PJe pelo Chrome (TRF-1 e TRF-5; 1º grau verificado) ou consulta o andamento do processo, com os conectores de andamento antes do navegador. Não use se o PDF já foi fornecido, para ler ou analisar os autos, nem para peticionar.
---

# Obter processo (autos e andamento)

Baixar os autos é trabalho mecânico de dez a quinze cliques num sistema lento. Não fica
melhor por ser feito por um humano — só fica mais caro. Consultar o andamento é ainda
mais simples: quase sempre um conector responde sem abrir o navegador.

## Dois modos

| Modo | Pedido típico | Entrega |
|---|---|---|
| **Consulta** | "como está o processo", "saiu decisão?", "NÃO baixar a íntegra" | situação e últimos movimentos, cada dado com a fonte e a data |
| **Download** | "baixa o processo", "pega os autos", número CNJ com pedido de cópia integral | PDF da íntegra, com índice, para a `analise-processo-pje` |

Pedido ambíguo ("busca o processo X"): faça a consulta, diga o que encontrou e ofereça
o download.

## O que só o José faz

**Login e certificado digital são dele.** Nunca digite credencial, nunca preencha
senha, nunca opere token ou certificado. Se a navegação cair numa tela de login, pare
e devolva a vez: *"o PJe pediu login — faz o acesso aí que eu sigo daqui"*. Se entrar
direto nos autos, a sessão dele ainda está viva.

**Ciência de intimação também é dele.** Não abra expediente nem intimação pendente: a
consulta ao teor pode dar a intimação por realizada e abrir o prazo.

## Consulta de andamento

1. **Conectores primeiro.** Use os conectores de andamento que a sessão tiver (ex.:
   Legal One, DataJud/DJEN): respondem sem navegador e sem depender da sessão do PJe.
   Ferramentas e parâmetros estão na descrição viva de cada uma.
2. **Navegador quando eles não bastarem** — processo fora do conector, dado defasado
   ou o José quer o estado de hoje: `references/pje.md`, seção *Consulta pelo
   navegador*. Nada de download.
3. **Entregue** a situação, os últimos movimentos e as decisões ou publicações
   recentes, cada dado com a fonte e a data — conector e PJe podem divergir. Prazo, só
   o que a fonte mostrar; não deduza prazo a partir de movimento.

## Download

| Sistema | Situação | Referência |
|---|---|---|
| **PJe TRF-5 e TRF-1, 1º grau** | caminho completo verificado ao vivo (ago/2026; PJe 2.11 e 2.9.1.1) | `references/pje.md` — leia **antes** de abrir o navegador |
| **PJe TRF-5 e TRF-1, 2º grau** | caminho não percorrido; endereço do TRF-5 conferido, o do TRF-1 não | `references/pje.md` como hipótese: confira cada `id` no DOM e avise o José de que é a primeira passagem ali |
| eproc, Projudi, e-SAJ, PJe de outros tribunais | não mapeados | ver *Sistema não mapeado* |

**Painel de download: padrão fixo, sem perguntar** — cronologia crescente, todos os
documentos (nenhum filtro de tipo, ID ou período) e "Índice do PDF" marcado. Pergunte
só quando os autos prometerem passar de ~150 MB: aí o recorte é decisão do José. O
"Índice do PDF" **nunca** se desmarca: os bookmarks que ele gera são o mapa de que a
`analise-processo-pje` depende para ler autos grandes sem carregá-los inteiros.

**Espera.** O PJe monta o PDF antes de entregá-lo, e autos grandes demoram (302
documentos ≈ 21 min): demora não é falha. As armadilhas da espera e da conferência do
arquivo estão no passo 5 do `pje.md`.

**Onde o arquivo cai.** Na pasta de Downloads do computador do José. O que dá para
conferir depende do ambiente:
- **Aba Code e CLI** — você enxerga o disco: identifique o arquivo deste download,
  confira que veio inteiro e informe o caminho.
- **Cowork** — você só enxerga a pasta montada na sessão: confirme com o José que o PDF
  chegou, em vez de afirmar, e, se a análise vier a seguir, peça que ele o coloque na
  pasta montada.

## Vários processos (lote)

Lote é trabalho de horas: 21 processos do TRF-1 levaram ~6 h (07/08/2026), com dois
agentes e scripts improvisados no caminho. Para não repetir:

- **Confirme o modo.** Se o José quer saber como estão, é consulta pelos conectores —
  sem navegador, sem download.
- **Tabela de controle em arquivo** antes do primeiro processo: CNJ, grau, situação,
  arquivo, nº de documentos. Permite retomar depois de queda de sessão, comum no TRF-1.
- **Um agente no navegador, um processo por vez**, com o painel padrão e sem perguntas
  por processo. O seguinte só começa depois de identificado e conferido o arquivo do
  anterior.
- **Script, se precisar, um só e escrito no começo** — para conferir e mover por nome
  exato. A conferência mecânica dos PDFs pode ir a um subagente Haiku.
- **Avise a estimativa de tempo** no início; no fim, entregue a tabela: o que veio, o
  que falhou e por quê.

## Sistema não mapeado

Diga isso ao José de forma direta e ofereça as duas saídas: ele baixa manualmente e te
aponta o PDF (quase sempre mais rápido), ou vocês mapeiam o caminho juntos agora — você
navega, ele corrige, e no fim vocês acrescentam um `references/<sistema>.md` no formato
do `pje.md`. Não improvise um caminho às cegas em sistema desconhecido: cada um tem
armadilha própria, e adivinhar queima o tempo do José sem produzir nada.

## Regras que valem para qualquer sistema

**Não confie em coordenadas de tela.** O zoom da página e a resolução da janela
deslocam tudo; um clique em `(1458, 27)` acerta o botão hoje e erra amanhã. Localize
os elementos por seletor (`id`, `title`, texto) e clique por referência ou via
`javascript_tool`.

**Não confie no screenshot logo depois de um AJAX.** Nesses sistemas o screenshot
às vezes mostra o estado anterior da página enquanto o DOM já mudou. Quando quiser
saber se algo funcionou, leia o DOM (`javascript_tool` ou `read_page`); use o
screenshot para entender o layout, não para verificar resultado.

**Diálogos nativos (`confirm`/`alert`) congelam a aba e a extensão junto.** Se
aparecer um, você perde screenshot, JS e leitura naquela aba — não adianta insistir.
Duas saídas: prevenir (sobrescrever `window.confirm` **antes** da ação que o dispara,
como o `pje.md` ensina) ou, se já travou, `navigate` a aba de volta para a página
anterior, o que descarta o diálogo e devolve o controle.

**O override do `confirm` não atravessa abas.** Ele vale só no documento onde você o
rodou. Toda aba nova nasce com o `confirm` original — reaplique assim que ela abrir,
antes do primeiro clique. Foi exatamente aí que o caminho travou no TRF-1, depois de
todo o resto já ter dado certo.

**O override aceita qualquer `confirm` da aba.** Use-o só no caminho mapeado (aviso do
CNJ, confirmação do download). Com ele ativo, não clique fora desse caminho: qualquer
outro aviso — inclusive um de ciência de intimação — seria aceito sem que o José o
visse.

## Ao terminar

- **Download:** número do processo, classe, órgão julgador, partes e quantos documentos
  os autos têm — é o que o José precisa para conferir se veio o processo certo. Na aba
  Code e no CLI, acrescente o caminho, o tamanho e o resultado do `index`; no Cowork,
  pergunte se o PDF chegou. Se o objetivo final é peça ou análise, o PDF segue para a
  `analise-processo-pje`.
- **Consulta:** o que pede o item 3 da *Consulta de andamento*.

## Manutenção

Sistema processual muda de layout sem aviso. Se um seletor documentado não existir
mais, não force: descubra o novo (leia o DOM), conclua a tarefa e **avise o José que a
skill precisa de atualização**, dizendo qual passo mudou. Uma skill que mente sobre o
caminho é pior que uma skill incompleta.
