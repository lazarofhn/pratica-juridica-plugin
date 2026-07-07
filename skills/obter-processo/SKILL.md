---
name: obter-processo
description: (OPCIONAL / camada B) Baixa a íntegra de um processo automatizando a navegação no sistema processual via extensão do Claude no Chrome. Use SOMENTE quando o usuário pedir explicitamente o download automático e o sistema-alvo estiver mapeado. Para o caso comum, o download manual é mais rápido — prefira apontar o PDF já baixado.
---

> **⚙️ Regra de uso — pipeline do plugin.** A orquestração geral deste plugin (o fluxo
> de ponta a ponta: análise → plano de respostas → pesquisa → escrita → verificação →
> entrega) está definida na skill **`analise-processual`**. Se o usuário acionou **esta**
> skill diretamente, **pergunte antes de executar**: ele quer **(a) seguir o pipeline do
> plugin** (via `analise-processual` — recomendado para trabalho completo: ancora nos
> autos, usa checkpoints e verificação de citações) ou **(b) usar esta skill de forma
> avulsa** (isolada, apenas o que ela faz)? Prossiga conforme a escolha do usuário.

# Obter Processo (aquisição automatizada)

**Camada B — opcional.** O default do plugin é o usuário fornecer o PDF baixado manualmente. Só use isto quando compensar (ver trade-off).

## Quando compensa (e quando não)
- ✅ Sistema onde baixar a íntegra é multi-clique/penoso.
- ✅ Processos gigantes (600mb+) onde vale **selecionar** o que baixar (corte temporal / tipo de peça) antes de baixar tudo.
- ❌ Baixar 1 processo pequeno de um sistema fácil — o manual ganha. Não use.

## Fluxo (via mcp__claude-in-chrome__*)
1. Usuário fornece o número do processo e faz **login/certificado ele mesmo** (nunca automatize credencial).
2. Navegar até os autos → localizar a opção de download da íntegra.
3. (Processos enormes) Ler o índice/lista de peças e baixar seletivamente.
4. Entregar o caminho do arquivo à camada C.

## Um sub-caminho por sistema (cada um é diferente)
- [ ] PJe
- [ ] eproc
- [ ] Projudi
- [ ] esaj
- [ ] (outros que você usar)

## TODO
- [ ] Mapear o caminho de navegação de CADA sistema como um bloco próprio.
- [ ] Medir o tempo real vs. manual antes de investir em cada sistema.
