# PJe — baixar a íntegra ou consultar um processo

Caminho verificado ao vivo, ponta a ponta, em dois ambientes de **1º grau** (ago/2026):
TRF-5 (PJe 2.11) e TRF-1 (PJe 2.9.1.1). Os `id` de campo, os `title` de botão e o
formato das URLs são **idênticos** nas duas versões — o que muda é o login e o painel
de download. O **2º grau não foi percorrido**: o endereço do TRF-5 foi conferido pelo
rodapé de um PDF baixado de lá; o do TRF-1 não tem prova. Ali, trate o caminho como
hipótese: confira cada `id` no DOM antes de usá-lo e avise o José do que divergir
(*Manutenção*, na SKILL).

## Endereços

| Tribunal | Grau | URL base | Verificação |
|---|---|---|---|
| TRF-5 | 1º | `https://pje1g.trf5.jus.br` | caminho completo, ao vivo (PJe 2.11) |
| TRF-5 | 2º | `https://pjett.trf5.jus.br` | só o endereço, pelo rodapé de PDF baixado |
| TRF-1 | 1º | `https://pje1g.trf1.jus.br` | caminho completo, ao vivo (PJe 2.9.1.1) |
| TRF-1 | 2º | `https://pje2g.trf1.jus.br` | nenhuma |

**O número CNJ diz a origem, não onde o processo está agora.** No formato
`NNNNNNN-DD.AAAA.J.TR.OOOO`, o campo `OOOO` é o órgão de origem: quatro dígitos
começando em `8` (TRF-5: `8100`, `8300`…) ou `3` (TRF-1: `3300`, `3400`…) indicam
processo nascido numa vara de 1º grau; `0000`, processo originário do tribunal. Em
grau de recurso o processo conserva o número da origem — um `…8100` pode estar hoje no
2º grau. Sempre que o José falar em apelação, agravo, recurso ou "no tribunal", ou se o
1º grau mostrar remessa ao tribunal, pergunte ou confira o 2º grau: buscar no grau
errado devolve "nenhum resultado" ou autos sem a fase recursal, e parece que o processo
não existe.

## Passo 1 — abrir a busca

Vá direto para a página de consulta; o menu sanduíche → *Processo* → *Pesquisar* →
*Processo* leva ao mesmo lugar em quatro cliques a mais:

```
<base>/pje/Processo/ConsultaProcesso/listView.seam
```

Tire um screenshot. Se aparecer tela de login, **pare e peça ao José que faça o login**.
O TRF-1 redireciona para o SSO do CNJ (`sso.cloud.pje.jus.br`) e sua sessão cai com
mais frequência que a do TRF-5; é comum precisar disso. As credenciais podem até vir
preenchidas pelo gerenciador de senhas dele — **não clique em ENTRAR mesmo assim**.
Autenticação é dele. Espere ele avisar e siga.

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
seis pedaços. É o que o José faz na mão.

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

Se o José der CPF/CNPJ ou nome de parte em vez do número, use o campo
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

A prevenção é trivial — sobrescrever `confirm` **antes** de clicar. O José já
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

O override aceita **qualquer** `confirm` da aba, não só o do aviso ou o do download.
Com ele ativo, não clique fora do caminho descrito aqui — em especial em expediente ou
intimação: um aviso de ciência seria aceito sem que o José o visse, e a consulta ao
teor pode dar a intimação por realizada e abrir o prazo.

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

**Padrão, aplicado sem perguntar:**
- **Cronologia crescente** — no TRF-5, troque o default. O PDF sai na ordem dos autos
  físicos, melhor para a leitura e para a análise.
- **Todos os documentos** — nenhum filtro de tipo, ID ou período.
- **"Índice do PDF" marcado** — no TRF-1, as quatro caixas, que já vêm marcadas.
  **Nunca desmarque:** são esses campos que geram os bookmarks do PDF, o índice de que
  a `analise-processo-pje` depende para ler processo de centenas de páginas sem
  carregar tudo no contexto.
- O resto no default (no TRF-5, expediente/movimentos = Não).

**Pergunte só acima de ~150 MB.** Se os autos prometerem passar disso — centenas de
documentos, muitos anexos digitalizados —, o recorte por tipo, ID ou período é decisão
do José: proponha-o a partir da lista de documentos dos autos e espere o ok. Fora
disso, não pergunte.

Confirme com:

```js
document.getElementById('navbar:downloadProcesso').click();
```

## Passo 5 — esperar e conferir o arquivo

O PJe monta o PDF na hora e só então o entrega ao navegador. O spinner que aparece não
dura na proporção do número de documentos: de 80 a 170 documentos, 10 a 20 s; 302
documentos, cerca de 21 min. Enquanto ele estiver na tela, espere — sem repetir o
clique — e não conclua nada antes de ele sumir. O fim do spinner também não é o fim do
download: o navegador ainda pode estar gravando o arquivo.

Na **aba Code e no CLI** você enxerga o disco e confere o arquivo; no **Cowork**, não
(vá ao passo 6).

**Antes do clique, retrate a pasta.** Liste a pasta de download do Chrome (em geral,
Downloads) e anote a hora **antes** de confirmar. O arquivo deste download é o que
surgir depois — não "o PDF mais recente" nem "o que tem o número no nome".

Três armadilhas já travaram a automação aqui:

1. **`.crdownload` órfão.** O Chrome grava o download em andamento como `.crdownload`
   e o renomeia no fim. Um `.crdownload` que já estava na pasta é resto de download
   interrompido e não some nunca: esperar "a pasta ficar sem `.crdownload`" trava para
   sempre. Acompanhe só o arquivo deste download.
2. **Tamanho em cache.** O tamanho que a listagem da pasta mostra pode vir do cache e
   parecer estável enquanto o Chrome ainda grava. Tamanho parado não prova que acabou.
3. **Curinga ao mover.** Mover ou renomear com `*.pdf` já levou junto cinco PDFs
   alheios da pasta de Downloads. Mova só se o José pediu, por nome exato, um arquivo
   por vez.

**A prova de que acabou:** o `.pdf` com o nome final existe, o `.crdownload` dele
sumiu e o arquivo abre — `processo.py index <pdf>` (script da `analise-processo-pje`)
lê o PDF e informa documentos e páginas. Zero documentos: veio sem índice. Com a
cronologia crescente, o último documento do índice tem de ser o mais recente da página
dos autos; se não for, o arquivo é outro ou veio incompleto.

## Passo 6 — fechar

Feche as abas que você abriu e informe o que os autos são (classe, órgão julgador,
partes, nº de documentos). Na aba Code e no CLI, acrescente o caminho, o tamanho e o
resultado do `index`. No Cowork o arquivo foi para a pasta de Downloads da máquina do
José, fora do que você enxerga: pergunte se o PDF chegou, em vez de afirmar.

## Consulta pelo navegador (sem download)

Para quando os conectores de andamento não bastarem. Faça os passos 1 a 3 e leia a
página dos autos pelo DOM; pare antes do passo 4. Na aba dos autos, não reaplique o
override do `confirm`: sem download, ele não é necessário, e o aviso que aparecer é para
o José ler (se a aba congelar, `navigate` de volta e avise). A leitura dos movimentos
nesta página ainda não foi mapeada: informe o que ela mostrar, diga o que não encontrou
e não clique em expediente nem em intimação.

## Sintomas e causas

| Sintoma | Causa provável |
|---|---|
| `screenshot`/`javascript_tool` dando timeout | `confirm` nativo aberto. Se foi no clique do download, você esqueceu de reaplicar o override na aba dos autos. Peça o OK ao José ou `navigate` a aba de volta |
| "nenhum resultado encontrado" | grau errado (1º vs 2º), tribunal errado, ou alguma das seis caixas do número em branco |
| autos sem a fase recursal | o processo subiu: a tramitação atual está no 2º grau, com o mesmo número |
| tela de login no meio do caminho | sessão expirou (comum no TRF-1, que passa pelo SSO) — peça ao José que faça o login; nunca digite credencial |
| "Página não encontrada" nos autos | URL montada à mão sem o `ca` de sessão — volte e clique no link do resultado |
| baixou um PDF pequeno, de um documento só | foi clicado o ícone de download do visualizador, não o da barra do topo |
| o PDF veio sem índice/bookmarks | os checkboxes de "Índice do PDF" foram desmarcados |
| o screenshot não mostra o resultado da busca | render atrasado — leia o DOM em vez do screenshot |
| o spinner do download passa de minutos | normal em autos grandes (302 documentos ≈ 21 min) — espere, sem repetir o clique |
| a espera pelo arquivo nunca termina | `.crdownload` órfão de download antigo, e a espera olhava a pasta inteira — acompanhe só o arquivo deste download |
| o arquivo "terminou", mas não abre ou vem cortado | tamanho parado na listagem (cache) tomado como fim — a prova é o `index` abrir o PDF |
| PDFs alheios movidos junto | curinga no comando de mover — mova por nome exato |
