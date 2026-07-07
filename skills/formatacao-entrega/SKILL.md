---
name: formatacao-entrega
description: (camada E — compartilhada) Converte a peça/relatório externo em documento de ENTREGA no padrão da casa — gera um .docx (Cambria, margens em cm, recuos, entrelinha 1,15, separação por parágrafo em branco) a partir da peça marcada com diretivas @tag. Usada pelas skills de output EXTERNAS (peças protocoladas e relatório para cliente). Relatórios internos dispensam.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Formatação de Entrega (camada E)

Produz o **.docx final** com fidelidade ao padrão da casa. Não altera conteúdo —
recebe o texto pronto e verificado e aplica a forma.

## Mecanismo (determinístico)
Script: `${CLAUDE_PLUGIN_ROOT}/skills/formatacao-entrega/scripts/build_docx.py`
(usa `python-docx`; se faltar: `pip install python-docx`).

```
python build_docx.py <peca_marcada.md> --out <workspace>/<numero-cnj>/peca.docx
```

Salve o `.docx` no workspace do processo
(`${CLAUDE_PLUGIN_DATA}/processos/<numero-cnj>/`).

## Fonte da verdade
`assets/padrao-formatacao.md` descreve o padrão completo (medidas, fontes, recuos).
O script é a implementação desse padrão. **Se o padrão mudar, edite os DOIS** (o
asset e o script) para não divergirem.

## Contrato com a `escrita-juridica` (convenção @tag)
Para o output ser convertível, a `escrita-juridica` deve emitir a peça em blocos
marcados por uma diretiva `@tag` no início da linha (exemplo completo em
`assets/exemplo-peca.md`):

| Tag | Papel | Formato aplicado |
|---|---|---|
| `@enderecamento` | Endereçamento | Cambria 14, negrito, justificado |
| `@identificacao` | Processo/classe/partes | Cambria 12 negrito (linhas coladas) |
| `@titulo` | Título da peça | Cambria 14 negrito, **centralizado** |
| `@corpo` | Parágrafos de texto | Cambria 12, justificado, recuo 1ª linha 2 cm |
| `@secao` | Título de seção | Cambria 12 negrito, justificado |
| `@citacao` | Transcrição | Cambria 11 **negrito**, recuo esq. 2 cm, entre “aspas curvas” |
| `@pedidos` | Itens a) b) c) | Cambria 11 **negrito**, justificado, recuo esq. 2 cm |
| `@fecho` | "Nestes termos…" | Cambria 12, justificado, **sem** recuo de 1ª linha |
| `@data` | Local e data | Cambria 12, justificado, sem recuo |
| `@assinatura` | 1ª linha nome (negrito), demais OAB | Cambria 12, **centralizado** |

Regras do parser:
- Cada `@tag` vale até o próximo `@tag`.
- Em `@corpo` e `@pedidos`, parágrafos/itens são separados por **linha em branco**.
- O conversor insere **um parágrafo vazio** entre blocos (a "respiração" do padrão);
  espaçamento automático antes/depois fica sempre em zero.

## Papel timbrado
A **imagem** do timbre é deliberadamente omitida (o padrão só define texto). As
margens (superior 4 cm, cabeçalho/rodapé a 1,25 cm) já reservam o espaço do timbre.
> TODO: opção `--timbrado <img>` para inserir a imagem no cabeçalho, quando o José
> fornecer o arquivo do timbre.

## Verificação
Depois de gerar, **abrir no Word** para conferência visual final. É esperado ver um
parágrafo em branco entre os blocos — é o padrão, não erro.

## TODO
- [ ] Suporte a papel timbrado (imagem no cabeçalho).
- [ ] Integrar os modelos de endereçamento da `peca-processual-base`.
