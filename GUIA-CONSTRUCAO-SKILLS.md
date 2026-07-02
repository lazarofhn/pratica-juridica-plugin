# Guia de Construção das Skills — plugin pratica-juridica

Documento-mãe para construir as skills uma a uma. Consolida a ideia bruta do José
+ as decisões de arquitetura já travadas. **Revisar antes de construir.**

## Decisões travadas
1. **Relatórios unificados** em `relatorio` com modo `interno|externo`. O modo
   externo **filtra conteúdo** (não só suaviza o tom): não expõe probabilidade
   crua de êxito nem estratégia interna.
2. **`peca-processual-base` (camada E)** guarda as orientações comuns às peças
   protocoladas; recurso/específica/simples a puxam.
3. **Aprovação do plano só em peças grandes**: quando `plano-de-respostas` gerar
   N gerações, mostrar o plano e aguardar o ok antes de escrever. Peça de 1
   geração segue direto.

## Mapa de skills (revisado)
```
A · analise-processual (orquestrador)
B · obter-processo (opcional, Chrome)
C · analise-processo-pje (retrieval no PDF — migrar a real)

D · OUTPUTS:
    analise-estrategia   (novo — modo reconhecimento/planejamento, sem peça)
    peca-recurso
    peca-especifica
    peca-simples
    memorial             (novo — peça híbrida entregue ao julgador)
    relatorio            (interno|externo — fundido)

E · COMPARTILHADAS:
    peca-processual-base (novo — orientações comuns às peças protocoladas)
    pesquisa-juridica    (perfis: processual|material; fontes: juris_br + know-how)
    escrita-juridica     (registros: peça|interno|externo)
    plano-de-respostas   (sempre; decide 1 vs N gerações)
    formatacao-entrega   (→ .docx timbrado; só externos)
    verificacao-citacoes (checagem contra as fontes)
```

## Fluxo do orquestrador
1. Definir objetivo → escolher a skill de output (ou `analise-estrategia`).
2. Garantir acesso ao processo (PDF manual por padrão; `obter-processo` se pedido).
3. Analisar seletivamente (`analise-processo-pje`), guiado pelo objetivo.
4. **`plano-de-respostas`** (sempre): índice numerado + nº de gerações. Se N>1 →
   mostrar plano e aguardar aprovação.
5. Executar o output (skill D), que puxa a camada E conforme necessário.
6. `verificacao-citacoes` antes de fechar. `formatacao-entrega` se externo.

---

## Template — anatomia de toda skill fina (D)
Toda skill de output segue esta ordem fixa:
1. **Quando ativar** — como o orquestrador a escolhe; como identificar o subtipo.
2. **Perguntas antes de começar** — o que esclarecer se o usuário omitiu.
3. **Estrutura do documento** — seções e de onde vêm (ex.: artigo do CPC → fallback).
4. **Plano de respostas** — como tende a segmentar + regras de ouro de segmentação.
5. **Pesquisa** — perfis (processual/material), ênfase padrão, profundidade, quando perguntar.
6. **Escrita** — registro/tom.
7. **Entrega** — externo? `.docx`/timbrado?
8. **Verificação** — o que conferir.
9. **Regras de ouro / vícios a evitar** — específicas do tipo.

---

## Especificação das skills D

### analise-estrategia  (modo reconhecimento/planejamento — sem peça)
1. **Ativar:** usuário quer *entender* o processo ou *planejar estratégia*, sem
   pedir peça — ou como **fase preliminar** antes de confeccionar algo.
2. **Perguntas:** foco? (dúvida pontual / panorama geral / avaliação de risco /
   próximos passos). Se for preliminar a uma peça, confirmar o objetivo final.
3. **Estrutura:** livre — panorama → questões-chave → cenários/riscos →
   recomendação → próximos passos.
4. **Plano:** normalmente 1 geração; se estratégia densa, segmentar por questão.
5. **Pesquisa:** sob demanda; se a estratégia depende de tese, aciona
   `pesquisa-juridica`. Pode ser leve.
6. **Escrita:** registro `interno` (franco; é para o próprio escritório).
7. **Entrega:** interno; formato simples.
8. **Verificação:** se citar algo.
9. **Regra de ouro:** não vira peça — é análise. Pode servir de insumo para,
   em seguida, rotear a uma skill de peça.

### peca-recurso
1. **Ativar:** objetivo = recorrer.
2. **Perguntas — identificar o recurso:** dúvida do usuário / omitido ("faça o
   recurso dessa decisão") / já indicado ("apelação contra a sentença"). **Se
   omitido → informar e perguntar se concorda com o cabimento ANTES de confeccionar.**
3. **Estrutura:** buscar no **artigo do CPC** que regula o recurso; fallback =
   Fatos → Requisitos de Admissibilidade → Fundamentos → Pedidos.
4. **Plano:** subsegmentável. **REGRA DE OURO — RE/REsp:** salvo comando em
   contrário, dedicar **uma resposta por requisito de admissibilidade**
   (repercussão geral, prequestionamento, etc.), pois a falta de fundamentação
   específica de um requisito derruba o recurso.
5. **Pesquisa:** puxa `peca-processual-base`; **ênfase média-alta em
   admissibilidade por padrão** (tempestividade, cabimento, custas); material
   segmentado por fundamento.
6. **Escrita:** registro `peça`.
7. **Entrega:** externo → `.docx`/timbrado.
8. **Verificação:** obrigatória.
9. **Regras de ouro:** admissibilidade de RE/REsp; fundamentação específica de
   cada requisito é inegociável.

### peca-especifica
1. **Ativar:** peça com previsão/nomenclatura própria no CPC (contestação,
   réplica, impugnação ao cumprimento de sentença, embargos à execução, embargos
   de terceiro…). A dica vem da **nomenclatura no prompt do usuário**.
   > ⚠️ **Embargos de declaração NÃO entram aqui** — é recurso → `peca-recurso`.
   > Aqui só cabem embargos que são **incidentes/ações** (à execução, de terceiro).
2. **Perguntas:** confirmar qual peça, se ambíguo.
3. **Estrutura:** onde a peça está prevista no CPC + doutrina; requisitos próprios.
4. **Plano:** por causa de pedir / tópico.
5. **Pesquisa:** `peca-processual-base`; **sem** a ênfase-padrão de admissibilidade
   dos recursos; jurisprudência processual **só se** o usuário enfatizar questão
   processual.
6–8. Padrão de peça (registro `peça`; externo; verificação obrigatória).
9. **Regra de ouro:** identificar a previsão/nomenclatura específica correta.

### peca-simples
1. **Ativar:** manifestação **sem** nomenclatura/requisitos específicos no CPC;
   guiada pelo **comando** (do usuário ou do despacho/decisão que intimou a parte).
2. **Perguntas:** o que a intimação/comando pede, se não estiver claro.
3. **Estrutura:** livre, guiada pelo comando; costuma ser atrelada a fatos.
4. **Plano:** ⚠️ **não presumir que é rasa** — pode ser tão densa quanto um
   recurso. Depende do `plano-de-respostas` como as demais.
5. **Pesquisa:** sob demanda conforme o conteúdo.
6–8. Padrão de peça.
9. **Regra de ouro:** "simples" = sem previsão específica no CPC, **não** = curta.

### memorial
1. **Ativar:** processo **pendente de julgamento** (1º grau ou instância recursal);
   usuário quer entregar memorial ao(s) julgador(es).
2. **Perguntas:** qual a **peça-base** em julgamento (inicial / recurso / …)?
   Alguma ênfase estratégica diferente da peça original?
3. **Estrutura:** resumo das alegações/fundamentos da peça-base, com **ênfase nos
   precedentes decisivos**; sempre atrelado à peça que resume.
4. **Plano:** por eixo argumentativo; costuma ser mais enxuto.
5. **Pesquisa:** reaproveita a fundamentação **já nos autos**; pode reforçar os
   precedentes decisivos (juris_br) — mas **sem nova ratio**.
6. **Escrita:** registro `peça` (persuasivo, dirigido ao julgador), enxuto.
7. **Entrega:** externo → `.docx`/timbrado.
8. **Verificação:** obrigatória + **checagem especial: nenhum argumento/ratio
   fora dos autos**.
9. **REGRA DE OURO:** o memorial **não inova** a argumentação. Pode mudar a
   *ênfase* dos argumentos, mas não pode introduzir *ratio* que não esteja nos autos.

### relatorio  (modo interno|externo)
1. **Ativar:** objetivo = informar sobre o processo (não é peça).
2. **Perguntas:** destinatário (escritório/cliente), se não estiver claro.
3. **Estrutura:** situação atual → o que está em jogo → [interno: riscos,
   probabilidade, estratégia] → próximos passos.
4. **Plano:** normalmente 1 geração; segmentar se vários processos/temas.
5. **Pesquisa:** base interna do que afirmar; ao cliente normalmente não se cita.
6. **Escrita:** registro `interno` OU `externo`.
7. **Entrega:** externo → `.docx`/timbrado; interno → formato simples.
8. **Verificação:** se afirmar algo dependente de fonte.
9. **Regras de ouro:** externo **nunca omite** situação negativa, mas equilibra
   com solução/conforto (ex.: "decisão negativa, mas já preparamos o recurso, com
   tema de repercussão geral favorável"). Externo **não** expõe probabilidade crua
   nem estratégia interna. Interno é franco/"raw".

---

## Especificação das skills E (compartilhadas)

### peca-processual-base  (novo — puxada por recurso/específica/simples e, em parte, memorial)
Orientações comuns às peças protocoladas:
- **Endereçamento** conforme juízo/tribunal.
- **Estrutura padrão:** Fatos → Admissibilidade/Cabimento → Fundamentos →
  Pedidos (subsegmentável pelo plano).
- **Pesquisa processual:** profundidade **variável**. Às vezes o conhecimento da
  própria IA basta, mas **conferir no `know-how`** (artigo do CPC + capítulo de
  doutrina do tema). Jurisprudência **quando o usuário enfatizar** ou a questão
  for muito discutida no processo. **Na dúvida sobre profundidade, perguntar.**
- **Pesquisa material:** **segmentada por assunto** conforme `plano-de-respostas`;
  buscar em juris_br + know-how.

### pesquisa-juridica
Perfis `admissibilidade|mérito|processual`; fontes lei+doutrina (know-how) e
jurisprudência (juris_br); navegar o know-how pelo índice (`ler_orientacao`
primeiro). Detalhe a formulação de query por perfil/fonte. *(já esboçada)*

### escrita-juridica
Registros `peça|interno|externo`; centraliza tom e vícios a evitar. *(já esboçada)*

### plano-de-respostas
Sempre roda antes de escrever; índice numerado + decisão de segmentação (1 vs N
gerações); gatilho: ≥2 fundamentos/causas, tutela+mérito, ou >~10 págs. *(já esboçada)*

### formatacao-entrega
Tipografia, timbrado, geração de `.docx`; só outputs externos. *(já esboçada)*

### verificacao-citacoes
Confere jurisprudência (juris_br), lei/doutrina (know-how), referências ao
processo e números/datas antes de fechar. *(já esboçada)*

---

## Ordem de construção sugerida
1. `peca-processual-base` (destrava as 3 peças protocoladas).
2. `pesquisa-juridica` + `escrita-juridica` (compartilhadas, usadas por todas).
3. `verificacao-citacoes` (maior risco).
4. `peca-recurso` → `peca-especifica` → `peca-simples`.
5. `memorial`, `relatorio`, `analise-estrategia`.
6. `formatacao-entrega`.

**Já prontas:** `analise-processo-pje` (migrada — SKILL.md + scripts/processo.py).
**Em stand-by:** `obter-processo` (download manual cobre; não construir por ora).
