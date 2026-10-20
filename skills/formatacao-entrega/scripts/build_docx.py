#!/usr/bin/env python3
"""build_docx.py — converte uma peça marcada (.md/.txt) em .docx no padrão da casa.

Padrão de formatação: ver ../assets/padrao-formatacao.md (fonte da verdade).
Esta é a implementação determinística daquele padrão.

Uso:
    python build_docx.py <entrada.md> --out <saida.docx>
        [--modelo <nome> | --template <modelo.docx>]
                                       timbrado: página, margens, cabeçalho e rodapé do modelo
        [--workspace <pasta>]          pasta do processo (para @citacao-ref fonte: autos)
        [--transcript <arquivo|pasta>] outra sessão como fonte das ementas
    python build_docx.py --preparar-modelo <documento do escritório.docx> <destino.docx>
        cria um modelo timbrado limpo a partir de um documento real do escritório

Modelos timbrados ficam FORA do repositório, em <raiz de dados>/modelos/<nome>.docx
(raiz = PRATICA_JURIDICA_DATA; sem a variável, a pasta dados-juridicos/modelos/ acima da
entrada). Todo modelo passa por limpeza antes do uso: só ficam página,
margens, cabeçalho, rodapé e estilos; saem corpo, comentários, notas, imagens do corpo,
metadados (customXml) e as propriedades do arquivo.

A ENTRADA usa blocos marcados por uma diretiva `@tag` no início da linha. Cada
bloco vai do seu `@tag` até o próximo. Tags reconhecidas (Cambria em todas):

    @enderecamento   Endereçamento (14 pt negrito, justificado)
    @identificacao   Processo/classe/partes (12 pt negrito, justificado; linhas coladas)
    @titulo          Título da peça (14 pt negrito, CENTRALIZADO)
    @corpo           Parágrafos de texto (12 pt, justificado, recuo 1ª linha 2 cm)
    @secao           Título de seção, ex. "1. DA SÍNTESE..." (12 pt negrito, justificado)
    @citacao         Transcrição (11 pt negrito, recuo esq. 2 cm, entre aspas curvas)
    @citacao-ref     Citação por REFERÊNCIA — cola o texto VERBATIM da fonte (citar.py),
                     com a forma do @citacao. Linhas `chave: valor`:
                       fonte: STJ|STF|TRF1|TRF5|TJPE|CARF|RFB|TCU   (rótulo)
                       processo: REsp 2.136.610       (classe e número; casa o número inteiro)
                       id: 123456                      (opcional; ID do resultado do conector)
                       itens: 1  ou  1-2  ou  II-IV    (opcional; recorte por item da ementa)
                       trecho: de "..." ate "..."      (opcional; fatia por âncoras únicas)
                       grifo: <trecho>                 (opcional, repetível; marca-texto)
                       ref: STJ, REsp ..., Rel. ...    (opcional; atribuição após as aspas)
                     Para citar peças dos AUTOS (workspace do processo):
                       fonte: autos
                       doc: 28   (ou arquivo: doc_028_....md)   (localiza no workspace)
                       + itens/trecho/grifo/ref idênticos
    @pedidos         Itens a) b) c) (11 pt negrito, justificado, recuo esq. 2 cm)
    @fecho           Fecho, ex. "Nestes termos, pede deferimento." (12 pt, justificado)
    @data            Local e data (12 pt, justificado, sem recuo)
    @assinatura      1ª linha = nome (negrito); demais = OAB etc. (12 pt, CENTRALIZADO)

Dentro de @corpo e @pedidos, parágrafos/itens são separados por LINHA EM BRANCO.
O conversor separa os blocos por UM parágrafo vazio (a "respiração" do padrão);
o espaçamento automático antes/depois fica sempre em zero.

Com erro em qualquer @citacao-ref (fonte não achada, recorte ambíguo, ementa com
defeito), nada é gravado: o .docx anterior, se houver, fica intacto.

Requer: pip install python-docx
"""

import argparse
import glob
import importlib.util
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


def _carregar_citar():
    """Importa o citar.py desta pasta pelo caminho (um `citar` alheio no sys.path não entra)."""
    caminho = os.path.join(os.path.dirname(os.path.abspath(__file__)), "citar.py")
    spec = importlib.util.spec_from_file_location("citar_formatacao_entrega", caminho)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


citar = _carregar_citar()   # resolve @citacao-ref (texto verbatim da fonte)

# caminho do transcript (definido no main); None = sessão atual
TRANSCRIPT = None
# pasta do processo (fonte: autos e cache das ementas); definida no main
WORKSPACE = None
# uma linha por @citacao-ref resolvido, para o relatório final
RESOLVIDAS = []

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
def _estilo_normal(doc):
    normal = doc.styles["Normal"]
    normal.font.name = FONTE
    normal.font.size = Pt(11)
    pf = normal.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = ENTRELINHAS
    # idioma pt-BR no estilo padrão
    rpr = normal.element.get_or_add_rPr()
    lang = rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        rpr.append(lang)
    lang.set(qn("w:val"), IDIOMA)


# ---------------------------------------------------------------- modelo timbrado
_RELS_DESCARTE = ("/comments", "/commentsExtended", "/commentsIds", "/commentsExtensible",
                  "/people", "/customXml")
_NOTAS_FIXAS = {"separator", "continuationSeparator", "continuationNotice"}


def _limpar_notas(part):
    """Deixa nas notas de rodapé/fim só os separadores (as notas eram do corpo descartado)."""
    from lxml import etree
    xml = getattr(part, "_element", None)
    raiz = xml if xml is not None else etree.fromstring(part.blob)
    for nota in list(raiz):
        if nota.get(qn("w:type")) not in _NOTAS_FIXAS:
            raiz.remove(nota)
    if xml is None:
        part._blob = etree.tostring(raiz, xml_declaration=True, encoding="UTF-8", standalone=True)
    for rid, rel in list(part.rels.items()):
        if not rel.is_external and rel.reltype.endswith("/image"):
            part.rels.pop(rid)


def _limpar_modelo(doc):
    """Tira do modelo tudo que não é timbre: corpo, comentários, notas, imagens do corpo,
    metadados (customXml) e propriedades do arquivo. Ficam página, margens, cabeçalho,
    rodapé e estilos — nada de conteúdo do documento de onde o modelo saiu."""
    body = doc.element.body
    for filho in list(body):
        if filho.tag != qn("w:sectPr"):
            body.remove(filho)
    part = doc.part
    xml = part.blob   # o XML do documento já sem o corpo
    for rid, rel in list(part.rels.items()):
        if rel.is_external:
            continue
        tipo = rel.reltype
        if tipo.endswith(("/footnotes", "/endnotes")):
            _limpar_notas(rel.target_part)
        elif tipo.endswith(_RELS_DESCARTE) or (tipo.endswith("/image")
                                               and f'"{rid}"'.encode() not in xml):
            part.rels.pop(rid)
    for rid, rel in list(part.package.rels.items()):
        if rel.reltype.endswith("/customXml"):
            part.package.rels.pop(rid)
    cp = doc.core_properties
    for campo in ("title", "subject", "keywords", "comments", "category", "last_modified_by"):
        setattr(cp, campo, "")


def preparar_modelo(origem, destino):
    """Cria um modelo timbrado limpo a partir de um documento real do escritório."""
    doc = Document(origem)
    _limpar_modelo(doc)
    os.makedirs(os.path.dirname(os.path.abspath(destino)) or ".", exist_ok=True)
    doc.save(destino)
    s = doc.sections[0]
    print(f"Modelo salvo em {destino}: página {s.page_width.cm:.1f} x {s.page_height.cm:.1f} cm; "
          f"margens {s.top_margin.cm:.2f} / {s.bottom_margin.cm:.2f} / {s.left_margin.cm:.2f} / "
          f"{s.right_margin.cm:.2f} cm (sup. / inf. / esq. / dir.)")


def _modelos_em(pasta):
    try:
        return sorted(f[:-5] for f in os.listdir(pasta) if f.lower().endswith(".docx"))
    except OSError:
        return []


def achar_modelo(nome, entrada):
    """--modelo NOME → <raiz>/modelos/NOME.docx. Raiz: PRATICA_JURIDICA_DATA; sem ela, sobe a
    partir da pasta da entrada procurando dados-juridicos/modelos/."""
    arquivo = nome if nome.lower().endswith(".docx") else nome + ".docx"
    pastas = []
    raiz = os.environ.get("PRATICA_JURIDICA_DATA")
    if raiz:
        pastas.append(os.path.join(raiz, "modelos"))
    atual = os.path.dirname(os.path.abspath(entrada))
    while True:
        if os.path.basename(atual).lower() == "dados-juridicos":
            pastas.append(os.path.join(atual, "modelos"))
        pastas.append(os.path.join(atual, "dados-juridicos", "modelos"))
        acima = os.path.dirname(atual)
        if acima == atual:
            break
        atual = acima
    for pasta in pastas:
        if os.path.isfile(os.path.join(pasta, arquivo)):
            return os.path.join(pasta, arquivo)
    existentes = next((m for m in (_modelos_em(p) for p in pastas) if m), None)
    dica = (f" Modelos disponíveis: {', '.join(existentes)}." if existentes
            else " Defina PRATICA_JURIDICA_DATA (os modelos ficam em <raiz>/modelos/) ou passe "
                 "--template <caminho>.")
    sys.exit(f"Modelo '{nome}' não encontrado.{dica}")


def novo_documento(template=None):
    """Documento em branco no padrão da casa. Com `template` (o .docx do timbrado), herda
    dele página, margens, cabeçalho e rodapé; o resto do modelo é descartado."""
    if template:
        doc = Document(template)
        _limpar_modelo(doc)
        _estilo_normal(doc)
        return doc

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
    _estilo_normal(doc)
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
    """Citação (11 pt negrito, recuo esq. 2 cm, aspas curvas). O(s) trecho(s) em
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
        if sp is None:
            raise LookupError(f"grifo não encontrado no texto citado: {citar.collapse(g)!r}")
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
        a = max(a, pos)          # grifos sobrepostos: realça a união
        if b <= a:
            continue
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


def _citacao_ref(doc, conteudo, n):
    """Resolve um bloco @citacao-ref (o n-ésimo) e insere a citação."""
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
    try:
        if kv.get("fonte", "").lower() == "autos":
            texto, src = citar.resolve_autos(
                WORKSPACE, doc=kv.get("doc"), arquivo=kv.get("arquivo"),
                itens=kv.get("itens"), trecho=kv.get("trecho"))
            origem = f"autos: {os.path.basename(src)}"
        else:
            if not (kv.get("processo") or kv.get("id")):
                raise LookupError("falta `processo:` (ou `id:`) no @citacao-ref")
            texto, prov = citar.resolve(
                kv.get("processo"), itens=kv.get("itens"), trecho=kv.get("trecho"),
                transcript=TRANSCRIPT, workspace=WORKSPACE, id_=kv.get("id"), detalhes=True)
            origem = f"{prov.get('via')}: {prov.get('cabecalho')}"
        suffix = f"({kv['ref']})" if kv.get("ref") else ""
        add_citacao(doc, texto, grifos, suffix=suffix)
    except (LookupError, ValueError) as e:
        rotulo = kv.get("processo") or kv.get("id") or kv.get("doc") or kv.get("arquivo") or "?"
        raise SystemExit(f"ERRO no {n}º @citacao-ref ({rotulo}): {e}\nNada foi gravado.")
    RESOLVIDAS.append(f"  [{n}] {kv.get('processo') or kv.get('doc') or kv.get('arquivo') or kv.get('id')}"
                      f" → {origem}")


# ---------------------------------------------------------------- render por tag
def render(doc, blocos):
    primeiro = True
    n_ref = 0
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
            n_ref += 1
            _citacao_ref(doc, conteudo, n_ref)

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
def _workspace_padrao(entrada):
    """Pasta do .md; se ela não tiver documentos extraídos (doc_NNN_*.md), sobe até dois
    níveis (ex.: <workspace>/redacao/peca.md) procurando a pasta do processo."""
    pasta = os.path.dirname(os.path.abspath(entrada))
    cand = pasta
    for _ in range(3):
        if glob.glob(os.path.join(cand, "doc_[0-9][0-9][0-9]_*.md")):
            return cand
        cand = os.path.dirname(cand)
    return pasta


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    if len(sys.argv) > 1 and sys.argv[1] == "--preparar-modelo":
        if len(sys.argv) != 4:
            sys.exit("Uso: build_docx.py --preparar-modelo <documento do escritório.docx> <destino.docx>")
        preparar_modelo(sys.argv[2], sys.argv[3])
        return

    ap = argparse.ArgumentParser(description="Converte peça marcada em .docx no padrão da casa.")
    ap.add_argument("entrada", help="arquivo .md/.txt com blocos @tag")
    ap.add_argument("--out", required=True, help="arquivo .docx de saída")
    timbre = ap.add_mutually_exclusive_group()
    timbre.add_argument("--modelo", help="nome do modelo timbrado em <raiz>/modelos/ (ex.: o da casa)")
    timbre.add_argument("--template", help="caminho de um modelo .docx do timbrado")
    ap.add_argument("--workspace", help="pasta do processo, para @citacao-ref fonte: autos "
                                        "(padrão: a pasta do .md ou a acima dela com doc_NNN_*.md)")
    ap.add_argument("--transcript", help="transcript (.jsonl) ou pasta de outra sessão para "
                                         "@citacao-ref (padrão: a sessão atual)")
    args = ap.parse_args()

    global TRANSCRIPT, WORKSPACE
    TRANSCRIPT = args.transcript
    WORKSPACE = os.path.abspath(args.workspace) if args.workspace else _workspace_padrao(args.entrada)
    if args.modelo:
        args.template = achar_modelo(args.modelo, args.entrada)
    if args.template and not os.path.isfile(args.template):
        sys.exit(f"Modelo não encontrado: {args.template}")

    with open(args.entrada, encoding="utf-8") as f:
        texto = f.read()

    blocos = ler_blocos(texto)
    if not blocos:
        sys.exit("Nenhum bloco @tag reconhecido. Confira a marcação da entrada.")

    doc = novo_documento(args.template)
    render(doc, blocos)
    doc.save(args.out)
    print(f"OK: {len(blocos)} blocos -> {args.out}"
          + (f" (timbrado: {os.path.basename(args.template)})" if args.template else ""))
    if RESOLVIDAS:
        print(f"@citacao-ref resolvidos ({len(RESOLVIDAS)}), workspace {WORKSPACE}:")
        print("\n".join(RESOLVIDAS))


if __name__ == "__main__":
    main()
