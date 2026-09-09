#!/usr/bin/env python3
"""build_docx.py — converte uma peça marcada (.md/.txt) em .docx no padrão da casa.

Padrão de formatação: ver ../assets/padrao-formatacao.md (fonte da verdade).
Esta é a implementação determinística daquele padrão.

Uso:
    python build_docx.py <entrada.md> --out <saida.docx>

A ENTRADA usa blocos marcados por uma diretiva `@tag` no início da linha. Cada
bloco vai do seu `@tag` até o próximo. Tags reconhecidas:

    @enderecamento   Endereçamento (14pt negrito, justificado)
    @identificacao   Processo/classe/partes (11pt negrito; linhas coladas)
    @titulo          Título da peça (14pt negrito, CENTRALIZADO)
    @corpo           Parágrafos de texto (11pt, justificado, recuo 1ª linha 2cm)
    @secao           Título de seção, ex. "1. DA SÍNTESE..." (11pt negrito, justif.)
    @citacao         Transcrição (11pt negrito, recuo esq. 2cm, entre aspas curvas)
    @citacao-ref     Fonte UTF-8 explícita: arquivo, sha256 e ref obrigatórios.
                     Opcionais: itens, trecho, grifo (repetível).
                     Ver ../references/fontes.md para o contrato completo.
    @pedidos         Itens a) b) c) (11pt, justif., recuo esq. 2cm)
    @fecho           Fecho, ex. "Nestes termos, pede deferimento." (11pt, justif.)
    @data            Local e data (11pt, CENTRALIZADO)
    @assinatura      1ª linha = nome (negrito); demais = OAB etc. (CENTRALIZADO)

Dentro de @corpo e @pedidos, parágrafos/itens são separados por LINHA EM BRANCO.
O conversor separa os blocos por UM parágrafo vazio (a "respiração" do padrão);
o espaçamento automático antes/depois fica sempre em zero.

Requer: pip install python-docx
"""

import argparse
import os
import sys

try:
    from docx import Document
    from docx.shared import Pt, Cm
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX
except ImportError:
    sys.exit("Falta a dependência: pip install python-docx")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import citar  # resolve @citacao-ref from an explicit, hash-checked source

# diretório do rascunho e das fontes explícitas; definido no main
WORKSPACE = None

FONTE = "Cambria"
IDIOMA = "pt-BR"
RECUO = 2.0          # cm — recuo de 1ª linha (corpo) e recuo esquerdo (citação/pedidos)
ENTRELINHAS = 1.15

TAGS = {
    "enderecamento", "identificacao", "titulo", "corpo", "secao",
    "citacao", "citacao-ref", "pedidos", "fecho", "data", "assinatura",
}

ALIGN = {
    "justify": WD_ALIGN_PARAGRAPH.JUSTIFY,
    "center": WD_ALIGN_PARAGRAPH.CENTER,
    "left": WD_ALIGN_PARAGRAPH.LEFT,
}


# ---------------------------------------------------------------- documento base
def novo_documento():
    doc = Document()

    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(4.0)
    sec.bottom_margin = Cm(3.5)
    sec.left_margin = Cm(3.5)
    sec.right_margin = Cm(2.75)
    sec.header_distance = Cm(1.25)
    sec.footer_distance = Cm(1.25)

    normal = doc.styles["Normal"]
    normal.font.name = FONTE
    normal.font.size = Pt(11)
    pf = normal.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = ENTRELINHAS
    # idioma pt-BR no estilo padrão
    rpr = normal.element.get_or_add_rPr()
    lang = OxmlElement("w:lang")
    lang.set(qn("w:val"), IDIOMA)
    rpr.append(lang)
    return doc


def add_par(doc, texto, *, size=11, bold=False, italic=False,
            align="justify", first_indent=None, left_indent=None):
    p = doc.add_paragraph()
    p.alignment = ALIGN[align]
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = ENTRELINHAS
    if first_indent is not None:
        pf.first_line_indent = Cm(first_indent)
    if left_indent is not None:
        pf.left_indent = Cm(left_indent)
    run = p.add_run(texto)
    run.font.name = FONTE
    # garante Cambria também para caracteres estendidos
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs"):
        rfonts.set(qn(attr), FONTE)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    return p


def add_citacao(doc, texto, grifos=(), suffix=""):
    """Citação (11pt negrito, recuo esq. 2cm, aspas curvas). O(s) trecho(s) em
    `grifos` recebem realce marca-texto (amarelo). `suffix` (ex.: atribuição do
    julgado) vai após a aspa de fechamento, sem realce."""
    p = doc.add_paragraph()
    p.alignment = ALIGN["justify"]
    pf = p.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = ENTRELINHAS
    pf.left_indent = Cm(RECUO)

    full = f"“{texto}”"
    if suffix:
        full += f" {suffix}"

    marks = []
    for g in grifos:
        sp = citar.find_grifo(texto, g)
        if sp:
            marks.append((sp[0] + 1, sp[1] + 1))  # +1 pela aspa de abertura
    marks.sort()

    def _run(s, hl):
        r = p.add_run(s)
        r.font.name = FONTE
        rpr = r._element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = OxmlElement("w:rFonts")
            rpr.append(rfonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            rfonts.set(qn(attr), FONTE)
        r.font.size = Pt(11)
        r.font.bold = True
        if hl:
            r.font.highlight_color = WD_COLOR_INDEX.YELLOW

    pos = 0
    for a, b in marks:
        if a > pos:
            _run(full[pos:a], False)
        _run(full[a:b], True)
        pos = b
    if pos < len(full):
        _run(full[pos:], False)
    return p


def branco(doc):
    """Parágrafo vazio — a 'respiração' entre blocos do padrão."""
    add_par(doc, "")


# ---------------------------------------------------------------- parsing
def ler_blocos(texto):
    """Divide o texto em blocos (tag, conteudo) pelas diretivas @tag."""
    blocos = []
    tag_atual = None
    buffer = []

    def flush():
        if tag_atual is not None:
            blocos.append((tag_atual, "\n".join(buffer).strip("\n")))

    for linha in texto.splitlines():
        marca = linha.strip()
        if marca.startswith("@") and marca[1:].strip().lower() in TAGS:
            flush()
            tag_atual = marca[1:].strip().lower()
            buffer = []
        else:
            buffer.append(linha)
    flush()
    return blocos


def paragrafos(conteudo):
    """Separa um bloco em parágrafos por linha em branco."""
    partes, atual = [], []
    for linha in conteudo.splitlines():
        if linha.strip() == "":
            if atual:
                partes.append(" ".join(x.strip() for x in atual))
                atual = []
        else:
            atual.append(linha)
    if atual:
        partes.append(" ".join(x.strip() for x in atual))
    return partes


# ---------------------------------------------------------------- render por tag
def render(doc, blocos):
    primeiro = True
    for tag, conteudo in blocos:
        if not primeiro:
            branco(doc)          # respiração entre blocos
        primeiro = False

        if tag == "enderecamento":
            for i, par in enumerate(paragrafos(conteudo)):
                if i:
                    branco(doc)
                add_par(doc, par, size=14, bold=True, align="justify")

        elif tag == "identificacao":
            # linhas coladas (bloco compacto), 12pt negrito
            for linha in [l for l in conteudo.splitlines() if l.strip()]:
                add_par(doc, linha.strip(), size=12, bold=True, align="justify")

        elif tag == "titulo":
            add_par(doc, conteudo.strip(), size=14, bold=True, align="center")

        elif tag == "corpo":
            for i, par in enumerate(paragrafos(conteudo)):
                if i:
                    branco(doc)
                add_par(doc, par, size=12, align="justify", first_indent=RECUO)

        elif tag == "secao":
            add_par(doc, conteudo.strip(), size=12, bold=True, align="justify")

        elif tag == "citacao":
            pars = paragrafos(conteudo)
            for i, par in enumerate(pars):
                if i:
                    branco(doc)
                # aspas curvas envolvendo o bloco inteiro
                if len(pars) == 1:
                    par = f"“{par}”"
                elif i == 0:
                    par = f"“{par}"
                elif i == len(pars) - 1:
                    par = f"{par}”"
                add_par(doc, par, size=11, bold=True, align="justify",
                        left_indent=RECUO)

        elif tag == "citacao-ref":
            kv, grifos = {}, []
            for linha in conteudo.splitlines():
                if not linha.strip():
                    continue
                k, _, v = linha.partition(":")
                k, v = k.strip().lower(), v.strip()
                if k == "grifo":
                    grifos.append(v)
                elif k:
                    kv[k] = v
            if not kv.get("ref"):
                raise ValueError("@citacao-ref exige atribuição em ref")
            texto, _src = citar.resolve_file(
                WORKSPACE, kv.get("arquivo"), kv.get("sha256"),
                itens=kv.get("itens"), trecho=kv.get("trecho"))
            suffix = f"({kv['ref']})"
            add_citacao(doc, texto, grifos, suffix=suffix)

        elif tag == "pedidos":
            itens = [l.strip() for l in conteudo.splitlines() if l.strip()]
            for i, item in enumerate(itens):
                if i:
                    branco(doc)
                add_par(doc, item, size=11, bold=True, align="justify", left_indent=RECUO)

        elif tag == "fecho":
            # igual ao corpo (12pt, justificado), mas SEM recuo de 1ª linha
            add_par(doc, conteudo.strip(), size=12, align="justify")

        elif tag == "data":
            add_par(doc, conteudo.strip(), size=12, align="justify")

        elif tag == "assinatura":
            linhas = [l.strip() for l in conteudo.splitlines() if l.strip()]
            for i, linha in enumerate(linhas):
                add_par(doc, linha, size=12, bold=(i == 0), align="center")


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser(description="Converte peça marcada em .docx no padrão da casa.")
    ap.add_argument("entrada", help="arquivo .md/.txt com blocos @tag")
    ap.add_argument("--out", required=True, help="arquivo .docx de saída")
    args = ap.parse_args()

    global WORKSPACE
    WORKSPACE = os.path.dirname(os.path.abspath(args.entrada))

    with open(args.entrada, encoding="utf-8") as f:
        texto = f.read()

    blocos = ler_blocos(texto)
    if not blocos:
        sys.exit("Nenhum bloco @tag reconhecido. Confira a marcação da entrada.")

    doc = novo_documento()
    render(doc, blocos)
    doc.save(args.out)
    print(f"OK: {len(blocos)} blocos -> {args.out}")


if __name__ == "__main__":
    main()
