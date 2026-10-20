#!/usr/bin/env python3
"""CLI para leitura seletiva de processos judiciais grandes (PJe) em PDF.

Extrai sob demanda, guiado pelo índice de documentos (bookmarks) do PDF. Nunca
carrega o PDF inteiro no contexto: lê o mapa, localiza e extrai só o necessário.

Comandos (detalhes em `python processo.py <comando> -h`):
  index     <pdf> [--json]                      mapa dos documentos
  peek      <pdf> --docs 10,23 [--chars N]      início de cada documento, sem o timbre
  extract   <pdf> (--docs 10,23 | --pages 5-9) [--out DIR] [--confirmar]
                                                markdown limpo, com front matter
  grep      <pdf> <termo> [--docs ...] [--regex] [--exato] [--max N]
                                                busca textual: página, documento e trecho
  find      <pdf> (--id N | --pattern TERMO)    evento/id do PJe -> documento
  refs      <pdf> --docs N                      referências "id N" do documento -> documentos
  sem-texto <pdf> [--doc N] [--json]            páginas sem texto extraível (imagem)
  render    <pdf> --pages a-b [--out DIR]       PNG das páginas, para ler a imagem
  workspace <cnj>                               pasta gravável do processo (imprime o caminho)

Página sem texto = menos de 80 caracteres úteis (letras/dígitos, já sem o rodapé e o
cabeçalho do PJe) e imagens cobrindo ao menos 10% da página. Não há OCR: a página é
marcada, e `render` gera a imagem para leitura direta. Texto de OCR que já venha no PDF
(camada invisível sobre a imagem escaneada) é marcado como `ocr`.

Dependência: pypdfium2 (pip install pypdfium2). Pillow é opcional: sem ele, `render`
grava PNG em tons de cinza.
"""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
import re
import struct
import sys
import tempfile
import unicodedata
import zlib
from pathlib import Path

# ----------------------------------------------------------------------------
# Parâmetros
# ----------------------------------------------------------------------------
MIN_UTEIS = 80            # abaixo disso (e com imagem), a página é "sem texto"
MIN_IMAGEM = 0.10         # imagens cobrindo 10% da página ou mais (logotipo e selo não contam)
CRITERIO_SEM_TEXTO = (f"menos de {MIN_UTEIS} caracteres úteis (letras e dígitos, sem o rodapé e o "
                      f"cabeçalho do PJe) e imagens cobrindo ao menos {MIN_IMAGEM:.0%} da página")
LIMIAR_RAPIDO = 1500      # com mais caracteres brutos que isso, a página tem texto
TOKENS_POR_PAGINA = 700   # estimativa para o aviso de tamanho antes de extrair
LIMITE_TOKENS = 150_000   # acima disso, extract pede --confirmar
FAIXA = 50                # páginas por faixa, no modo sem índice
MAX_RENDER = 30           # páginas por chamada de render (sem --confirmar)
MAX_PX = 2000             # lado maior da imagem gerada por render

# ----------------------------------------------------------------------------
# Ruído do PJe: rodapé de assinatura e cabeçalho "Documento id N - Tipo (Nome)"
# ----------------------------------------------------------------------------
BOILERPLATE_RES = [
    re.compile(r"^\s*Num\.\s*\d+\s*-\s*P[áa]g\.\s*\d+\b", re.IGNORECASE),
    re.compile(r"^\s*Assinado eletronicamente por:", re.IGNORECASE),
    re.compile(r"^\s*https?://pje", re.IGNORECASE),
    re.compile(r"^\s*N[úu]mero do documento:", re.IGNORECASE),
    re.compile(r"^\s*Este documento foi gerado pelo usu[áa]rio", re.IGNORECASE),
]
CAB_PAGINA_RE = re.compile(r"^\s*Documento id (\d+)\s*-\s*", re.IGNORECASE)
# Início de um tipo do PJe, quando o cabeçalho vem colado ao texto (texto normalizado).
TIPO_COMPOSTO_RE = re.compile(r"(peticao (intercorrente|inicial)|embargos de declaracao|"
                              r"intimacao de pauta|certidao de julgamento colegiado|nota oral|"
                              r"outros documentos|[^\W\d_]+)")
RODAPE_RE = re.compile(r"Num\.\s*(\d{6,})\s*-\s*P[áa]g\.\s*(\d+)", re.IGNORECASE)

# Título do bookmark. TRF-5: "Petição (Outras) | NUM: 241577420 | 27/05/2026 11:43".
# TRF-1: "Manifestação | <nome do arquivo> | NUM: 64540541 | 09/07/2020 15:46".
TITULO_RE = re.compile(r"^(?P<prefixo>.*?)\s*\|\s*NUM:\s*(?P<num>\d+)\s*\|\s*(?P<data>.+?)\s*$")

# Citação de outro documento dentro de uma peça: "id 240895548", "(id. 240714892)",
# "ID 33878565 - Pág. 72" (página dentro do documento citado).
CITACAO_ID_RE = re.compile(r"\bid\.?\s*(\d{6,})\b(?:\s*[-–,]\s*p[áa]gs?\.?\s*(\d+))?", re.IGNORECASE)

CNJ_RE = re.compile(r"\b(\d{7})-?(\d{2})\.?(\d{4})\.?(\d)\.?(\d{2})\.?(\d{4})\b")

# Documento "Índice" do PJe: linhas "<id> <dd/mm/aaaa> [hh:mm] <documento> <tipo> [<polo>]".
INDICE_LINHA_RE = re.compile(r"^\s*(\d{6,})\s+(\d{2}/\d{2}/\d{4})(?:\s+\d{1,2}:\d{2}(?::\d{2})?)?\s*(.*)$")
INDICE_CAB_RE = re.compile(r"^\s*(Id\.?(\s|$)|Data da|Assinatura\s*$|Documento\s+Tipo)", re.IGNORECASE)
POLO_RE = re.compile(r"\s+(?:Interno|Externo|Polo ativo|Polo passivo|Ativo|Passivo|"
                     r"Terceiros?(?: interessados?)?)\s*$", re.IGNORECASE)

# Classificação "peça?" — sobre o texto normalizado (minúsculo, sem acento).
PECA_RE = re.compile(
    r"\b(peticao inicial|inicial|emenda|contestacao|reconvencao|replica|treplica|"
    r"impugnacao|sentenca|acordao|ementa|voto|relatorio|decisao|despacho|apelacao|"
    r"agravo|recurso|razoes|contrarrazoes|contraminuta|embargos|manifestacao|parecer|"
    r"memoriais|memorial|alegacoes finais|excecao|informacoes|cumprimento de sentenca)\b")
NAO_PECA_RE = re.compile(
    r"\b(procuracao|substabelecimento|certidao|intimacao|citacao|mandado|oficio|"
    r"comprovante|guia|custas|documento de identificacao|documento de comprovacao|"
    r"outros documentos|anexo|cabecalho|indice|ato ordinatorio|aviso de recebimento|"
    r"alvara|termo|juntada|ciencia|nota oral|extrato|planilha|calculo|laudo|contrato|"
    r"nota fiscal|diligencia|carta|expediente|pauta)\b")
JUNTADA_RE = re.compile(r"\b(juntada|ciencia|ciente|subs|substabelec\w*|procuracao|guia|"
                        r"custas|comprovante|recolhimento|habilitacao)\b")

# Timbre do tribunal — repetido em toda peça, inútil para o ranking do peek.
LETTERHEAD_RES = [
    re.compile(r"^\s*tribunal de justi", re.IGNORECASE),
    re.compile(r"^\s*tribunal regional", re.IGNORECASE),
    re.compile(r"^\s*justi[çc]a federal", re.IGNORECASE),
    re.compile(r"^\s*poder judici", re.IGNORECASE),
    re.compile(r"^\s*processo judicial eletr", re.IGNORECASE),
    re.compile(r"^\s*(gab\.|(se[çc][ãa]o|vara|gabinete|comarca|ju[íi]zo)\b)", re.IGNORECASE),
    re.compile(r"^\s*(avenida|rua|av\.|pra[çc]a|estrada|rodovia|alameda|setor)\s", re.IGNORECASE),
    re.compile(r"^\s*processo\s*(n|:|refer)", re.IGNORECASE),
    re.compile(r"^\s*(autor|r[ée]u|reu|recuperand|exequente|executad|agravante|"
               r"agravad|embargante|embargad|requerente|requerid|apelante|apelad|"
               r"impetrante|impetrad|advogad)", re.IGNORECASE),
    re.compile(r"^\s*F:\(?\d", re.IGNORECASE),       # telefone do fórum
    re.compile(r"^\s*CEP[:\s]", re.IGNORECASE),
    re.compile(r"^\s*(tel\.?|fone|fax)[:\s]", re.IGNORECASE),
    re.compile(r"^\s*www\.", re.IGNORECASE),
    re.compile(r"^\s*\d{1,3}\s*$"),                    # número de página solto
    re.compile(r"^\s*[A-ZÁÉÍÓÚÂÊÔÃÕÇ ]+\(\d+\)\s*$"),   # classe com código: "APELAÇÃO CÍVEL (198)"
]
# Linha de "rol de partes" (caixa alta longa, com vírgulas) — continuação do timbre.
ROL_PARTES_RE = re.compile(r"^[A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9 ,.\-/()]{30,}$")

_ACENTOS = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑºª",
                         "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCNoa")


# ----------------------------------------------------------------------------
# Utilidades
# ----------------------------------------------------------------------------
def _norm(s: str) -> str:
    """Minúsculo, sem acento e com espaços simples (para comparar e classificar)."""
    s = (s or "").translate(_ACENTOS)
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", s).lower().strip()


def _norm_mesmo_tamanho(s: str) -> str:
    """Tira acento e põe em minúsculo preservando o comprimento (posições valem no original)."""
    out = s.translate(_ACENTOS).lower()
    return out if len(out) == len(s) else s.lower()


def _collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _md(s) -> str:
    """Valor seguro para célula de tabela Markdown."""
    return _collapse(str(s or "")).replace("|", "\\|")


def _milhar(n: int) -> str:
    return f"{n:,}".replace(",", ".")


def _encurtar(s: str, n: int) -> str:
    s = _collapse(s)
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _faixas_str(paginas) -> str:
    """[3,4,5,9] -> '3-5, 9'."""
    pags = sorted(set(paginas))
    if not pags:
        return "nenhuma"
    partes, ini, ant = [], pags[0], pags[0]
    for p in pags[1:]:
        if p == ant + 1:
            ant = p
            continue
        partes.append(f"{ini}-{ant}" if ant > ini else str(ini))
        ini = ant = p
    partes.append(f"{ini}-{ant}" if ant > ini else str(ini))
    return ", ".join(partes)


def _parse_paginas(spec: str, total: int) -> list[tuple[int, int]]:
    """'5-9,12' -> [(5, 9), (12, 12)], validado contra o total de páginas (1-indexado)."""
    faixas = []
    for parte in re.split(r"[,\s]+", spec.strip()):
        if not parte:
            continue
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", parte)
        if not m:
            sys.exit(f"ERRO: faixa de páginas inválida: {parte!r} (use 5-9,12)")
        a = int(m.group(1))
        b = int(m.group(2) or a)
        if a > b:
            a, b = b, a
        if a < 1 or b > total:
            sys.exit(f"ERRO: páginas {a}-{b} fora do PDF (1-{total})")
        faixas.append((a, b))
    if not faixas:
        sys.exit("ERRO: nenhuma página informada")
    return faixas


def _parse_seqs(spec: str) -> list[int]:
    try:
        return [int(x) for x in re.split(r"[,\s]+", spec.strip()) if x != ""]
    except ValueError:
        sys.exit(f"ERRO: lista de documentos inválida: {spec!r} (use 10,23)")


def _abrir(pdf_path: str):
    try:
        import pypdfium2 as pdfium  # import tardio: workspace não precisa dele
    except ImportError:
        sys.exit("ERRO: falta a dependência pypdfium2 — rode: pip install pypdfium2")
    p = Path(pdf_path)
    if not p.exists():
        sys.exit(f"ERRO: arquivo não encontrado: {p}")
    try:
        return pdfium.PdfDocument(str(p))
    except Exception as e:  # PDF corrompido, protegido por senha ou que não é PDF
        sys.exit(f"ERRO: não consegui abrir o PDF {p.name}: {e}")


def _raw():
    import pypdfium2.raw as pdfium_c
    return pdfium_c


# ----------------------------------------------------------------------------
# Cache do perfil das páginas (só números: nenhum texto dos autos vai para o cache)
# ----------------------------------------------------------------------------
_CACHE_VERSAO = 2   # mude quando a limpeza de página mudar (invalida o cache antigo)


def _cache_path(pdf_path: str) -> Path | None:
    try:
        st = os.stat(pdf_path)
        chave = (f"{os.path.abspath(pdf_path)}|{st.st_size}|{st.st_mtime_ns}|"
                 f"{MIN_UTEIS}|{MIN_IMAGEM}|{LIMIAR_RAPIDO}|{_CACHE_VERSAO}")
        h = hashlib.sha1(chave.encode("utf-8")).hexdigest()[:20]
        return Path(tempfile.gettempdir()) / "pratica-juridica" / f"perfil-{h}.json"
    except OSError:
        return None


def _cache_ler(pdf_path: str) -> dict:
    p = _cache_path(pdf_path)
    try:
        dados = json.loads(p.read_text(encoding="utf-8")) if p and p.exists() else {}
        return dados if dados.get("v") == 1 else {}
    except Exception:
        return {}


def _cache_gravar(pdf_path: str, dados: dict) -> None:
    p = _cache_path(pdf_path)
    if not p:
        return
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        tmp = p.with_suffix(".tmp")
        tmp.write_text(json.dumps({**dados, "v": 1}), encoding="utf-8")
        os.replace(tmp, p)
    except Exception:
        pass  # cache é otimização; falhar aqui não pode quebrar o comando


# ----------------------------------------------------------------------------
# Texto das páginas
# ----------------------------------------------------------------------------
def _partir_cabecalho(resto: str) -> tuple[str, str, int]:
    """'Tipo (Nome) texto…' → (tipo, nome, fim). O nome pode ter parênteses internos;
    o que vem depois do parêntese que o fecha é texto da página (OCR colado)."""
    abre = resto.find("(")
    if abre > 0:
        nivel = 0
        for k in range(abre, len(resto)):
            nivel += {"(": 1, ")": -1}.get(resto[k], 0)
            if nivel == 0:
                return resto[:abre].strip(), resto[abre + 1:k].strip(), k + 1
    if len(resto.strip()) > 40:   # cabeçalho colado à primeira linha da página
        m = TIPO_COMPOSTO_RE.match(_norm_mesmo_tamanho(resto.lstrip()))
        if m:
            desloc = len(resto) - len(resto.lstrip())
            return resto[desloc: desloc + m.end()].strip(), "", desloc + m.end()
    return resto.strip(), "", len(resto)


def _tirar_cabecalho(linha: str, m, docs_por_num: dict | None) -> str:
    """Remove o cabeçalho 'Documento id N - Tipo (Nome)' que o PJe põe no topo de cada
    página. Em páginas com OCR o cabeçalho vem colado ao texto da imagem: corta só ele."""
    d = (docs_por_num or {}).get(m.group(1))
    if d:
        candidatos = []
        if d.get("nome"):
            candidatos.append(f"Documento id {m.group(1)} - {d['tipo']} ({d['nome']})")
        candidatos.append(f"Documento id {m.group(1)} - {d['tipo']}")
        for cand in candidatos:
            pat = r"\s*".join(re.escape(t) for t in cand.split())
            mm = re.match(r"\s*" + pat, linha, re.IGNORECASE)
            if mm:
                return linha[mm.end():]
    resto = linha[m.end():]
    return resto[_partir_cabecalho(resto)[2]:]


def _limpar_pagina(texto: str, docs_por_num: dict | None = None) -> list[str]:
    """Remove o rodapé e o cabeçalho do PJe; devolve as linhas úteis."""
    out = []
    linhas = texto.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    for k, linha in enumerate(linhas):
        if any(r.search(linha) for r in BOILERPLATE_RES):
            continue
        if k < 3:
            m = CAB_PAGINA_RE.match(linha)
            if m:
                linha = _tirar_cabecalho(linha, m, docs_por_num)
                if not linha.strip():
                    continue
        out.append(linha.rstrip())
    return out


def _uteis(linhas) -> int:
    return sum(len(re.findall(r"\w", ln)) for ln in linhas)


def _cobertura_imagem(page, parar_em: float | None = None) -> float:
    """Fração da página coberta por imagens (soma das áreas; 0 = nenhuma). Desce nos
    Form XObjects (o PJe embrulha cada página importada num deles). Com `parar_em`,
    para assim que a soma o atinge."""
    c = _raw()
    w, h = page.get_size()
    total = float(w * h) or 1.0
    l, b, r, t = ctypes.c_float(), ctypes.c_float(), ctypes.c_float(), ctypes.c_float()
    soma = 0.0

    def walk(contar, pegar, pai, nivel) -> bool:
        nonlocal soma
        for k in range(contar(pai)):
            o = pegar(pai, k)
            tipo = c.FPDFPageObj_GetType(o)
            if tipo == c.FPDF_PAGEOBJ_IMAGE:
                if c.FPDFPageObj_GetBounds(o, l, b, r, t):
                    soma += max(0.0, r.value - l.value) * max(0.0, t.value - b.value) / total
                if parar_em is not None and soma >= parar_em:
                    return True
            elif tipo == c.FPDF_PAGEOBJ_FORM and nivel < 4:
                if walk(c.FPDFFormObj_CountObjects, c.FPDFFormObj_GetObject, o, nivel + 1):
                    return True
        return False

    walk(c.FPDFPage_CountObjects, c.FPDFPage_GetObject, page.raw, 0)
    return soma


def _sem_texto(page, linhas) -> bool:
    """Critério de página sem texto: poucos caracteres úteis e imagem relevante."""
    return _uteis(linhas) < MIN_UTEIS and _cobertura_imagem(page, MIN_IMAGEM) >= MIN_IMAGEM


def _texto_invisivel(textpage) -> bool:
    """True se a maior parte do texto é invisível (modo 3) — a camada de OCR que a
    digitalização põe sobre a imagem escaneada. Amostra alguns caracteres."""
    c = _raw()
    n = textpage.count_chars()
    if n <= 0:
        return False
    inv = vis = 0
    for frac in (0.05, 0.15, 0.25, 0.35, 0.45, 0.55, 0.65, 0.75, 0.85):
        o = c.FPDFText_GetTextObject(textpage.raw, int(n * frac))
        if not o:
            continue
        if c.FPDFTextObj_GetTextRenderMode(o) == c.FPDF_TEXTRENDERMODE_INVISIBLE:
            inv += 1
        else:
            vis += 1
    return inv >= 2 and inv > vis


def _ler_pagina(pdf, i: int, docs_por_num=None, classificar=True):
    """(linhas limpas, fonte) da página i (0-indexada). fonte: texto-nativo | ocr | sem-texto."""
    page = pdf[i]
    tp = page.get_textpage()
    try:
        linhas = _limpar_pagina(tp.get_text_range(), docs_por_num)
        if not classificar:
            return linhas, None
        if _sem_texto(page, linhas):
            fonte = "sem-texto"
        elif _uteis(linhas) >= MIN_UTEIS and _texto_invisivel(tp):
            fonte = "ocr"
        else:
            fonte = "texto-nativo"
        return linhas, fonte
    finally:
        tp.close()
        page.close()


def paginas_sem_texto(pdf, pdf_path: str, docs_por_num=None) -> list[int]:
    """Páginas (1-indexadas) sem texto extraível. Rápido: só abre o texto das páginas
    com poucos caracteres. Resultado cacheado por arquivo (tamanho + data)."""
    cache = _cache_ler(pdf_path)
    if isinstance(cache.get("sem_texto"), list) and cache.get("n") == len(pdf):
        return cache["sem_texto"]
    res = []
    for i in range(len(pdf)):
        page = pdf[i]
        tp = page.get_textpage()
        try:
            if tp.count_chars() < LIMIAR_RAPIDO and \
                    _sem_texto(page, _limpar_pagina(tp.get_text_range(), docs_por_num)):
                res.append(i + 1)
        finally:
            tp.close()
            page.close()
    cache.update({"n": len(pdf), "sem_texto": res})
    _cache_gravar(pdf_path, cache)
    return res


def _rodapes(pdf, pdf_path: str) -> list:
    """Por página: [num, pag] do rodapé 'Num. N - Pág. M' do PJe, ou None. Cacheado."""
    cache = _cache_ler(pdf_path)
    if isinstance(cache.get("rodape"), list) and cache.get("n") == len(pdf):
        return cache["rodape"]
    print(f"(lendo o rodapé das {len(pdf)} páginas para montar o índice…)", file=sys.stderr)
    res = []
    for i in range(len(pdf)):
        page = pdf[i]
        tp = page.get_textpage()
        try:
            achados = RODAPE_RE.findall(tp.get_text_range())
            res.append([achados[-1][0], int(achados[-1][1])] if achados else None)
        finally:
            tp.close()
            page.close()
    cache.update({"n": len(pdf), "rodape": res})
    _cache_gravar(pdf_path, cache)
    return res


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


def texto_paginas(pdf, pg_ini: int, pg_fim: int, docs_por_num=None, max_chars=None,
                  pdf_nome: str = "<pdf>") -> tuple[str, dict]:
    """Texto limpo das páginas pg_ini..pg_fim (1-indexadas), com um marcador por página.
    Devolve (texto, {"sem_texto": [...], "ocr": [...]})."""
    blocos, info, total = [], {"sem_texto": [], "ocr": []}, 0
    for pg in range(pg_ini, pg_fim + 1):
        linhas, fonte = _ler_pagina(pdf, pg - 1, docs_por_num)
        if fonte == "sem-texto":
            info["sem_texto"].append(pg)
            blocos.append(f"<!-- pág. {pg} · sem texto extraível (imagem): "
                          f"processo.py render {pdf_nome} --pages {pg} -->")
        elif fonte == "ocr":
            info["ocr"].append(pg)
            blocos.append(f"<!-- pág. {pg} · texto de OCR sobre imagem: confira na imagem "
                          f"antes de citar literalmente -->")
        else:
            blocos.append(f"<!-- pág. {pg} -->")
        paras = _dewrap(linhas)
        blocos.extend(paras)
        total += sum(len(p) for p in paras)
        if max_chars and total >= max_chars:
            break
    txt = "\n\n".join(blocos)
    return (txt[:max_chars] if max_chars else txt), info


def texto_doc(pdf, doc: dict, max_chars: int | None = None, docs_por_num=None) -> str:
    """Texto limpo de um documento (faixa de páginas do índice)."""
    return texto_paginas(pdf, doc["pg_ini"], doc["pg_fim"], docs_por_num, max_chars)[0]


# ----------------------------------------------------------------------------
# Índice
# ----------------------------------------------------------------------------
def classificar_peca(tipo: str, nome: str = "") -> bool | None:
    """True = peça (petição das partes, decisão, parecer); False = anexo/expediente;
    None = indefinido (petição genérica, volume digitalizado): olhe com peek/grep."""
    t, n = _norm(tipo), _norm(nome)
    if re.search(r"\bvolume\b", t):
        return None
    if NAO_PECA_RE.search(t):
        return False
    if PECA_RE.search(t):
        return not (n and JUNTADA_RE.search(n))
    if n:
        if JUNTADA_RE.search(n) or NAO_PECA_RE.search(n):
            return False
        if PECA_RE.search(n):
            return True
    if re.search(r"\bpeticao\b", t):
        return None
    return False


def _bookmarks(pdf) -> list[tuple[int, str]]:
    """(página 0-indexada, título) do nível de bookmark que tem mais entradas."""
    por_nivel: dict[int, list] = {}
    for it in pdf.get_toc():
        dest = it.get_dest()
        pg = dest.get_index() if dest else None
        if pg is None:
            continue
        por_nivel.setdefault(getattr(it, "level", 0), []).append((pg, it.get_title() or ""))
    if not por_nivel:
        return []
    nivel = max(sorted(por_nivel), key=lambda k: len(por_nivel[k]))
    return sorted(por_nivel[nivel], key=lambda x: x[0])


def _nomes_do_indice(pdf, doc_indice: dict, tipos: dict) -> dict:
    """Lê o documento 'Índice' do PJe (tabela Id · Data · Documento · Tipo [· Polo]) e
    devolve {id: nome}. O TRF-5 só traz o nome aqui; o bookmark tem só o tipo."""
    linhas = []
    for pg in range(doc_indice["pg_ini"], doc_indice["pg_fim"] + 1):
        linhas.extend(_ler_pagina(pdf, pg - 1, classificar=False)[0])
    linhas_id: list[list] = []
    for ln in linhas:
        m = INDICE_LINHA_RE.match(ln)
        if m:
            linhas_id.append([m.group(1), [m.group(3)]])
        elif linhas_id and ln.strip() and not INDICE_CAB_RE.match(ln):
            linhas_id[-1][1].append(ln.strip())
    nomes = {}
    for num, partes in linhas_id:
        resto = POLO_RE.sub("", _collapse(" ".join(partes)))
        tipo = _collapse(tipos.get(num, ""))
        if tipo and _norm_mesmo_tamanho(resto).endswith(_norm_mesmo_tamanho(tipo)):
            resto = resto[: len(resto) - len(tipo)].strip()
        if resto:
            nomes[num] = resto
    return nomes


def _primeira_linha(pdf, pg: int) -> str:
    linhas, _ = _ler_pagina(pdf, pg - 1, classificar=False)
    return _encurtar(_pular_letterhead("\n".join(linhas)).split("\n")[0], 80)


def _cabecalho_da_pagina(pdf, pg: int) -> tuple[str, str] | None:
    """(tipo, nome) do cabeçalho 'Documento id N - Tipo (Nome)' da página, se houver."""
    page = pdf[pg - 1]
    tp = page.get_textpage()
    try:
        for linha in tp.get_text_range().replace("\r", "\n").split("\n")[:3]:
            m = CAB_PAGINA_RE.match(linha)
            if m:
                tipo, nome, _ = _partir_cabecalho(linha[m.end():])
                return _encurtar(tipo, 60), nome
    finally:
        tp.close()
        page.close()
    return None


def _indice_sem_bookmarks(pdf, pdf_path: str) -> tuple[list[dict], str]:
    """Sem bookmarks: remonta os documentos pelo rodapé 'Num. N - Pág. M' do PJe; sem
    rodapé, divide o PDF em faixas fixas de FAIXA páginas."""
    n = len(pdf)
    rod = _rodapes(pdf, pdf_path)
    blocos: list[tuple[int, int, str | None]] = []   # (ini, fim, num) 1-indexados
    if sum(1 for r in rod if r) >= max(1, n // 2):
        modo, i = "rodape", 0
        while i < n:
            if rod[i] is None:
                j = i
                while j < n and rod[j] is None and j - i < FAIXA:
                    j += 1
                blocos.append((i + 1, j, None))
                i = j
                continue
            num, j = rod[i][0], i + 1
            while j < n and rod[j] and rod[j][0] == num and rod[j][1] != 1:
                j += 1
            blocos.append((i + 1, j, num))
            i = j
    else:
        modo = "faixas"
        blocos = [(a, min(a + FAIXA - 1, n), None) for a in range(1, n + 1, FAIXA)]
    docs = []
    for seq, (ini, fim, num) in enumerate(blocos):
        cab = _cabecalho_da_pagina(pdf, ini) if num else None
        if cab:
            tipo, nome = cab
            peca = classificar_peca(tipo, nome)
        else:
            tipo = "(sem bookmark)" if num else "Faixa de páginas"
            nome, peca = _primeira_linha(pdf, ini), None
        docs.append({
            "seq": seq, "tipo": tipo, "nome": "" if _norm(nome) == _norm(tipo) else nome,
            "num": num, "data": None, "pg_ini": ini, "pg_fim": fim, "npags": fim - ini + 1,
            "is_peca": peca, "slug": f"pags-{ini}-{fim}",
        })
    return docs, modo


def construir_indice(pdf, pdf_path: str | None = None) -> tuple[list[dict], dict]:
    """Lista de documentos (faixas de página) a partir dos bookmarks do PJe.
    Devolve (docs, info); info["modo"] = bookmarks | rodape | faixas."""
    n = len(pdf)
    brutos = _bookmarks(pdf)
    info = {"modo": "bookmarks", "nomes_do_indice": False}
    if not brutos:
        docs, info["modo"] = _indice_sem_bookmarks(pdf, pdf_path or "")
        return docs, info
    docs = []
    for i, (pg, titulo) in enumerate(brutos):
        fim = max(pg, (brutos[i + 1][0] - 1) if i + 1 < len(brutos) else n - 1)
        m = TITULO_RE.match(titulo)
        if m:
            prefixo, num, data = m.group("prefixo").strip(), m.group("num"), m.group("data").strip()
        else:
            prefixo, num, data = titulo.strip(), None, None
        tipo, sep, nome = prefixo.partition("|")
        tipo, nome = tipo.strip(), nome.strip()
        if _norm(nome) == _norm(tipo):
            nome = ""
        docs.append({
            "seq": i, "tipo": tipo, "nome": nome, "num": num, "data": data,
            "pg_ini": pg + 1, "pg_fim": fim + 1, "npags": fim - pg + 1,
            "slug": prefixo,           # nome de arquivo estável entre versões
            "_sem_nome": bool(num and not sep),   # bookmark só com o tipo (TRF-5)
        })
    if any(d["_sem_nome"] for d in docs):
        doc_indice = next((d for d in docs if _norm(d["tipo"]) == "indice"), None)
        if doc_indice:
            tipos = {d["num"]: d["tipo"] for d in docs if d["num"]}
            nomes = _nomes_do_indice(pdf, doc_indice, tipos)
            for d in docs:
                nome = nomes.get(d["num"]) if d["_sem_nome"] else None
                if nome and _norm(nome) != _norm(d["tipo"]):
                    d["nome"] = nome
                    info["nomes_do_indice"] = True
    for d in docs:
        d["is_peca"] = classificar_peca(d["tipo"], d["nome"])
    return docs, info


def _publico(d: dict) -> dict:
    """Campos do documento para a saída JSON (sem os auxiliares internos)."""
    return {k: v for k, v in d.items() if k != "slug" and not k.startswith("_")}


def _docs_por_num(docs) -> dict:
    return {d["num"]: d for d in docs if d.get("num")}


def _doc_da_pagina(docs) -> dict:
    mapa = {}
    for d in docs:
        for p in range(d["pg_ini"], d["pg_fim"] + 1):
            mapa.setdefault(p, d)
    return mapa


def _avisar_modo(info: dict, pdf_nome: str) -> None:
    if info["modo"] == "bookmarks":
        return
    if info["modo"] == "rodape":
        msg = ("PDF SEM BOOKMARKS (índice de documentos do PJe). Os documentos foram "
               "remontados pelo rodapé 'Num. N - Pág. M' e pelo cabeçalho de página; sem "
               "data, e o tipo pode faltar (aí a coluna nome mostra a primeira linha). "
               "Confirme com peek/grep.")
    else:
        msg = (f"PDF SEM BOOKMARKS e sem rodapé do PJe: modo sem índice, em faixas de "
               f"{FAIXA} páginas. Localize com `grep {pdf_nome} <termo>` e leia com "
               f"`extract {pdf_nome} --pages a-b`.")
    print(f"\n*** AVISO: {msg} ***\n", file=sys.stderr)


def _peca_str(v) -> str:
    return "sim" if v is True else ("?" if v is None else "—")


# ----------------------------------------------------------------------------
# Comandos
# ----------------------------------------------------------------------------
def cmd_index(args):
    pdf = _abrir(args.pdf)
    nome_pdf = Path(args.pdf).name
    docs, info = construir_indice(pdf, args.pdf)
    sem = set(paginas_sem_texto(pdf, args.pdf, _docs_por_num(docs)))
    for d in docs:
        d["sem_texto"] = sum(1 for p in range(d["pg_ini"], d["pg_fim"] + 1) if p in sem)
    _avisar_modo(info, nome_pdf)
    if args.json:
        print(json.dumps([_publico(d) for d in docs],
                         ensure_ascii=False, indent=2))
        return
    pecas = sum(1 for d in docs if d["is_peca"] is True)
    indef = sum(1 for d in docs if d["is_peca"] is None)
    print(f"# Índice — {Path(args.pdf).stem}")
    print(f"\nTotal: {len(docs)} documentos · {len(pdf)} páginas · peças: {pecas} · "
          f"indefinidos (?): {indef} · páginas sem texto: {len(sem)}")
    if info["modo"] == "rodape":
        print("\n> **AVISO — PDF sem bookmarks.** Documentos remontados pelo rodapé "
              "'Num. N - Pág. M' do PJe (sem data; tipo pelo cabeçalho de página, quando há). "
              "Confirme com `peek`/`grep` antes de confiar no recorte.")
    elif info["modo"] == "faixas":
        print(f"\n> **AVISO — PDF sem bookmarks e sem rodapé do PJe.** Modo sem índice: cada "
              f"linha é uma faixa de {FAIXA} páginas, não um documento. Use `grep` para "
              f"localizar e `extract --pages a-b` para ler.")
    elif info["nomes_do_indice"]:
        print("\n(nomes lidos do documento Índice do PJe)")
    if sem:
        print(f"\n> {len(sem)} página(s) sem texto extraível (imagem): `sem-texto {nome_pdf}` "
              f"lista; `render {nome_pdf} --pages N` gera a imagem para leitura.")
    print("\n| seq | tipo | nome | evento | data | págs | s/ texto | peça? |")
    print("|----:|------|------|-------:|------|-----:|---------:|:-----:|")
    for d in docs:
        data = (d["data"] or "").split(" ")[0]
        print(f"| {d['seq']} | {_md(d['tipo'])} | {_md(_encurtar(d['nome'] or '', 70))} "
              f"| {d['num'] or ''} | {data} | {d['pg_ini']}-{d['pg_fim']} ({d['npags']}) "
              f"| {d['sem_texto'] or ''} | {_peca_str(d['is_peca'])} |")
    print("\npeça? sim = petição, decisão ou parecer · ? = petição genérica ou volume "
          "digitalizado (confira com peek/grep) · — = anexo/expediente")


def _pular_letterhead(texto: str) -> str:
    """Remove o timbre do tribunal do início, para o snippet mostrar substância."""
    out = []
    em_cabecalho = True
    for ln in texto.split("\n"):
        s = ln.strip()
        if not s:
            continue
        if em_cabecalho:
            if any(r.search(s) for r in LETTERHEAD_RES) or ROL_PARTES_RE.match(s):
                continue
            em_cabecalho = False  # primeira linha substantiva encontrada
        out.append(s)
    return "\n".join(out)


def cmd_peek(args):
    pdf = _abrir(args.pdf)
    docs, info = construir_indice(pdf, args.pdf)
    _avisar_modo(info, Path(args.pdf).name)
    por_seq, por_num = {d["seq"]: d for d in docs}, _docs_por_num(docs)
    for seq in _parse_seqs(args.docs):
        d = por_seq.get(seq)
        if not d:
            print(f"## seq {seq}: NÃO ENCONTRADO\n")
            continue
        # busca bastante texto (o timbre + rol de partes pode ser longo),
        # remove o cabeçalho, e só então trunca ao tamanho pedido.
        bruto, inf = texto_paginas(pdf, d["pg_ini"], d["pg_fim"], por_num,
                                   max_chars=max(args.chars * 10, 5000))
        bruto = re.sub(r"<!--.*?-->\n*", "", bruto).strip()
        snippet = _pular_letterhead(bruto)
        nome = f" · {d['nome']}" if d.get("nome") else ""
        meta = ", ".join(x for x in (f"evento {d['num']}" if d.get("num") else "", d.get("data") or "",
                                     f"pg {d['pg_ini']}-{d['pg_fim']}") if x)
        print(f"## seq {seq} — {d['tipo']}{nome} ({meta})")
        if not snippet and inf["sem_texto"]:
            print(f"(sem texto extraível nas primeiras páginas: imagem escaneada — "
                  f"`render {Path(args.pdf).name} --pages {inf['sem_texto'][0]}`)")
        print(snippet[:args.chars])
        print()


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", _norm(s))[:30].strip("-") or "doc"


def _fm(campos: dict) -> str:
    """Front matter YAML; aspas só quando o valor tem caractere especial do YAML."""
    linhas = ["---"]
    for k, v in campos.items():
        if v is None:
            v = ""
        elif isinstance(v, str) and (not v or re.search(r"[:#{}\[\]&*!|>'\"%@`]", v)
                                     or v[0] in "-?, " or v != v.strip()):
            v = json.dumps(v, ensure_ascii=False)
        linhas.append(f"{k}: {v}")
    return "\n".join(linhas + ["---", "", ""])


def _fonte_resumo(npags: int, info: dict) -> str:
    s, o = len(info["sem_texto"]), len(info["ocr"])
    if s == npags:
        return "sem-texto"
    if o == npags:
        return "ocr"
    if s == 0 and o == 0:
        return "texto-nativo"
    return "misto"


def cmd_extract(args):
    pdf = _abrir(args.pdf)
    nome_pdf = Path(args.pdf).name
    docs, info = construir_indice(pdf, args.pdf)
    _avisar_modo(info, nome_pdf)
    por_seq, por_num, da_pagina = {d["seq"]: d for d in docs}, _docs_por_num(docs), _doc_da_pagina(docs)

    alvos = []   # (nome_arquivo, campos_fm, pg_ini, pg_fim)
    if args.docs:
        for seq in _parse_seqs(args.docs):
            d = por_seq.get(seq)
            if not d:
                print(f"seq {seq}: NÃO ENCONTRADO", file=sys.stderr)
                continue
            campos = {"seq": seq, "tipo": d["tipo"], "nome": d.get("nome") or "",
                      "evento": d["num"], "data": d["data"],
                      "paginas": f"{d['pg_ini']}-{d['pg_fim']}"}
            alvos.append((f"doc_{seq:03d}_{_slug(d['slug'])}.md", campos, d["pg_ini"], d["pg_fim"]))
    else:
        for a, b in _parse_paginas(args.pages, len(pdf)):
            envolvidos = sorted({da_pagina[p]["seq"] for p in range(a, b + 1) if p in da_pagina})
            campos = {"paginas": f"{a}-{b}", "documentos": ", ".join(map(str, envolvidos)) or None}
            alvos.append((f"paginas_{a:04d}-{b:04d}.md", campos, a, b))
    if not alvos:
        sys.exit("ERRO: nada a extrair")

    npags = sum(b - a + 1 for _, _, a, b in alvos)
    estimativa = npags * TOKENS_POR_PAGINA
    if estimativa > args.limite_tokens and not args.confirmar:
        print(f"AVISO DE TAMANHO: {npags} páginas (~{_milhar(estimativa)} tokens estimados) — ler isso "
              f"inteiro estoura o contexto.\n  Prefira: `grep {nome_pdf} <termo>` para achar o "
              f"trecho, `peek` para o começo, ou `extract --pages a-b` em fatias.\n  Para gravar "
              f"assim mesmo (sem ler tudo de uma vez), repita com --confirmar.", file=sys.stderr)
        sys.exit(3)

    out_dir = _ensure_writable(Path(args.out) if args.out else _workspace_do_pdf(pdf, args.pdf, docs))
    gerados = []
    for nome, campos, a, b in alvos:
        corpo, inf = texto_paginas(pdf, a, b, por_num, pdf_nome=nome_pdf)
        campos.update({
            "fonte": _fonte_resumo(b - a + 1, inf),
            "paginas_sem_texto": _faixas_str(inf["sem_texto"]),
            "paginas_ocr": _faixas_str(inf["ocr"]),
            "origem": nome_pdf,
        })
        (out_dir / nome).write_text(_fm(campos) + corpo + "\n", encoding="utf-8")
        gerados.append((nome, len(corpo), inf))
    print(f"Gerados {len(gerados)} arquivo(s) em {out_dir}:")
    total = 0
    for nome, nchars, inf in gerados:
        tok = nchars // 4
        total += tok
        extra = []
        if inf["sem_texto"]:
            extra.append(f"sem texto: págs. {_faixas_str(inf['sem_texto'])}")
        if inf["ocr"]:
            extra.append(f"OCR: {len(inf['ocr'])} pág.")
        if tok > 40_000:
            extra.append("grande: leia por partes")
        print(f"  {nome}  (~{_milhar(tok)} tokens{'; ' + '; '.join(extra) if extra else ''})")
    print(f"Total: ~{_milhar(total)} tokens")


def _compilar_busca(termo: str, regex: bool, exato: bool):
    if not (termo or "").strip():
        sys.exit("ERRO: termo de busca vazio")
    if regex:   # na regex só se tiram acentos: minúscula trocaria \S por \s, \D por \d…
        alvo = termo if exato else termo.translate(_ACENTOS)
    else:
        partes = (termo if exato else _norm_mesmo_tamanho(termo)).split()
        alvo = r"\s+".join(re.escape(p) for p in partes)
    try:
        return re.compile(alvo, 0 if exato else re.IGNORECASE)
    except re.error as e:
        sys.exit(f"ERRO: expressão regular inválida: {e}")


def _grep(pdf, docs, termo, seqs=None, regex=False, exato=False, maximo=40, contexto=90):
    """Ocorrências do termo: [(pág., doc, trecho com **destaque**)], total."""
    pat = _compilar_busca(termo, regex, exato)
    por_num, da_pagina = _docs_por_num(docs), _doc_da_pagina(docs)
    if seqs:
        alvo = {d["seq"] for d in docs if d["seq"] in seqs}
        paginas = [p for d in docs if d["seq"] in alvo for p in range(d["pg_ini"], d["pg_fim"] + 1)]
    else:
        paginas = range(1, len(pdf) + 1)
    if len(paginas) > 300:
        print(f"(lendo {len(paginas)} páginas…)", file=sys.stderr)
    achados, total = [], 0
    for pg in paginas:
        linhas, _ = _ler_pagina(pdf, pg - 1, por_num, classificar=False)
        texto = _collapse(" ".join(linhas))
        busca = texto if exato else _norm_mesmo_tamanho(texto)
        for m in pat.finditer(busca):
            total += 1
            if len(achados) < maximo:
                a, b = m.start(), m.end()
                ini, fim = max(0, a - contexto), min(len(texto), b + contexto)
                trecho = (("…" if ini else "") + texto[ini:a] + "**" + texto[a:b] + "**"
                          + texto[b:fim] + ("…" if fim < len(texto) else ""))
                achados.append((pg, da_pagina.get(pg), trecho))
    return achados, total


def _desc_doc(d) -> str:
    if not d:
        return "fora dos documentos do índice"
    nome = f" · {_encurtar(d['nome'], 50)}" if d.get("nome") else ""
    ev = f" · evento {d['num']}" if d.get("num") else ""
    return f"seq {d['seq']} {d['tipo']}{nome}{ev} (págs. {d['pg_ini']}-{d['pg_fim']})"


def cmd_grep(args):
    pdf = _abrir(args.pdf)
    docs, info = construir_indice(pdf, args.pdf)
    _avisar_modo(info, Path(args.pdf).name)
    termo = args.termo if args.termo is not None else args.pattern
    seqs = set(_parse_seqs(args.docs)) if args.docs else None
    achados, total = _grep(pdf, docs, termo, seqs, args.regex, args.exato, args.max)
    escopo = f" nos documentos {args.docs}" if args.docs else ""
    if not total:
        print(f"Nenhuma ocorrência de {termo!r}{escopo}.")
        return
    paginas = len({p for p, _, _ in achados})
    print(f"# grep {termo!r}{escopo}: {total} ocorrência(s)"
          + (f" — mostrando {len(achados)} (use --max)" if total > len(achados) else "")
          + f", em {paginas} página(s) listadas\n")
    for pg, d, trecho in achados:
        print(f"- pág. {pg} · {_desc_doc(d)}\n  {trecho}")


def cmd_find(args):
    if args.pattern is not None:
        args.termo = None
        return cmd_grep(args)
    pdf = _abrir(args.pdf)
    docs, _ = construir_indice(pdf, args.pdf)
    alvo = re.sub(r"\D", "", str(args.id))
    achados = [d for d in docs if d.get("num") == alvo]
    for d in achados:
        print(json.dumps(_publico(d), ensure_ascii=False))
    if achados:
        return
    rod = _rodapes(pdf, args.pdf)
    paginas = [i + 1 for i, r in enumerate(rod) if r and r[0] == alvo]
    if paginas:
        print(f"Evento/id {alvo} sem bookmark próprio; aparece no rodapé das páginas "
              f"{_faixas_str(paginas)} (extract --pages).")
    else:
        print(f"Nenhum documento com evento/id {alvo} neste PDF.")


def cmd_refs(args):
    pdf = _abrir(args.pdf)
    docs, _ = construir_indice(pdf, args.pdf)
    por_seq, por_num = {d["seq"]: d for d in docs}, _docs_por_num(docs)
    for seq in _parse_seqs(args.docs):
        d = por_seq.get(seq)
        if not d:
            print(f"## seq {seq}: NÃO ENCONTRADO\n")
            continue
        texto = re.sub(r"<!--.*?-->", " ", texto_doc(pdf, d, docs_por_num=por_num))
        texto = _collapse(texto)
        vistos: dict[tuple, str] = {}
        for m in CITACAO_ID_RE.finditer(texto):
            chave = (m.group(1), m.group(2))
            if m.group(1) != d.get("num") and chave not in vistos:
                vistos[chave] = texto[max(0, m.start() - 60): m.end() + 40].strip()
        print(f"## seq {seq} — {d['tipo']} (evento {d.get('num')}): "
              f"{len(vistos)} referência(s) 'id N'")
        for (num, pag), ctx in vistos.items():
            alvo = por_num.get(num)
            destino = _desc_doc(alvo) if alvo else "não está no índice deste PDF"
            if alvo and pag and int(pag) <= alvo["npags"]:
                destino += f" → pág. {pag} do documento = pág. {alvo['pg_ini'] + int(pag) - 1} do PDF"
            rotulo = f"id {num}" + (f", pág. {pag}" if pag else "")
            print(f"- {rotulo} → {destino}\n  “…{ctx}…”")
        print()


def cmd_sem_texto(args):
    pdf = _abrir(args.pdf)
    docs, info = construir_indice(pdf, args.pdf)
    sem = paginas_sem_texto(pdf, args.pdf, _docs_por_num(docs))
    filtro = set(_parse_seqs(args.doc)) if args.doc else None
    saida = []
    for d in docs:
        if filtro is not None and d["seq"] not in filtro:
            continue
        pags = [p for p in sem if d["pg_ini"] <= p <= d["pg_fim"]]
        if pags or filtro is not None:
            saida.append({"seq": d["seq"], "tipo": d["tipo"], "nome": d.get("nome") or "",
                          "evento": d.get("num"), "pg_ini": d["pg_ini"], "pg_fim": d["pg_fim"],
                          "paginas": pags, "faixas": _faixas_str(pags)})
    if args.json:
        print(json.dumps({"pdf": str(Path(args.pdf).resolve()), "total_paginas": len(pdf),
                          "criterio": CRITERIO_SEM_TEXTO,
                          "paginas_sem_texto": sum(len(s["paginas"]) for s in saida),
                          "documentos": saida}, ensure_ascii=False, indent=2))
        return
    total = sum(len(s["paginas"]) for s in saida)
    if not total:
        print("Nenhuma página sem texto" + (f" nos documentos {args.doc}." if args.doc else " no PDF."))
        return
    print(f"# Páginas sem texto extraível — {total} página(s)\n")
    for s in saida:
        if s["paginas"]:
            print(f"- seq {s['seq']} {s['tipo']}"
                  + (f" · {_encurtar(s['nome'], 50)}" if s["nome"] else "")
                  + f": págs. {s['faixas']} ({len(s['paginas'])} de {s['pg_fim'] - s['pg_ini'] + 1})")
    print(f"\nPara ler uma página decisiva: `render {Path(args.pdf).name} --pages N`.")


def _png_cinza(caminho: Path, largura: int, altura: int, passo: int, buf: bytes) -> None:
    """PNG em tons de cinza sem dependências (usado quando o Pillow não está instalado)."""
    linhas = b"".join(b"\x00" + buf[y * passo: y * passo + largura] for y in range(altura))

    def bloco(tag: bytes, dados: bytes) -> bytes:
        return (struct.pack(">I", len(dados)) + tag + dados
                + struct.pack(">I", zlib.crc32(tag + dados) & 0xFFFFFFFF))

    caminho.write_bytes(b"\x89PNG\r\n\x1a\n"
                        + bloco(b"IHDR", struct.pack(">IIBBBBB", largura, altura, 8, 0, 0, 0, 0))
                        + bloco(b"IDAT", zlib.compress(linhas, 6)) + bloco(b"IEND", b""))


def cmd_render(args):
    pdf = _abrir(args.pdf)
    paginas = [p for a, b in _parse_paginas(args.pages, len(pdf)) for p in range(a, b + 1)]
    paginas = list(dict.fromkeys(paginas))
    if len(paginas) > MAX_RENDER and not args.confirmar:
        sys.exit(f"AVISO: {len(paginas)} páginas pedidas; cada imagem custa ~1.500 tokens para "
                 f"ler. Renderize só as decisivas (máx. {MAX_RENDER} por vez) ou repita com --confirmar.")
    try:
        import PIL  # noqa: F401
        com_pil = True
    except ImportError:
        com_pil = False
        print("(Pillow não instalado: PNG em tons de cinza. Para cor: pip install pillow)",
              file=sys.stderr)
    if args.out:
        out_dir = _ensure_writable(Path(args.out))
    else:
        docs, _ = construir_indice(pdf, args.pdf)
        out_dir = _ensure_writable(_workspace_do_pdf(pdf, args.pdf, docs) / "imagens")
    gerados = []
    for p in paginas:
        page = pdf[p - 1]
        try:
            w, h = page.get_size()
            escala = min(args.escala, MAX_PX / max(w, h, 1))
            destino = out_dir / f"pag_{p:04d}.png"
            if com_pil:
                page.render(scale=escala).to_pil().save(destino, "PNG")
            else:
                bm = page.render(scale=escala, grayscale=True)
                if getattr(bm, "n_channels", 1) != 1:
                    sys.exit("ERRO: esta versão do pypdfium2 não gera bitmap em tons de cinza; "
                             "instale o Pillow: pip install pillow")
                _png_cinza(destino, bm.width, bm.height, bm.stride, bytes(bm.buffer))
            gerados.append(destino)
        finally:
            page.close()
    print(f"Gerada(s) {len(gerados)} imagem(ns) em {out_dir}:")
    for g in gerados:
        print(f"  {g}")
    print("Leia cada PNG com a ferramenta de leitura de arquivo (o Claude lê a imagem). "
          "Transcrição de imagem não é texto nativo: marque-a como tal e confira antes de citar.")


# ----------------------------------------------------------------------------
# Workspace — pasta gravável e, de preferência, persistente do processo
# ----------------------------------------------------------------------------
def _writable(p: Path) -> bool:
    try:
        p.mkdir(parents=True, exist_ok=True)
        t = p / ".w_test"
        t.write_text("x", encoding="utf-8")
        try:
            t.unlink()
        except Exception:
            pass  # alguns mounts (Cowork) gravam mas bloqueiam delete; gravar basta
        return True
    except Exception:
        return False


def _parece_temporario(p: Path) -> bool:
    s = str(p).replace("\\", "/").lower()
    tmp = str(Path(tempfile.gettempdir())).replace("\\", "/").lower()
    return (s.startswith(tmp) or "/scratch-workspaces/" in s or s.startswith("/sessions/")
            or "/appdata/local/temp/" in s or s.startswith("/tmp/"))


def _aviso_temporario(caminho: Path, motivo: str) -> None:
    print("\n" + "=" * 72 + "\n"
          f"AVISO: PASTA TEMPORÁRIA — {motivo}\n"
          f"  Os dados deste processo vão para {caminho}\n"
          "  e podem SUMIR ao fim da sessão (o trabalho já extraído se perde).\n"
          "  Para fixar uma pasta: defina PRATICA_JURIDICA_DATA=<pasta gravável>\n"
          "    Windows: setx PRATICA_JURIDICA_DATA \"C:\\Users\\<você>\\Documents\\dados-juridicos\""
          " (reabra o app)\n"
          "    macOS/Linux: export PRATICA_JURIDICA_DATA=~/dados-juridicos (no perfil do shell)\n"
          "  ou crie uma pasta dados-juridicos/ na pasta de trabalho da sessão.\n"
          + "=" * 72 + "\n", file=sys.stderr)


def _ensure_writable(out_dir: Path) -> Path:
    """Garante um diretório gravável. Se o pedido falhar (ex.: pasta read-only no
    sandbox do Cowork), cai para ./outputs/<nome> e avisa."""
    if _writable(out_dir):
        return out_dir
    fb = Path.cwd() / "outputs" / out_dir.name
    fb.mkdir(parents=True, exist_ok=True)
    _aviso_temporario(fb.resolve(), f"{out_dir} não é gravável")
    return fb


def _dados_juridicos() -> Path | None:
    """Pasta `dados-juridicos/` já existente e gravável: no cwd, nos ancestrais ou, no
    Cowork, nas pastas montadas irmãs sob `mnt/`. Criá-la é decisão do usuário."""
    cur = Path.cwd().resolve()
    for anc in (cur, *cur.parents):
        bases = [anc]
        mnt = anc if anc.name == "mnt" else anc / "mnt"
        try:
            if mnt.is_dir():
                bases += sorted(p for p in mnt.iterdir() if p.is_dir())
        except OSError:
            pass
        for base in bases:
            cand = base / "dados-juridicos"
            try:
                if cand.is_dir() and _writable(cand):
                    return cand
            except OSError:
                continue
    return None


def _data_root() -> tuple[Path, str, bool]:
    """(raiz, origem, persistente) por precedência: PRATICA_JURIDICA_DATA →
    CLAUDE_PLUGIN_DATA → dados-juridicos/ detectada → ./outputs (sessão)."""
    for var in ("PRATICA_JURIDICA_DATA", "CLAUDE_PLUGIN_DATA"):
        if os.environ.get(var):
            p = Path(os.environ[var]).expanduser()
            if _writable(p):
                return p, var, not _parece_temporario(p)
            print(f"[aviso] {var}={p} não é gravável; ignorado", file=sys.stderr)
    achada = _dados_juridicos()
    if achada is not None:
        return achada, "dados-juridicos/", not _parece_temporario(achada)
    p = Path.cwd() / "outputs"
    if _writable(p):
        return p, "./outputs da sessão", False
    return Path.cwd(), "pasta atual", False


def normalizar_cnj(cnj: str) -> str:
    """'12345678920244058100' → '1234567-89.2024.4.05.8100'. Identificador fora do padrão
    CNJ é aceito se tiver só letras, dígitos, ponto, hífen e sublinhado."""
    s = (cnj or "").strip()
    digitos = re.sub(r"\D", "", s)
    if len(digitos) == 20:
        d = digitos
        return f"{d[:7]}-{d[7:9]}.{d[9:13]}.{d[13]}.{d[14:16]}.{d[16:]}"
    seguro = re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-.")
    if not seguro or not re.search(r"[A-Za-z0-9]", seguro):
        raise ValueError(f"identificador de processo inválido: {cnj!r}")
    return seguro


def resolver_workspace(cnj: str) -> tuple[Path, str, bool]:
    """(pasta do processo, origem, persistente). Reaproveita o layout antigo
    <raiz>/<cnj> se ele já existir; senão usa <raiz>/processos/<cnj>."""
    canon = normalizar_cnj(cnj)
    root, origem, persistente = _data_root()
    digitos = re.sub(r"\D", "", canon)
    candidatos = [root / "processos" / canon, root / canon]
    if len(digitos) == 20:
        candidatos += [root / "processos" / digitos, root / digitos]
    ws = next((c for c in candidatos if c.is_dir()), root / "processos" / canon)
    ws.mkdir(parents=True, exist_ok=True)
    if ws.parent == root:
        print(f"[ok] reaproveitando a pasta do layout antigo <raiz>/<cnj>: {ws}", file=sys.stderr)
    return ws.resolve(), origem, persistente


def _diagnostico_workspace(ws: Path, origem: str, persistente: bool) -> None:
    if persistente:
        print(f"[ok] dados em {origem} (persistente): {ws}", file=sys.stderr)
    elif origem in ("PRATICA_JURIDICA_DATA", "CLAUDE_PLUGIN_DATA"):
        _aviso_temporario(ws, f"{origem} aponta para uma pasta temporária")
    else:
        _aviso_temporario(ws, f"nenhuma pasta fixa configurada (usando {origem})")


def _cnj_do_pdf(pdf, pdf_path: str, docs) -> str | None:
    """CNJ do processo: campo 'Número:' do cabeçalho do PJe, nome do arquivo ou 1ª página."""
    try:
        linhas, _ = _ler_pagina(pdf, 0, classificar=False)
    except Exception:
        linhas = []
    primeira = "\n".join(linhas)
    m = re.search(r"N[úu]mero:\s*" + CNJ_RE.pattern, primeira)
    m = m or CNJ_RE.search(Path(pdf_path).stem) or CNJ_RE.search(primeira)
    if not m:
        return None
    g = m.groups()[-6:]
    return f"{g[0]}-{g[1]}.{g[2]}.{g[3]}.{g[4]}.{g[5]}"


def _workspace_do_pdf(pdf, pdf_path: str, docs) -> Path:
    cnj = _cnj_do_pdf(pdf, pdf_path, docs)
    if not cnj:
        sys.exit("ERRO: não achei o número CNJ no PDF para escolher a pasta do processo. "
                 "Informe --out <pasta> (o caminho impresso por `processo.py workspace <cnj>`).")
    ws, origem, persistente = resolver_workspace(cnj)
    print(f"[workspace] processo {cnj} → {ws}", file=sys.stderr)
    if not persistente:
        _diagnostico_workspace(ws, origem, persistente)
    return ws


def cmd_workspace(args):
    """Resolve/cria a pasta do processo e imprime o caminho ABSOLUTO no stdout. O
    diagnóstico de persistência vai para o stderr (nunca quebra o comando)."""
    try:
        ws, origem, persistente = resolver_workspace(args.cnj)
    except ValueError as e:
        sys.exit(f"ERRO: {e}")
    print(str(ws))
    _diagnostico_workspace(ws, origem, persistente)


# ----------------------------------------------------------------------------
def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")  # console cp1252 no Windows
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Leitura seletiva de processos do PJe em PDF.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("index", help="mapa dos documentos")
    p.add_argument("pdf")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_index)

    p = sub.add_parser("peek", help="início de cada documento, sem o timbre")
    p.add_argument("pdf")
    p.add_argument("--docs", required=True)
    p.add_argument("--chars", type=int, default=400)
    p.set_defaults(func=cmd_peek)

    p = sub.add_parser("extract", help="markdown limpo de documentos ou de páginas")
    p.add_argument("pdf")
    alvo = p.add_mutually_exclusive_group(required=True)
    alvo.add_argument("--docs", help="seqs do índice: 10,23")
    alvo.add_argument("--pages", help="páginas do PDF: 5-9,12")
    p.add_argument("--out", help="pasta de saída (padrão: workspace do processo, pelo CNJ do PDF)")
    p.add_argument("--confirmar", action="store_true", help="extrair mesmo acima do limite de tamanho")
    p.add_argument("--limite-tokens", type=int, default=LIMITE_TOKENS)
    p.set_defaults(func=cmd_extract)

    p = sub.add_parser("grep", help="busca textual com página e documento")
    p.add_argument("pdf")
    p.add_argument("termo")
    p.add_argument("--docs", help="limitar aos seqs: 10,23")
    p.add_argument("--regex", action="store_true", help="termo é expressão regular")
    p.add_argument("--exato", action="store_true", help="diferenciar maiúsculas e acentos")
    p.add_argument("--max", type=int, default=40, help="máximo de ocorrências listadas")
    p.set_defaults(func=cmd_grep, pattern=None)

    p = sub.add_parser("find", help="evento/id do PJe -> documento (--pattern = grep)")
    p.add_argument("pdf")
    q = p.add_mutually_exclusive_group(required=True)
    q.add_argument("--id")
    q.add_argument("--pattern", help="o mesmo que `grep <pdf> <termo>`")
    p.add_argument("--docs")
    p.add_argument("--regex", action="store_true")
    p.add_argument("--exato", action="store_true")
    p.add_argument("--max", type=int, default=40)
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("refs", help='referências "id N" de um documento -> documentos')
    p.add_argument("pdf")
    p.add_argument("--docs", required=True)
    p.set_defaults(func=cmd_refs)

    p = sub.add_parser("sem-texto", help="páginas sem texto extraível (imagem escaneada)")
    p.add_argument("pdf")
    p.add_argument("--doc", help="limitar aos seqs: 3 ou 3,5")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_sem_texto)

    p = sub.add_parser("render", help="PNG das páginas, para ler a imagem")
    p.add_argument("pdf")
    p.add_argument("--pages", required=True)
    p.add_argument("--out", help="pasta de saída (padrão: <workspace>/imagens)")
    p.add_argument("--escala", type=float, default=2.0)
    p.add_argument("--confirmar", action="store_true")
    p.set_defaults(func=cmd_render)

    p = sub.add_parser("workspace", help="pasta gravável do processo (imprime o caminho)")
    p.add_argument("cnj")
    p.set_defaults(func=cmd_workspace)

    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
