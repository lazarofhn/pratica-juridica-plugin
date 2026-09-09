# Adaptação para Astra e ChatGPT Work

## Resultado e escopo

A variante `plugins/pratica-juridica-work` mantém as 15 skills e os ativos de
formatação da versão Claude 1.2.0, com instruções e runtime próprios. A origem
analisada é `2b16ab2cd00b8e5774e9e3a2aba1c47eb229f711`, igual ao HEAD publicado
no GitHub na conferência de 9 de setembro de 2026. A análise abrangeu todas as
skills, scripts Python, manifesto, catálogo Claude, referência PJe e guia de construção.

Não foi executado caso jurídico real nem instalação em ChatGPT Work. O resultado
é uma variante implementada com validação técnica local, a homologar no ambiente
de destino. As regras jurídicas foram preservadas como orientações de trabalho;
esta revisão não certifica cabimento ou direito aplicável a um caso concreto.

## Constatações e mudanças

| Superfície original | Problema observado | Tratamento na variante |
|---|---|---|
| Aviso repetido em todas as skills | Pergunta obrigatória sobre fluxo completo ou uso avulso, mesmo com pedido claro | Respeitar o pedido e carregar apenas as dependências necessárias |
| `plano-de-respostas` | Aprovação por geração e subgeração; tamanho/número de chamadas tratado como profundidade | Segmentação por questão e evidência; checkpoints em arquivo; revisão humana por etapas quando solicitada |
| `escrita-juridica` | “Uso máximo” de conectivos, recapitulação enumerada e proibição de corte de conteúdo conviviam com concisão | Encadeamento pelo sentido, corte de redundância, preservação de desenvolvimento e preferência por prosa |
| `analise-processo-pje` | Opus/Sonnet e Agent tool impostos | Modelo escolhido na sessão; delegação condicionada à autorização e disponibilidade |
| `processo.py` | Busca em ancestrais/mounts, variáveis Claude, fallback silencioso e promessa de persistência | Raiz explícita ou cwd, CNJ normalizado, erro visível e persistência a verificar |
| `citar.py` | Varredura de conversas privadas; correspondência parcial de número; seleção do texto mais longo | Fonte explícita, hash, recorte com âncoras únicas; nenhuma leitura de transcripts |
| Pesquisa e verificação | Pesquisa restringia voto a pedido explícito, mas auditoria exigia inteiro teor; repetição de buscas como prova de fonte | Inteiro teor para precedentes decisivos; fonte salva pode ser reaberta; ementa recebe alcance limitado |
| Pesquisa jurídica | Descarte de desfavoráveis e inferência de superação a partir de divergência | Registrar contrários, avaliar aderência e conferir superação |
| `obter-processo` | Extensão Claude, JS específico e override genérico de confirmação | Navegador documentado na sessão, interface observada e tratamento explícito de diálogos |
| Referência PJe | Grau atual deduzido do órgão de origem; evidência real só para parte dos ambientes anunciados | Confirmar tramitação atual; marcar endereços/seletores como referências históricas |
| Entrega e README | Word local, Downloads e execução no computador tratados como universais | Detectar capacidades; declarar inspeção visual ou acesso pendente; distinguir execução na nuvem |

A mudança de `@citacao-ref` é incompatível com rascunhos antigos: agora são
obrigatórios `arquivo`, `sha256` e `ref`. O script não interpreta automaticamente
respostas de todo MCP; recebe texto UTF-8 exportado ou extraído de modo verificável.
Isso elimina a dependência de transcripts, mas exige um caminho real de captura.
Sem exportação fiel, a skill orienta paráfrase conferida ou pendência explícita.

## Fundamento da adaptação de linguagem

A orientação oficial de Astra destaca sensibilidade a instruções de skills,
pausas excessivas por aprovação e necessidade de esclarecer estilo e autonomia.
Por isso, a mudança foca em condições de decisão e conclusão verificável, sem
trocar apenas “Claude” por “Astra”. A melhora comportamental é uma hipótese a
avaliar com casos representativos, não um resultado comprovado por testes estruturais.
[Orientação de Astra](https://developers.openai.com/api/docs/guides/latest-model).

As descrições ficaram mais curtas e discriminantes porque a descoberta inicial de
skills usa seus metadados; o corpo e as referências são carregados quando necessários.
[Documentação de skills](https://learn.chatgpt.com/docs/build-skills).

O pacote usa o manifesto de compatibilidade `.codex-plugin/plugin.json`, que segue
suportado. A documentação também oferece manifesto portátil `plugin.json`; migrar
para ele é uma evolução possível, não requisito para esta cópia. Marketplaces
locais e de repositório têm disponibilidade variável por superfície. Nenhuma
configuração local foi tratada como instalação comprovada em nuvem.
[Documentação de empacotamento](https://developers.openai.com/plugins/build/plugins).

## Organização recomendada no GitHub

Manter um repositório com variantes distribuídas separadamente permite revisar o
método jurídico junto e distinguir dependências do ambiente. A estrutura desta
entrega preserva os caminhos usados pela instalação Claude:

```text
pratica-juridica-plugin/
  .claude-plugin/                 manifesto e marketplace existentes
  skills/                        versão Claude existente
  plugins/
    pratica-juridica-work/
      .codex-plugin/plugin.json
      skills/                    15 skills OpenAI adaptadas
      README.md
      LICENSE
  docs/ADAPTACAO-OPENAI.md
  tests/test_work.py
  scripts/package_work.py
```

Uma branch como `codex/adaptacao-chatgpt-work` reúne as alterações desta proposta.
O pull request é o pedido de incorporar essa branch à principal; ele não é uma
cópia permanente do plugin. Após revisar e integrar o PR, a branch pode ser removida,
e as duas variantes continuam coexistindo na principal. Não é necessário um fork
ou outro repositório. Esta proposta usa a branch `codex/adaptacao-chatgpt-work`;
a incorporação à principal depende da revisão e integração do pull request.

Não recomendo branches permanentes “Claude” e “ChatGPT” para manter produtos:
elas dificultam propagar uma correção comum e conferir divergências. Também não
recomendo duplicar todas as regras jurídicas indefinidamente. A cópia nesta etapa
facilita revisão e homologação sem quebrar a instalação original. Mudanças jurídicas
futuras devem ser avaliadas para ambas as variantes e registradas no mesmo PR.

Depois de homologar, uma refatoração separada pode extrair scripts e regras realmente
comuns para uma fonte compartilhada, com geração dos pacotes Claude e OpenAI.
Os pacotes finais devem ser autocontidos, sem links simbólicos ou caminhos que saiam
da raiz. Não convém mover o plugin Claude agora: seu marketplace aponta para `./`.
Essa mudança exige revisar o catálogo e testar atualização das instalações existentes.

Os números de versão são independentes: Claude permanece 1.2.0; Work começa em 0.1.0,
com registro da revisão de origem. Use releases ou nomes de pacote distintos.
O empacotador desta entrega inclui somente a variante OpenAI e exclui dados de execução.

## Homologação pendente

Validação local concluída em 9 de setembro de 2026: manifesto aprovado pelo
`validate_plugin.py` oficial; 15 skills aprovadas pelo `quick_validate.py` oficial;
11 testes de `tests/test_work.py` aprovados. Os testes exercitam recortes, hash,
ambiguidade, limites de caminho, normalização de workspace, geração/leitura de DOCX
e seleção de páginas em PDF PJe sintético. Também conferem links relativos das skills.
A inspeção do DOCX foi programática, sem revisão visual no Word ou renderizador.
Os testes não medem comportamento de Astra ou qualidade jurídica das entregas.

Para repetir os testes locais, use Python 3.10+ com `python-docx`, `pypdfium2`,
`pypdf` e `reportlab`, e execute `python -m unittest discover -s tests -v` na raiz.
Os validadores oficiais exigem também `PyYAML` e pertencem ao ambiente Codex,
não ao pacote distribuído. Gere o ZIP com `python scripts/package_work.py`.

Testar em uma conversa nova do Work com PDF sintético, sem bookmarks e com bookmarks;
conferir acesso aos conectores; capturar uma fonte por ferramenta; gerar e visualizar
DOCX; encerrar e retomar com os artefatos exportados. Navegação PJe depende de sessão
autenticada e deve ser testada em leitura/download autorizado. Conferir separadamente
uma peça curta, um recurso complexo, um memorial de reforço e uma citação sem fonte.

Os critérios são observáveis: concluir o escopo sem aprovações artificiais; respeitar
checkpoints solicitados; não redigir alegação sem suporte; registrar contrário relevante;
não confundir rascunho com arquivo salvo; informar exatamente o que não foi lido.
