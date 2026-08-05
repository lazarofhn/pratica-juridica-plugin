---
name: obter-processo
description: (camada B) Baixa a íntegra de um processo automatizando a navegação no sistema processual pela extensão do Claude no Chrome. Use sempre que o usuário pedir para "baixar o processo", "pegar os autos", "buscar o processo no PJe", ou der um número CNJ e pedir a cópia integral — inclusive quando ele não disser o nome do sistema. Hoje o PJe está mapeado ponta a ponta (TRF5 e TRF1, 1º e 2º graus); outros sistemas ainda não.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (análise →
> plano de respostas → pesquisa → escrita → verificação → entrega) está na skill
> **`analise-processual`**. Se o usuário acionou **esta** skill diretamente e o objetivo
> final dele é uma peça ou um relatório, pergunte se ele quer **(a)** seguir o pipeline
> completo ou **(b)** só o download avulso. Se ele pediu apenas o download, não pergunte
> nada disso — baixe e entregue.

# Obter Processo (aquisição automatizada)

Baixar os autos é trabalho mecânico de dez a quinze cliques em um sistema lento. Ele
não fica melhor por ser feito por um humano — só fica mais caro. Por isso este caminho
vale a pena sempre que o sistema estiver mapeado.

## O que só o usuário pode fazer

**Login e certificado digital são dele.** Nunca digite credencial, nunca preencha
senha, nunca opere token ou certificado. Se a navegação cair numa tela de login,
pare e avise: *"o PJe pediu login — faz o acesso aí que eu sigo daqui"*. Se entrar
direto nos autos, é porque a sessão dele ainda está viva.

O arquivo cai na pasta de Downloads da **máquina do usuário**, não neste ambiente.
Você não enxerga o disco dele: ao terminar, confirme com ele que o PDF chegou em vez
de afirmar que chegou.

## Sistemas mapeados

| Sistema | Referência |
|---|---|
| **PJe** (TRF5 e TRF1, 1º e 2º graus) | `references/pje.md` — leia **antes** de abrir o navegador. Verificado ao vivo em duas versões do PJe (2.11 e 2.9.1.1) |
| eproc, Projudi, e-SAJ, PJe de outros tribunais | não mapeados — ver abaixo |

## Se o sistema não estiver mapeado

Diga isso ao usuário de forma direta e ofereça as duas saídas: ele baixa manualmente
e te aponta o PDF (quase sempre mais rápido), ou vocês mapeiam o caminho juntos agora
— você navega, ele corrige, e no fim vocês acrescentam um `references/<sistema>.md`
seguindo o formato do `pje.md`. Não improvise um caminho às cegas em sistema
desconhecido: cada um tem armadilha própria, e tentar adivinhar queima tempo do
usuário sem produzir nada.

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

**Processos gigantes.** Acima de umas poucas centenas de megabytes, baixar tudo é
desperdício e às vezes estoura. O painel de download do PJe filtra por tipo de
documento, faixa de ID e período: nesse caso, leia o índice dos autos primeiro,
combine com o usuário o recorte e baixe só o que interessa.

## Ao terminar

Entregue ao usuário: o número do processo, a classe, o órgão julgador, as partes e
quantos documentos os autos têm — é o que ele precisa para conferir se veio o processo
certo. Depois pergunte se o PDF chegou na pasta dele. Se o objetivo final era uma peça
ou análise, o PDF baixado é o insumo da camada C (`analise-processo-pje`).

## Manutenção

Sistema processual muda de layout sem aviso. Se um seletor documentado não existir
mais, não force: descubra o novo (leia o DOM), conclua a tarefa e **avise o usuário
que a skill precisa de atualização**, dizendo qual passo mudou. Uma skill que mente
sobre o caminho é pior que uma skill incompleta.
