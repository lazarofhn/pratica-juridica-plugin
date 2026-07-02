#!/usr/bin/env python3
"""citar.py — resolve `@citacao-ref` extraindo a ementa VERBATIM do transcript.

A busca no `Juris_br` (MCP) grava o resultado no transcript da sessão. O local varia:
Claude Code = `~/.claude/projects/**/*.jsonl`; Cowork = sob um mount (ex.:
`.../mnt/.claude/projects/`, que NÃO é o HOME). Este módulo procura em vários locais
(env `CLAUDE_PROJECTS_DIR` → HOME → subindo a partir do diretório atual) e lê de lá o
bloco de resultado da fonte
pelo número do processo, extrai a `Ementa` exatamente como o MCP retornou, aplica
recorte (itens / trecho) e devolve o texto. Assim a peça cita sem redigitação e a
citação fica comprovadamente fiel à fonte.

FIDELIDADE: só se normaliza ESPAÇO EM BRANCO (junta linhas quebradas do resultado).
Nunca se altera caractere dentro de palavra.

Uso (teste):
    python citar.py --processo "REsp 2.136.610" [--itens 1-2] \
        [--trecho 'de "..." ate "..."'] [--grifo "trecho a marcar"] [--transcript PATH]
"""

import glob
import json
import os
import re


# --------------------------------------------------------------- transcripts
def _candidate_project_dirs():
    """Locais possíveis do `.claude/projects` (onde ficam os transcripts .jsonl).
    Cobre Claude Code (HOME) e Cowork (transcript sob um mount, p.ex.
    `/sessions/<id>/mnt/.claude/projects`, que NÃO é o HOME). Ordem: env override →
    HOME → subindo a partir do diretório atual (direto e sob `mnt/`)."""
    cands = []
    env = os.environ.get("CLAUDE_PROJECTS_DIR")
    if env:
        cands.append(env)
    cands.append(os.path.join(os.path.expanduser("~"), ".claude", "projects"))
    cur = os.path.abspath(os.getcwd())
    while True:
        cands.append(os.path.join(cur, ".claude", "projects"))
        cands.append(os.path.join(cur, "mnt", ".claude", "projects"))
        parent = os.path.dirname(cur)
        if parent == cur:
            break
        cur = parent
    seen, out = set(), []
    for c in cands:
        if c and c not in seen:
            seen.add(c)
            if os.path.isdir(c):
                out.append(c)
    return out


def transcripts(newest_first=True):
    files = []
    for d in _candidate_project_dirs():
        files.extend(glob.glob(os.path.join(d, "**", "*.jsonl"), recursive=True))
    files = list(dict.fromkeys(files))  # dedup preservando ordem
    files.sort(key=os.path.getmtime, reverse=newest_first)
    return files


def _collect_strings(obj, out):
    """Coleta todos os valores string; desembrulha wrappers {"result": "..."}
    (a saída do MCP) para recuperar as quebras de linha reais da ementa."""
    if isinstance(obj, str):
        s = obj
        if '"result"' in s and s.lstrip().startswith("{"):
            try:
                inner = json.loads(s)
                if isinstance(inner, dict) and isinstance(inner.get("result"), str):
                    out.append(inner["result"])
                    return
            except json.JSONDecodeError:
                pass
        out.append(s)
    elif isinstance(obj, dict):
        for v in obj.values():
            _collect_strings(v, out)
    elif isinstance(obj, list):
        for v in obj:
            _collect_strings(v, out)


# Separador de chunk (uma mensagem/resultado do transcript). Impede que um bloco
# atravesse a fronteira de um resultado e engula texto de mensagens posteriores.
_CHUNK_SEP = "\n\x1e\n"


def _decoded_text(path):
    chunks = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            _collect_strings(obj, chunks)
    return _CHUNK_SEP.join(chunks)


# --------------------------------------------------------------- parsing dos resultados
# Blocos de resultado do juris_br. Dois formatos:
#   STJ/STF/TCU/TRF5: "### Resultado N (ID: ...) ... **Processo**: ... **Ementa**:\n<txt>\n---"
#   RFB/CARF:         "### N. <rótulo com nº> — ID `...` ... > <ementa em blockquote>\n---"
_BLOCK_HDR = re.compile(r"^###\s+(?:Resultado\b|\d+\.\s)", re.M)
# Cabeçalho do resultado de DETALHES (ementa completa, não truncada):
# "## <fonte> — Acórdão/Solução ID ...". Ementas grandes só saem inteiras aqui.
_DETALHE_HDR = re.compile(r"^##\s+.*\bID\b.*$", re.M)


def _norm_proc(s):
    return re.sub(r"[^0-9a-z]", "", s.lower())


def _field(block, name):
    m = re.search(r"\*\*" + re.escape(name) + r"\*\*:\s*(.+)", block)
    return m.group(1).strip() if m else ""


def _iter_blocks(text):
    """Cada bloco vai do seu cabeçalho '### ' até o próximo, cortado no
    primeiro separador '---' (fim do resultado)."""
    starts = sorted([m.start() for m in _BLOCK_HDR.finditer(text)] +
                    [m.start() for m in _DETALHE_HDR.finditer(text)])
    for i, s in enumerate(starts):
        nxt = starts[i + 1] if i + 1 < len(starts) else len(text)
        block = text[s:nxt]
        cut = re.search(r"\n\s*---\s*\n|\x1e", block)
        if cut:
            block = block[:cut.start()]
        yield block


def _ementa_of(block):
    # formato DETALHES (ementa completa): seção "### Ementa"
    m = re.search(r"###\s*Ementa\s*\n(.*)", block, re.DOTALL)
    if m and m.group(1).strip():
        return m.group(1).strip()
    # formato STJ: após "**Ementa**:"
    m = re.search(r"\*\*Ementa\*\*:\s*\n?(.*)", block, re.DOTALL)
    if m and m.group(1).strip():
        return m.group(1).strip()
    # formato RFB/CARF: ementa nas linhas de citação (iniciadas por '>')
    q = [re.sub(r"^\s*>\s?", "", ln) for ln in block.split("\n") if ln.lstrip().startswith(">")]
    if q:
        return "\n".join(q).strip()
    return ""


def find_ementa(processo, transcript=None):
    """Retorna (ementa_bruta, caminho_fonte) ou (None, None). Casa o localizador
    (nº de processo/acórdão/solução) no cabeçalho do bloco ou no campo Processo.
    Havendo mais de uma ocorrência (p.ex. busca truncada + `detalhes` completo),
    devolve a ementa MAIS LONGA — isto é, a versão íntegra vinda do detalhes."""
    alvo = _norm_proc(processo)
    best, best_src = None, None
    files = [transcript] if transcript else transcripts()
    for path in files:
        text = _decoded_text(path)
        for block in _iter_blocks(text):
            header = block.split("\n", 1)[0]
            hay = _norm_proc(header + " " + _field(block, "Processo"))
            if alvo and alvo in hay:
                em = _ementa_of(block)
                if em and (best is None or len(em) > len(best)):
                    best, best_src = em, path
    return best, best_src


# --------------------------------------------------------------- recorte / grifo
def collapse(s):
    return re.sub(r"\s+", " ", s).strip()


def _split_itens(ementa):
    parts = re.split(r"(?m)^\s*(\d+)\.\s+", ementa)
    itens = {}
    for i in range(1, len(parts) - 1, 2):
        itens[int(parts[i])] = parts[i + 1]
    return itens


def _parse_range(s):
    s = s.strip()
    if "-" in s:
        a, b = s.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x) for x in re.split(r"[,\s]+", s) if x]


def _parse_trecho(s):
    m = re.search(r'de\s+"(.+?)"\s+at[eé]\s+"(.+?)"', s, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    if "|" in s:
        a, b = s.split("|", 1)
        return a.strip(), b.strip()
    return s.strip(), None


def _extract_span(texto, ini, fim, processo):
    ini_n = collapse(ini)
    i = texto.find(ini_n)
    if i < 0:
        raise LookupError(f"Âncora inicial não encontrada em {processo}: {ini_n!r}")
    if texto.find(ini_n, i + 1) >= 0:
        raise LookupError(f"Âncora inicial AMBÍGUA em {processo}: {ini_n!r}")
    if not fim:
        return texto[i:]
    fim_n = collapse(fim)
    j = texto.find(fim_n, i)
    if j < 0:
        raise LookupError(f"Âncora final não encontrada em {processo}: {fim_n!r}")
    return texto[i:j + len(fim_n)]


def find_grifo(texto, grifo):
    g = collapse(grifo)
    i = texto.find(g)
    if i < 0:
        return None
    return (i, i + len(g))


def resolve(processo, itens=None, trecho=None, transcript=None):
    """Devolve (texto_resolvido, caminho_fonte)."""
    ementa, src = find_ementa(processo, transcript)
    if ementa is None:
        raise LookupError(
            f"Ementa não encontrada no transcript para {processo!r}. "
            f"Rode a busca no Juris_br nesta sessão antes de citar (regra do rastro)."
        )
    if itens:
        mapa = _split_itens(ementa)
        nums = _parse_range(itens)
        faltando = [n for n in nums if n not in mapa]
        if faltando:
            raise LookupError(f"Itens {faltando} não encontrados na ementa de {processo}")
        texto = " ".join(f"{n}. {collapse(mapa[n])}" for n in nums)
    else:
        texto = collapse(ementa)
    if trecho:
        ini, fim = _parse_trecho(trecho)
        texto = _extract_span(texto, ini, fim, processo)
    return texto, src


# --------------------------------------------------------------- fonte: autos (workspace)
def _clean_autos(text):
    """Remove artefatos da extração do PJe: frontmatter, marcadores de página,
    cabeçalhos 'Documento id N - Tipo' e rodapés 'Num. N - Pág. N Assinado...'.
    Só mexe em ruído estrutural; não altera o texto jurídico."""
    text = re.sub(r"^\s*---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)  # frontmatter
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)                    # <!-- pág. N -->
    text = re.sub(r"Num\.\s*\d+\s*-\s*P[áa]g\.\s*\d+\s*Assinado eletronicamente por:[^\n]*",
                  " ", text)                                                     # rodapé
    text = re.sub(r"Documento id \d+ -\s*\w+", " ", text)                        # cabeçalho de página
    # rodapé de página do inteiro teor do STJ (pdftotext), que quebra a frase no meio
    text = re.sub(r"(?m)^\s*Documento:\s*\d+\s*-\s*Inteiro Teor.*$", " ", text)
    return text


def _find_doc(workspace, doc=None, arquivo=None):
    if arquivo:
        return arquivo if os.path.isabs(arquivo) else os.path.join(workspace or ".", arquivo)
    if doc is not None and workspace:
        hits = sorted(glob.glob(os.path.join(workspace, f"doc_{int(doc):03d}_*.md")))
        if hits:
            return hits[0]
    return None


def resolve_autos(workspace, doc=None, arquivo=None, itens=None, trecho=None):
    """Extrai texto VERBATIM de um documento dos autos (workspace do processo)."""
    path = _find_doc(workspace, doc, arquivo)
    if not path or not os.path.exists(path):
        raise LookupError(
            f"Documento dos autos não encontrado (doc={doc}, arquivo={arquivo}, workspace={workspace})."
        )
    with open(path, encoding="utf-8") as f:
        texto = collapse(_clean_autos(f.read()))
    if itens:
        mapa = _split_itens(texto)
        nums = _parse_range(itens)
        faltando = [n for n in nums if n not in mapa]
        if faltando:
            raise LookupError(f"Itens {faltando} não encontrados em {os.path.basename(path)}")
        texto = " ".join(f"{n}. {collapse(mapa[n])}" for n in nums)
    if trecho:
        ini, fim = _parse_trecho(trecho)
        texto = _extract_span(texto, ini, fim, os.path.basename(path))
    return texto, path


# --------------------------------------------------------------- CLI (teste)
def main():
    import argparse
    ap = argparse.ArgumentParser(description="Resolve @citacao-ref (teste).")
    ap.add_argument("--fonte", default="", help="'autos' para ler do workspace; vazio = juris_br")
    ap.add_argument("--processo")
    ap.add_argument("--doc")
    ap.add_argument("--arquivo")
    ap.add_argument("--workspace")
    ap.add_argument("--itens")
    ap.add_argument("--trecho")
    ap.add_argument("--grifo")
    ap.add_argument("--transcript")
    a = ap.parse_args()
    if a.fonte.lower() == "autos":
        texto, src = resolve_autos(a.workspace, doc=a.doc, arquivo=a.arquivo,
                                   itens=a.itens, trecho=a.trecho)
    else:
        texto, src = resolve(a.processo, itens=a.itens, trecho=a.trecho, transcript=a.transcript)
    print(f"[fonte: {src}]")
    print(texto)
    if a.grifo:
        print(f"[grifo span: {find_grifo(texto, a.grifo)}]")


if __name__ == "__main__":
    main()
