# PJe: referências para navegação observada

O plugin original registrou navegação em agosto de 2026 no TRF-5, 1º grau,
e no TRF-1, 1º grau. Isso não comprova funcionamento atual ou nos graus recursais.

| Tribunal | Grau | Endereço histórico |
|---|---|---|
| TRF-5 | 1º | https://pje1g.trf5.jus.br |
| TRF-5 | 2º | https://pjett.trf5.jus.br |
| TRF-1 | 1º | https://pje1g.trf1.jus.br |
| TRF-1 | 2º | https://pje2g.trf1.jus.br |

Confirme tribunal e grau atual. O número CNJ conserva o órgão de origem, inclusive
em situações de tramitação recursal. Não deduza grau atual somente pelo sufixo.

A consulta observada estava em `/pje/Processo/ConsultaProcesso/listView.seam`.
Prefira o link de consulta exposto pelo portal. A busca pode distribuir o CNJ em
sequencial, dígito, ano, ramo, tribunal e órgão. Confira cada valor após preencher.

Os IDs históricos tinham prefixo `fPP:numeroProcesso:` e sufixos
`numeroSequencial`, `numeroDigitoVerificador`, `Ano`, `ramoJustica`,
`respectivoTribunal` e `NumeroOrgaoJustica`. O botão de busca era `fPP:searchProcessos`.
Use esses nomes como pistas de localização, somente após observar o DOM atual.
Execute ações pela API documentada da ferramenta, sem injetar scripts de mutação
para contornar limites do navegador.

Confira número, partes e órgão no resultado. Abra o link observado dos autos;
não construa URLs internas com tokens de sessão. Na barra geral dos autos, localize
o download do processo completo, distinguindo-o do download de documento individual.
Preserve opções de índice do PDF. Confirme o escopo e a ordenação selecionados.

Se houver aviso ou diálogo, leia seu conteúdo e use o controle documentado para
respondê-lo. Se o controle não existir, peça intervenção do usuário. Não substitua
`window.confirm`. Após iniciar a geração, aguarde a mudança observável de estado
e confira o resultado pelo mecanismo de download disponível.

Resultado vazio exige revisar filtros, grau e permissões antes de concluir ausência.
Mudança de layout exige nova observação, não repetição cega de cliques. Registre a
limitação e o passo alterado; editar a skill é uma tarefa de manutenção separada.
