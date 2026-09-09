#!/usr/bin/env python3
"""CLI para análise agêntica de processos judiciais grandes (PJe) em PDF.

Motor de extração sob demanda guiado pelos bookmarks do PDF. NÃO carrega o
PDF inteiro no contexto — extrai só os documentos pedidos.

Comandos:
  index   <pdf> [--json|--md]            mapa dos documentos (a partir dos bookmarks)
  peek    <pdf> --docs 10,23 [--chars N] primeiros N chars de cada doc (ranking)
  extract <pdf> --docs 10,23 --out DIR   markdown completo dos docs (rodapé limpo)
  find    <pdf> --id 240895548           resolve um id/evento do PJe → seq do doc

Dependência: pypdfium2  (pip install pypdfium2) — wheel leve, sem PyTorch.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

# ----------------------------------------------------------------------------
# Boilerplate do PJe que se repete em (quase) toda página — puro ruído p/ IA.
# ----------------------------------------------------------------------------
BOILERPLATE_RES = [
    re.compile(r"^\s*Num\.\s+\d+\s*-\s*P[áa]g\.\s+\d+\s*$", re.IGNORECASE),
    re.compile(r"^\s*Assinado eletronicamente por:", re.IGNORECASE),
    re.compile(r"^\s*https?://pje", re.IGNORECASE),
    re.compile(r"^\s*N[úu]mero do documento:", re.IGNORECASE),
    re.compile(r"^\s*Este documento foi gerado pelo usu[áa]rio", re.IGNORECASE),
]

# Título do bookmark: "Petição (Outras) | NUM: 241577420 | 27/05/2026 11:43"
TITULO_RE = re.compile(r"^(?P<tipo>.*?)\s*\|\s*NUM:\s*(?P<num>\d+)\s*\|\s*(?P<data>.+?)\s*$")

# Tipos que NÃO são peça jurídica (registramos no índice, mas não transformamos por padrão).
NAO_PECA = {
    "outros documentos", "anexo", "instrumento de procuracao",
    "cabecalho", "indice",
}

# Resolução de citações: "id 240895548", "id. 240714892", "(id 240714892)"
CITACAO_ID_RE = re.compile(r"\bid\.?\s*(\d{6,})\b", re.IGNORECASE)

# Cabeçalho/timbre do tribunal — repetido em toda peça, inútil para ranking.
LETTERHEAD_RES = [
    re.compile(r"^\s*tribunal de justi", re.IGNORECASE),
    re.compile(r"^\s*poder judici", re.IGNORECASE),
    re.compile(r"^\s*(se[çc][ãa]o|vara|gabinete|comarca|ju[íi]zo)\b", re.IGNORECASE),
    re.compile(r"^\s*(avenida|rua|av\.|pra[çc]a|estrada|rodovia|alameda|setor)\s", re.IGNORECASE),
    re.compile(r"^\s*processo\s*n", re.IGNORECASE),
    re.compile(r"^\s*(autor|r[ée]u|reu|recuperand|exequente|executad|agravante|"
               r"agravad|embargante|embargad|requerente|requerid|apelante|apelad)",
               re.IGNORECASE),
    re.compile(r"^\s*F:\(?\d", re.IGNORECASE),       # telefone do fórum
    re.compile(r"^\s*CEP[:\s]", re.IGNORECASE),
    re.compile(r"^\s*(tel\.?|fone|fax)[:\s]", re.IGNORECASE),
    re.compile(r"^\s*www\.", re.IGNORECASE),
    re.compile(r"^\s*\d{1,3}\s*$"),                    # número de página solto
]
# Linha de "rol de partes" (caixa alta longa, com vírgulas) — continuação do timbre.
ROL_PARTES_RE = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,.\-/()]{30,}$")


def _pular_letterhead(texto: str) -> str:
    """Remove o timbre do tribunal do início, para o snippet mostrar substância."""
    linhas = texto.split("\n")
    out = []
    em_cabecalho = True
    for ln in linhas:
        s = ln.strip()
        if not s:
            continue
        if em_cabecalho:
            if any(r.search(s) for r in LETTERHEAD_RES) or ROL_PARTES_RE.match(s):
                continue
            em_cabecalho = False  # primeira linha substantiva encontrada
        out.append(s)
    return "\n".join(out)


def _strip_acentos(s: str) -> str:
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower().strip()


def _abrir(pdf_path: str):
    import pypdfium2 as pdfium  # import tardio
    p = Path(pdf_path)
    if not p.exists():
        sys.exit(f"ERRO: arquivo não encontrado: {p}")
    return pdfium.PdfDocument(str(p))


def construir_indice(pdf) -> list[dict]:
    """Lê os bookmarks e monta a lista de documentos com faixas de página."""
    n = len(pdf)
    brutos = []
    for it in pdf.get_toc():
        dest = it.get_dest()
        pg = dest.get_index() if dest else None
        if pg is None:
            continue
        brutos.append((pg, it.get_title() or ""))
    brutos.sort(key=lambda x: x[0])

    docs = []
    for i, (pg, titulo) in enumerate(brutos):
        fim = (brutos[i + 1][0] - 1) if i + 1 < len(brutos) else n - 1
        m = TITULO_RE.match(titulo)
        if m:
            tipo = m.group("tipo").strip()
            num = m.group("num")
            data = m.group("data").strip()
        else:
            tipo, num, data = titulo.strip(), None, None
        is_peca = _strip_acentos(tipo) not in NAO_PECA
        docs.append({
            "seq": i,
            "tipo": tipo,
            "num": num,
            "data": data,
            "pg_ini": pg + 1,      # 1-indexed para humanos
            "pg_fim": fim + 1,
            "npags": fim - pg + 1,
            "is_peca": is_peca,
        })
    return docs


def _limpar_pagina(texto: str) -> list[str]:
    """Remove boilerplate e devolve linhas úteis."""
    out = []
    for linha in texto.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if any(r.search(linha) for r in BOILERPLATE_RES):
            continue
        out.append(linha.rstrip())
    return out


def _dewrap(linhas: list[str]) -> list[str]:
    """Junta linhas quebradas pelo PDF em parágrafos.

    Heurística: se a linha não termina em pontuação forte e a próxima começa
    em minúscula (ou dígito), é continuação → junta com espaço.
    """
    paragrafos: list[str] = []
    buf = ""
    for ln in linhas:
        s = ln.strip()
        if not s:
            if buf:
                paragrafos.append(buf.strip())
                buf = ""
            continue
        if not buf:
            buf = s
            continue
        termina_forte = buf.endswith((".", ":", ";", "!", "?"))
        proxima_minuscula = s[:1].islower() or s[:1].isdigit()
        # junta se: não terminou em pontuação forte E (próxima minúscula OU buf
        # é longo o bastante para ser prosa/lista que quebrou — ex: rol de partes)
        if (not termina_forte) and (proxima_minuscula or len(buf) > 55):
            buf += " " + s
        else:
            paragrafos.append(buf.strip())
            buf = s
    if buf:
        paragrafos.append(buf.strip())
    return [p for p in paragrafos if p]


def texto_doc(pdf, doc: dict, max_chars: int | None = None) -> str:
    """Extrai e limpa o texto de um documento (faixa de páginas)."""
    partes = []
    total = 0
    for pg in range(doc["pg_ini"] - 1, doc["pg_fim"]):
        raw = pdf[pg].get_textpage().get_text_range()
        linhas = _limpar_pagina(raw)
        if not linhas:
            continue
        partes.append((pg + 1, _dewrap(linhas)))
        total += sum(len(p) for p in partes[-1][1])
        if max_chars and total >= max_chars:
            break
    # monta texto
    blocos = []
    for pg_num, paras in partes:
        blocos.append(f"<!-- pág. {pg_num} -->")
        blocos.extend(paras)
    txt = "\n\n".join(blocos)
    if max_chars:
        txt = txt[:max_chars]
    return txt


# ----------------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------------
def cmd_index(args):
    pdf = _abrir(args.pdf)
    docs = construir_indice(pdf)
    if args.json:
        print(json.dumps(docs, ensure_ascii=False, indent=2))
        return
    # markdown (default) — compacto p/ ranking
    print(f"# Índice — {Path(args.pdf).stem}")
    print(f"\nTotal: {len(docs)} documentos / {len(pdf)} páginas\n")
    print("| seq | tipo | evento | data | pgs | peça? |")
    print("|----:|------|-------:|------|----:|:-----:|")
    for d in docs:
        peca = "sim" if d["is_peca"] else "—"
        print(f"| {d['seq']} | {d['tipo']} | {d['num'] or ''} | {d['data'] or ''} "
              f"| {d['pg_ini']}-{d['pg_fim']} ({d['npags']}) | {peca} |")


def cmd_peek(args):
    pdf = _abrir(args.pdf)
    docs = {d["seq"]: d for d in construir_indice(pdf)}
    seqs = [int(x) for x in args.docs.split(",") if x.strip() != ""]
    for seq in seqs:
        d = docs.get(seq)
        if not d:
            print(f"## seq {seq}: NÃO ENCONTRADO\n")
            continue
        # busca bastante texto (o timbre + rol de partes pode ser longo),
        # remove o cabeçalho, e só então trunca ao tamanho pedido.
        bruto = texto_doc(pdf, d, max_chars=max(args.chars * 10, 5000))
        bruto = re.sub(r"<!-- pág\. \d+ -->\n*", "", bruto).strip()
        snippet = _pular_letterhead(bruto)
        print(f"## seq {seq} — {d['tipo']} (evento {d['num']}, {d['data']}, "
              f"pg {d['pg_ini']}-{d['pg_fim']})")
        print(snippet[:args.chars])
        print()


def cmd_extract(args):
    pdf = _abrir(args.pdf)
    docs = {d["seq"]: d for d in construir_indice(pdf)}
    seqs = [int(x) for x in args.docs.split(",") if x.strip() != ""]
    out_dir = _ensure_writable(Path(args.out))
    gerados = []
    for seq in seqs:
        d = docs.get(seq)
        if not d:
            print(f"seq {seq}: NÃO ENCONTRADO", file=sys.stderr)
            continue
        corpo = texto_doc(pdf, d)
        slug = re.sub(r"[^a-z0-9]+", "-", _strip_acentos(d["tipo"]))[:30].strip("-")
        nome = f"doc_{seq:03d}_{slug}.md"
        fm = (
            "---\n"
            f"seq: {seq}\n"
            f"tipo: {d['tipo']}\n"
            f"evento: {d['num']}\n"
            f"data: {d['data']}\n"
            f"paginas: {d['pg_ini']}-{d['pg_fim']}\n"
            f"fonte: texto-nativo\n"
            "---\n\n"
        )
        (out_dir / nome).write_text(fm + corpo + "\n", encoding="utf-8")
        gerados.append((nome, len(corpo)))
    print(f"Gerados {len(gerados)} arquivo(s) em {out_dir}:")
    for nome, nchars in gerados:
        print(f"  {nome}  (~{nchars // 4} tokens)")


def cmd_find(args):
    pdf = _abrir(args.pdf)
    docs = construir_indice(pdf)
    alvo = str(args.id)
    achados = [d for d in docs if d["num"] == alvo]
    if not achados:
        print(f"Nenhum documento com evento/id {alvo}")
        return
    for d in achados:
        print(json.dumps(d, ensure_ascii=False))


# Explicit workspace: no ancestor/mount scanning or silent output relocation.
def _ensure_writable(out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    if not out_dir.is_dir():
        raise NotADirectoryError(out_dir)
    return out_dir


def _data_root() -> tuple[Path, str]:
    configured = os.environ.get("PRATICA_JURIDICA_DATA")
    if configured:
        return Path(configured).expanduser().resolve(), "PRATICA_JURIDICA_DATA"
    return Path.cwd() / "dados-juridicos", "workspace atual"


def cmd_workspace(args):
    value = args.cnj.strip()
    if not re.fullmatch(r"(?:[0-9]{20}|[0-9]{7}-[0-9]{2}\.[0-9]{4}\.[0-9]\.[0-9]{2}\.[0-9]{4})", value):
        raise ValueError("Informe CNJ com 20 dígitos, formatado ou sem pontuação")
    cnj = re.sub(r"[^0-9]", "", value)
    root, label = _data_root()
    ws = root / "processos" / cnj
    _ensure_writable(ws)
    print(str(ws.resolve()))
    print(f"[dados] {label}; confirme persistência/exportação no ambiente atual", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser(description="Análise agêntica de processos PJe.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("index"); p.add_argument("pdf")
    p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_index)

    p = sub.add_parser("peek"); p.add_argument("pdf")
    p.add_argument("--docs", required=True); p.add_argument("--chars", type=int, default=400)
    p.set_defaults(func=cmd_peek)

    p = sub.add_parser("extract"); p.add_argument("pdf")
    p.add_argument("--docs", required=True); p.add_argument("--out", default="./tmp_processo")
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("find"); p.add_argument("pdf")
    p.add_argument("--id", required=True); p.set_defaults(func=cmd_find)

    p = sub.add_parser("workspace"); p.add_argument("cnj")
    p.set_defaults(func=cmd_workspace)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
