---
name: formatacao-entrega
description: Gera o .docx de entrega no padrão da casa a partir de blocos @tag, colando ementas e trechos dos autos verbatim por @citacao-ref, com timbrado por modelo .docx. Não use para relatório interno (markdown basta) nem para redigir ou revisar o texto.
---

# Formatação de entrega

Converte a peça ou o relatório externo, já redigido e verificado, no `.docx` final; não
altera conteúdo. É a dona do contrato `@tag`: a `escrita-juridica` emite os blocos e as
skills de saída apontam para cá. O nível não muda a formatação, só a verificação que vem
antes (`verificacao-citacoes`).

## Gerar
Script: `${CLAUDE_PLUGIN_ROOT}/skills/formatacao-entrega/scripts/build_docx.py`
(requer `python-docx`: `pip install python-docx`).

```
python build_docx.py <peca.md> --out <workspace>/peca.docx
       [--modelo <nome> | --template <timbrado.docx>] [--workspace <workspace>]
       [--transcript <arquivo|pasta>]
python build_docx.py --preparar-modelo <documento do escritório.docx> <raiz>/modelos/<nome>.docx
```
- `<workspace>` é o caminho que `processo.py workspace <cnj>` imprime; não o monte à mão.
- **`fonte: autos` precisa do workspace.** Sem `--workspace`, o script procura os
  `doc_NNN_*.md` na pasta do `.md` e até dois níveis acima (serve para
  `<workspace>/redacao/`); rascunho fora dele exige `--workspace`.
- **Timbrado:** `--modelo <nome>` usa um modelo da pasta privada `<raiz>/modelos/` (raiz =
  `PRATICA_JURIDICA_DATA`; sem ela, a pasta `dados-juridicos/modelos/` acima do `.md`).
  Qual modelo vale para cada escritório e tipo de documento está no `LEIA-ME.md` dessa
  pasta; na dúvida sobre o escritório do caso, pergunte. Página, margens, cabeçalho e
  rodapé vêm do modelo; a tipografia é a do padrão. Os modelos ficam fora do repositório.
  `--template <caminho>` serve para um modelo avulso.
- **Novo timbrado:** `--preparar-modelo` cria o modelo a partir de um documento real do
  escritório e guarda só página, margens, cabeçalho e rodapé; corpo, comentários, notas,
  imagens do corpo, metadados e propriedades do arquivo saem. A mesma limpeza roda em todo
  modelo na hora do uso: nada do documento de origem vai para a peça.
- Erro em qualquer `@citacao-ref` (fonte não achada, âncora ambígua, ementa com defeito,
  grifo ausente) para a geração e nada é gravado: o `.docx` anterior fica intacto. No
  fim, o script lista de onde veio cada citação (detalhes, busca, cache ou autos).
- Abra no Word para a conferência visual: parágrafo em branco entre blocos é o padrão.

## Contrato @tag
Cada bloco começa numa linha só com a diretiva e vai até a próxima. Exemplo completo:
`assets/exemplo-peca.md`. Medidas: `assets/padrao-formatacao.md`, fonte da verdade (mudou
o padrão, mude o asset e o script).

| Tag | Uso | Forma (Cambria) |
|---|---|---|
| `@enderecamento` | endereçamento | 14 pt negrito, justificado |
| `@identificacao` | processo, classe, partes | 12 pt negrito, linhas coladas |
| `@titulo` | nome da peça | 14 pt negrito, centralizado |
| `@secao` | título de seção | 12 pt negrito, justificado |
| `@corpo` | parágrafos | 12 pt, justificado, recuo de 1ª linha 2 cm |
| `@citacao` | transcrição escrita à mão | 11 pt negrito, recuo esquerdo 2 cm, aspas curvas |
| `@citacao-ref` | transcrição por referência (abaixo) | a mesma do `@citacao` |
| `@pedidos` | itens a), b), c) | 11 pt negrito, recuo esquerdo 2 cm |
| `@fecho` | "Nestes termos, pede deferimento." | 12 pt, justificado, sem recuo |
| `@data` | local e data | 12 pt, justificado, sem recuo |
| `@assinatura` | nome (1ª linha, negrito) e OAB | 12 pt, centralizado |

- Em `@corpo`, `@citacao` e `@pedidos`, parágrafos e itens se separam por linha em branco.
- Entre blocos entra um parágrafo vazio; espaçamento antes/depois é sempre zero.
- Linha com `@` que não seja uma tag da tabela é texto do bloco em curso.

## @citacao-ref — citar sem redigitar
Cola o texto **verbatim** da fonte: só o espaço em branco é normalizado. Uma chave por
linha:

| Chave | Valor |
|---|---|
| `fonte` | rótulo da base (`STJ`, `STF`, `TRF1`, `TRF5`, `TJPE`, `CARF`, `RFB`, `TCU`) ou `autos` |
| `processo` | classe e número como o conector devolveu; casa o número inteiro e a classe |
| `id` | ID do resultado do conector, quando o número casar com mais de um julgado |
| `itens` | recorte por item da ementa: `1`, `1-2`, `2,4`, `II-IV` (vale para itens na mesma linha) |
| `trecho` | `de "âncora inicial" ate "âncora final"`; âncora repetida só vale se as passagens forem idênticas |
| `grifo` | trecho realçado com marca-texto; repetível; tem de estar no texto citado |
| `ref` | atribuição depois das aspas |
| `doc` · `arquivo` | com `fonte: autos`: seq do documento extraído (`doc: 28` → `doc_028_*.md`) ou arquivo do workspace |

```
@citacao-ref
fonte: STJ
processo: REsp 1.234.567
itens: 1-2
grifo: configura negativa de prestação jurisdicional
ref: STJ, REsp 1.234.567, Segunda Turma, Rel. Min. Fulano de Tal

@citacao-ref
fonte: autos
doc: 28
trecho: de "PROCESSUAL CIVIL" ate "Apelação desprovida"
ref: TRF-1, 7ª Turma, acórdão recorrido
```

Jurisprudência — de onde vem o texto:
- Só da saída do conector gravada **nesta sessão** (transcript da sessão, dos subagentes e
  saídas grandes salvas à parte); nunca de texto do modelo ou de Bash. Outra sessão ou
  projeto, só com `--transcript <arquivo .jsonl ou pasta>`.
- Busca e detalhes do mesmo julgado: vale o detalhes (ementa íntegra). Ementa longa, ou
  do TRF-5: rode o `*_detalhes_*` antes de citar.
- O texto achado fica em `<workspace>/citacoes/`; nova geração em outra sessão o usa sem
  refazer a busca.
- Do resultado do TRF-5 o script tira o cabeçalho do PJe com as partes: o texto começa
  em "EMENTA".
- Ementa com "[…ementa truncada…]" ou com "?" no lugar de aspa ou travessão (defeito do
  conector) é recusada: reabra pelo `*_detalhes_*`; persistindo, transcreva do inteiro
  teor oficial em `@citacao` e passe pela `verificacao-citacoes`.

**Conferir o texto que vai entrar** — é o que a `verificacao-citacoes` inspeciona
(`citar.py` fica na pasta do `build_docx.py`):
```
python citar.py --processo "REsp 1.234.567" [--id <ID>] [--itens 1] [--trecho '...']
       [--grifo '...'] [--workspace <workspace>] [--transcript <arquivo|pasta>] [--json]
python citar.py --fonte autos --workspace <workspace> (--doc 28 | --arquivo <x.md>) [--trecho '...']
```
Imprime só o texto resolvido; a procedência (detalhes, busca, cache ou autos, e o
arquivo) vai para o stderr, ou para o JSON com `--json`. Exit 2 = não resolveu.

## TODO
- Fórmulas de endereçamento da casa (por instância/tribunal) — o José fornece; entram em
  `assets/enderecamento.md`.
