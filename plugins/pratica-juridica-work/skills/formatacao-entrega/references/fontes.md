# Fontes explícitas para transcrição

Esta variante elimina busca automática em conversas privadas e correspondência
aproximada por número de processo. Cada `@citacao-ref` aponta para um arquivo exato
e para seu SHA-256. A sintaxe antiga por `processo` ou `doc` deve ser migrada.

Salve o arquivo recebido ou exporte o resultado original por mecanismo determinístico
disponível, em UTF-8, dentro do workspace. Registre em `pesquisas.jsonl` sua origem,
URL/ID, órgão, processo, decisão, data, tipo de documento, ferramenta/parâmetros e
horário de captura. Para autos, registre também hash do PDF, evento e páginas.
Texto extraído de PDF exige conferência com o original quando a literalidade for
decisiva. Não reescreva a fonte com o modelo para simular uma captura.

Calcule o hash dos bytes efetivamente salvos:

```text
python citar.py --hash <arquivo>
```

Exemplo estrutural (substitua os campos por dados da fonte real):

```text
@citacao-ref
arquivo: fontes/acordao.txt
sha256: <hash SHA-256 de 64 caracteres>
trecho: de "âncora inicial única" ate "âncora final única"
grifo: expressão contida no recorte
ref: Tribunal, classe e número, órgão, relator, data, documento/página ou URL
```

`arquivo`, `sha256` e `ref` são obrigatórios. O caminho é relativo ao diretório do
rascunho ou absoluto dentro desse mesmo workspace; saída para diretório externo é
rejeitada. `trecho` e `grifo` são opcionais. `itens: 1-2` funciona apenas se o arquivo
contiver texto com itens numerados no início das linhas; não use em JSON bruto.
Sem recorte, todo o conteúdo textual será transcrito: prefira âncoras para excluir
cabeçalhos e metadados. Âncoras repetidas são rejeitadas; amplie-as para desambiguar.
Para trechos separados, use blocos separados e atribua a mesma fonte.

O script verifica integridade e normaliza somente espaços em branco. Ele não remove
rodapés automaticamente, não interpreta respostas JSON e não identifica uma ementa
por heurística. Se o texto veio dividido por ruído de extração, prepare uma extração
determinística conferida com o original, conservando original e transformação.

O hash não certifica autoria, origem oficial, atualização ou ratio decidendi. A
referência é conferida pela skill `verificacao-citacoes`. Se não for possível salvar
texto fiel, faça paráfrase com fonte e alcance explícitos ou entregue a transcrição
como pendência; não declare fidelidade automática. Citações manuais em `@citacao`
continuam possíveis, mas exigem confronto literal independente com a fonte.
