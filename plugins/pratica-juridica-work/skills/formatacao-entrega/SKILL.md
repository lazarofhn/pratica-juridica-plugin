---
name: formatacao-entrega
description: Gera DOCX de peças e relatórios externos no padrão da casa a partir de texto marcado, com transcrições por fonte explícita e hash.
---

## Execução no ambiente OpenAI
Leia [o contrato de ambiente](../analise-processual/references/ambiente-openai.md)
uma vez por tarefa. Execute o escopo solicitado; a invocação direta desta skill
não exige escolher entre uso avulso e fluxo completo. Use apenas as dependências
necessárias. Pergunte somente por informação ausente que mude materialmente a
entrega, após aproveitar o contexto e os arquivos disponíveis.


# Formatação de Entrega (camada E)

Produz o **.docx final** com fidelidade ao padrão da casa. Não altera conteúdo —
recebe o texto pronto e verificado e aplica a forma.

## Mecanismo (determinístico)
Script: [build_docx.py](scripts/build_docx.py), relativo a esta skill instalada
(usa `python-docx`; se faltar: `pip install python-docx`).

```
python build_docx.py <workspace>/peca_marcada.md --out <workspace>/peca.docx
```

Salve o `.docx` no workspace do processo
(`<workspace-do-processo>/`).

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
Depois de gerar, renderize ou abra com a ferramenta disponível para conferência visual. Se indisponível, declare que a inspeção visual está pendente. É esperado ver um
parágrafo em branco entre os blocos — é o padrão, não erro.

## TODO
- [ ] Suporte a papel timbrado (imagem no cabeçalho).
- [ ] Integrar os modelos de endereçamento da `peca-processual-base`.

## Fontes portáteis
Para `@citacao-ref`, leia [references/fontes.md](references/fontes.md).
Não há descoberta de transcripts nesta variante.
