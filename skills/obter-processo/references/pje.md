# PJe — baixar a íntegra de um processo

Caminho verificado ao vivo em **dois** ambientes (ago/2026): TRF-5 1º grau (PJe 2.11)
e TRF-1 1º grau (PJe 2.9.1.1). Os `id` de campo, os `title` de botão e o formato das
URLs são **idênticos** nas duas versões — o que muda é o login e os filtros do painel
de download. Isso é forte indício de que os quatro endereços da tabela funcionam
igual, mas confirme lendo o DOM antes de concluir que algo quebrou.

## Endereços

| Tribunal | Grau | URL base |
|---|---|---|
| TRF-5 | 1º | `https://pje1g.trf5.jus.br` |
| TRF-5 | 2º | `https://pjett.trf5.jus.br` |
| TRF-1 | 1º | `https://pje1g.trf1.jus.br` |
| TRF-1 | 2º | `https://pje2g.trf1.jus.br` |

**O grau vem do número CNJ, não de chute.** No formato
`NNNNNNN-DD.AAAA.J.TR.OOOO`, o campo `OOOO` é o órgão de origem: quatro dígitos
começando em `8` (TRF-5: `8100`, `8300`…) ou `3` (TRF-1: `3300`, `3400`…) são vara de
1º grau; `0000` é o próprio tribunal, ou seja, 2º grau. Na dúvida — e sempre que o
usuário falar em apelação, agravo, recurso ou "no tribunal" — pergunte, porque buscar
no grau errado devolve "nenhum resultado" e parece que o processo não existe.

## Passo 1 — abrir a busca

Vá direto para a página de consulta; o menu sanduíche → *Processo* → *Pesquisar* →
*Processo* leva ao mesmo lugar em quatro cliques a mais:

```
<base>/pje/Processo/ConsultaProcesso/listView.seam
```

Tire um screenshot. Se aparecer tela de login, **pare e peça para o usuário logar**.
O TRF-1 redireciona para o SSO do CNJ (`sso.cloud.pje.jus.br`) e sua sessão cai com
mais frequência que a do TRF-5; é comum precisar disso. As credenciais podem até vir
preenchidas pelo gerenciador de senhas do usuário — **não clique em ENTRAR mesmo
assim**. Autenticação é dele. Espere ele avisar e siga.

Se aparecer o formulário de filtros com o nome dele no topo, a sessão está viva.

## Passo 2 — preencher o número

O campo é dividido em seis caixas com `id` estáveis (iguais nas duas versões):

| Caixa | `id` | exemplo fictício `1234567-89.2024.4.05.8100` |
|---|---|---|
| sequencial | `fPP:numeroProcesso:numeroSequencial` | `1234567` |
| dígito | `fPP:numeroProcesso:numeroDigitoVerificador` | `89` |
| ano | `fPP:numeroProcesso:Ano` | `2024` |
| ramo | `fPP:numeroProcesso:ramoJustica` | `4` (já vem preenchido) |
| tribunal | `fPP:numeroProcesso:respectivoTribunal` | `05` (já vem preenchido) |
| órgão | `fPP:numeroProcesso:NumeroOrgaoJustica` | `8100` |

Digitar **não** avança de caixa sozinho — quem digita o número inteiro na primeira
caixa perde os outros cinco pedaços. Duas formas que funcionam:

*Colar* o número completo formatado na primeira caixa: o próprio PJe distribui os
seis pedaços. É o que o usuário faz na mão.

*Preencher por `id`*, que é o mais confiável para automação:

```js
const n = '1234567-89.2024.4.05.8100';   // exemplo; troque pelo número real
const d = n.replace(/\D/g, '');
const partes = [d.slice(0,7), d.slice(7,9), d.slice(9,13), d.slice(13,14), d.slice(14,16), d.slice(16,20)];
const ids = ['numeroSequencial','numeroDigitoVerificador','Ano','ramoJustica','respectivoTribunal','NumeroOrgaoJustica'];
ids.forEach((id, i) => {
  const el = document.getElementById('fPP:numeroProcesso:' + id);
  el.value = partes[i];
  el.dispatchEvent(new Event('input',  {bubbles:true}));
  el.dispatchEvent(new Event('change', {bubbles:true}));
});
```

Se o usuário der CPF/CNPJ ou nome de parte em vez do número, use o campo
correspondente do mesmo formulário — a busca aceita qualquer um deles e devolve
lista. Se ele não souber o número, ele pode pedir que você o procure antes no DJEN
ou no Legal One.

Dispare a busca com `document.getElementById('fPP:searchProcessos').click()` e espere
~2-3s. Depois **leia o DOM** para conferir o resultado; o screenshot pode estar
desatualizado nesse ponto.

## Passo 3 — abrir os autos (o aviso do CNJ)

Este é o passo que trava tudo se for feito na ordem errada.

Clicar no número do processo dispara um `window.confirm()` com o aviso do CNJ. Esse
diálogo é **nativo do navegador**: enquanto estiver aberto ele congela o renderizador,
e a extensão perde a aba — `screenshot`, `read_page` e `javascript_tool` passam a dar
timeout. Pior: a janela do aviso abre **fora** do grupo de abas do MCP, então você não
consegue nem enxergá-la para clicar em OK. A única saída depois de travado é
`navigate` a aba de volta para a página de consulta, o que descarta o diálogo.

A prevenção é trivial — sobrescrever `confirm` **antes** de clicar. O usuário já
autorizou aceitar esse aviso, que é meramente informativo:

```js
window.confirm = () => true;
window.alert   = () => {};
const link = [...document.querySelectorAll('a')]
  .find(a => /1234567-89\.2024/.test(a.innerText));   // trecho do número buscado
link.click();
```

Os autos abrem numa **aba nova dentro do grupo do MCP**, em uma URL assim:

```
<base>/pje/Processo/ConsultaProcesso/Detalhe/listProcessoCompletoAdvogado.seam?id=<idProcesso>&ca=<hash>&aba=
```

Chame `tabs_context_mcp` para pegar o `tabId` novo. Não tente montar essa URL na mão
em vez de clicar: o `ca` é um hash de sessão e, sem ele, o PJe responde "Página não
encontrada".

> ### ⚠️ Reaplique o override na aba nova
> O `window.confirm` que você sobrescreveu vale **só naquele documento**. A aba dos
> autos é outro documento: nasce com o `confirm` original. E o TRF-1 dispara um
> **segundo** `confirm()` na hora do download (o TRF-5 não dispara) — sem o override,
> a aba dos autos congela no passo seguinte, depois de todo o caminho já andado.
>
> Primeira coisa a rodar na aba nova, antes de qualquer clique:
> ```js
> window.confirm = () => true; window.alert = () => {};
> ```

## Passo 4 — baixar a íntegra

Na barra azul do topo, o ícone de download fica entre *Juntar documentos* e
*Etiquetas do processo*:

```js
document.querySelector('a[title="Download autos do processo"]').click();
```

> **A armadilha.** Existe um segundo ícone de download, idêntico, na barra do
> visualizador de documentos (mais abaixo, à direita do número da página). Aquele baixa
> **só o documento aberto no momento**, não os autos. Selecionar pelo `title` acima
> elimina o risco; clicar por coordenada, não.

Abre um painel de filtros que **muda conforme a versão do PJe** — leia o que está na
tela em vez de assumir:

| | TRF-5 (2.11) | TRF-1 (2.9.1.1) |
|---|---|---|
| Tipo de documento | ✔ | ✔ |
| ID a partir de / Até | ✔ | ✔ |
| Período de / Até | ✔ | ✔ |
| Cronologia (default) | Decrescente | Crescente |
| Incluir expediente / movimentos | ✔ (default Não) | — |
| Índice do PDF (4 checkboxes) | — | ✔ (todas marcadas) |

**Pergunte ao usuário antes de confirmar** — é decisão dele, e ele pediu que fosse
sempre perguntada. O que vale explicar em uma linha: a cronologia crescente deixa o
PDF na ordem dos autos físicos, melhor para leitura e para a análise posterior; e os
filtros de tipo/ID/período existem para processos grandes demais para baixar inteiros.

**Não desmarque o "Índice do PDF"** onde ele existir. São esses campos que geram os
bookmarks do PDF — exatamente o índice de que a skill `analise-processo-pje` depende
para ler processo de centenas de páginas sem carregar tudo no contexto. Desmarcar ali
custa caro duas etapas adiante.

Confirme com:

```js
document.getElementById('navbar:downloadProcesso').click();
```

O PJe monta o PDF na hora. Aparece um spinner que, em processo de 80 a 170 documentos,
leva de dez a vinte segundos — em processos grandes, bem mais. Espere o spinner sumir
antes de concluir qualquer coisa.

## Passo 5 — fechar

O arquivo vai para a pasta de Downloads **da máquina do usuário**; você não tem como
verificar isso daqui. Feche as abas que você abriu, informe o que os autos são
(classe, órgão julgador, partes, nº de documentos) e pergunte se o PDF chegou.

## Sintomas e causas

| Sintoma | Causa provável |
|---|---|
| `screenshot`/`javascript_tool` dando timeout | `confirm` nativo aberto. Se foi no clique do download, você esqueceu de reaplicar o override na aba dos autos. Peça o OK ao usuário ou `navigate` a aba de volta |
| "nenhum resultado encontrado" | grau errado (1º vs 2º), tribunal errado, ou alguma das seis caixas do número em branco |
| tela de login no meio do caminho | sessão expirou (comum no TRF-1, que passa pelo SSO) — peça ao usuário que logue; nunca digite credencial |
| "Página não encontrada" nos autos | URL montada à mão sem o `ca` de sessão — volte e clique no link do resultado |
| baixou um PDF pequeno, de um documento só | foi clicado o ícone de download do visualizador, não o da barra do topo |
| o PDF veio sem índice/bookmarks | os checkboxes de "Índice do PDF" foram desmarcados |
| o screenshot não mostra o resultado da busca | render atrasado — leia o DOM em vez do screenshot |
