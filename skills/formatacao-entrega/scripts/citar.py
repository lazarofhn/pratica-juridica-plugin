#!/usr/bin/env python3
"""citar.py — resolve `@citacao-ref`: devolve o texto VERBATIM da fonte citada.

Duas fontes:
- jurisprudência (padrão): a saída do conector de jurisprudência (MCP) gravada no
  transcript da SESSÃO ATUAL. Só valem saídas de ferramenta MCP — nunca texto do modelo
  nem saída de Bash. Arquivos lidos: transcript principal da sessão, os dos subagentes e
  as saídas grandes salvas à parte (tool-results). Sem id de sessão no ambiente, o
  projeto da pasta atual (no Cowork, o único projeto do mount da sessão). Outra sessão
  ou projeto só com --transcript <arquivo|pasta>.
- autos (`fonte: autos`): o .md extraído pelo processo.py no workspace do processo.

Casamento: pelo número normalizado (só dígitos, número inteiro — "REsp 213661" não casa
"REsp 2136610"), com classe compatível ("AREsp" não casa "REsp"); ou pelo ID do
conector (`id:`). Mesmo julgado na busca e no detalhes: vale o detalhes (ementa
íntegra); empate: o resultado mais recente. Dois julgados possíveis: erro, peça `id:`.

Cache: com workspace, a ementa achada fica em <workspace>/citacoes/<chave>.json e é
usada quando o transcript da sessão não a tem mais (outra sessão, outro ambiente).

FIDELIDADE: só se normaliza espaço em branco (junta linhas quebradas). Nunca se altera
caractere dentro de palavra. Do resultado do TRF-5 sai só o cabeçalho do PJe com as
partes (o texto começa em "EMENTA"). Texto com o marcador de truncamento do conector ou
com '?' no lugar de aspa/travessão (defeito de codificação) é recusado com erro.

Uso — imprime SÓ o texto resolvido (o mesmo que entra no .docx); a procedência vai para
o stderr, ou para o JSON com --json:
    python citar.py --processo "REsp 2.136.610" [--id ID] [--itens 1-2]
        [--trecho 'de "..." ate "..."'] [--grifo "trecho"] [--transcript PATH]
        [--workspace DIR] [--json]
    python citar.py --fonte autos --workspace DIR (--doc 28 | --arquivo doc_028_x.md)
        [--itens ...] [--trecho ...]
"""
from __future__ import annotations

import datetime
import glob
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

# --------------------------------------------------------------- normalização
_ACENTOS = str.maketrans("áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
                         "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN")
# Palavras que não identificam a classe do julgado (base, rótulos, preposições).
_NEUTRAS = {
    "n", "no", "na", "nos", "nas", "do", "da", "dos", "das", "de", "e", "em", "o", "a",
    "num", "numero", "processo", "proc", "acordao", "acordaos", "solucao", "consulta",
    "divergencia", "cosit", "disit", "carf", "csrf", "stj", "stf", "tcu", "trf", "tjpe",
    "rfb", "id", "ementa", "resultado", "tema", "rel", "min", "turma",
}
_NUM_RE = re.compile(r"\d+(?:[.\-/]\d+)*")


def collapse(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def _tokens(s: str) -> list[str]:
    s = unicodedata.normalize("NFKD", (s or "").translate(_ACENTOS))
    s = "".join(c for c in s if not unicodedata.combining(c)).lower()
    return [t for t in re.findall(r"[a-z]+", s)]


def _classe(s: str) -> frozenset:
    """Tokens de classe do localizador: 'AgInt no AREsp 2.115.749/SP' → {agint, aresp}."""
    s = re.sub(r"(?<=\d)/[A-Za-z]{2}\b", "", s or "")       # UF depois do número
    return frozenset(t for t in _tokens(s) if t not in _NEUTRAS and len(t) > 1)


def _numeros(s: str) -> list[str]:
    """Cada número do texto só com dígitos: '2.136.610/PR' → '2136610'."""
    return [re.sub(r"\D", "", m.group()) for m in _NUM_RE.finditer(s or "")]


# --------------------------------------------------------------- transcripts
def _raizes_projetos() -> list[Path]:
    """Pastas `.claude/projects` candidatas: env CLAUDE_PROJECTS_DIR, HOME e, subindo do
    diretório atual, `.claude/projects` e `mnt/.claude/projects` (mount do Cowork)."""
    cands = []
    if os.environ.get("CLAUDE_PROJECTS_DIR"):
        cands.append(Path(os.environ["CLAUDE_PROJECTS_DIR"]))
    cands.append(Path.home() / ".claude" / "projects")
    cur = Path.cwd().resolve()
    for anc in (cur, *cur.parents):
        cands += [anc / ".claude" / "projects", anc / "mnt" / ".claude" / "projects"]
    vistos, out = set(), []
    for c in cands:
        try:
            if str(c) not in vistos and c.is_dir():
                vistos.add(str(c))
                out.append(c)
        except OSError:
            continue
    return out


def _arquivos_de_sessao(pasta_projeto: Path, sid: str) -> list[Path]:
    arqs = [pasta_projeto / f"{sid}.jsonl"]
    sessao = pasta_projeto / sid
    arqs += sorted(sessao.glob("subagents/*.jsonl")) + sorted(sessao.glob("tool-results/*"))
    return [a for a in arqs if a.is_file()]


def arquivos_da_sessao(transcript: str | None = None) -> list[Path]:
    """Arquivos de onde ler as saídas do conector. Explícito (--transcript) vence; senão,
    a sessão atual (CLAUDE_CODE_SESSION_ID); senão, o projeto da pasta atual."""
    if transcript:
        p = Path(transcript)
        if p.is_dir():
            return sorted(x for x in p.rglob("*") if x.is_file() and
                          (x.suffix == ".jsonl" or x.parent.name == "tool-results"))
        if p.is_file():
            irmaos = sorted((p.parent / p.stem).glob("tool-results/*")) if p.suffix == ".jsonl" else []
            return [p, *irmaos]
        raise LookupError(f"--transcript não encontrado: {transcript}")
    raizes = _raizes_projetos()
    sid = os.environ.get("CLAUDE_CODE_SESSION_ID") or os.environ.get("CLAUDE_SESSION_ID")
    if sid and re.fullmatch(r"[A-Za-z0-9-]+", sid):
        for raiz in raizes:
            try:
                projetos = [p for p in raiz.iterdir() if p.is_dir()]
            except OSError:
                continue
            for proj in projetos:   # só nomes de pasta: nada de outros projetos é lido
                if (proj / f"{sid}.jsonl").is_file() or (proj / sid).is_dir():
                    return _arquivos_de_sessao(proj, sid)
    def do_projeto(proj: Path) -> list[Path]:
        arqs = []
        for t in sorted(proj.glob("*.jsonl"), key=lambda x: x.stat().st_mtime, reverse=True):
            arqs += _arquivos_de_sessao(proj, t.stem)
        return arqs

    slug = re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd().resolve()))
    for raiz in raizes:
        if (raiz / slug).is_dir():
            return do_projeto(raiz / slug)
    # Cowork: o mount da sessão (…/mnt/.claude/projects) só tem o projeto desta sessão
    home = (Path.home() / ".claude" / "projects").resolve()
    for raiz in raizes:
        try:
            projetos = [p for p in raiz.iterdir() if p.is_dir()]
        except OSError:
            continue
        if raiz.resolve() != home and raiz.parent.parent.name == "mnt" and len(projetos) == 1:
            return do_projeto(projetos[0])
    return []


def _texto_resultado(conteudo) -> str:
    """Texto de um tool_result (string ou lista de blocos), sem o envelope {"result": …}."""
    if isinstance(conteudo, list):
        conteudo = "\n".join(c.get("text", "") for c in conteudo if isinstance(c, dict))
    if not isinstance(conteudo, str):
        return ""
    s = conteudo.strip()
    if s.startswith("{") and '"result"' in s[:40]:
        try:
            obj = json.loads(s)
            if isinstance(obj, dict) and isinstance(obj.get("result"), str):
                return obj["result"]
        except json.JSONDecodeError:
            pass
    return conteudo


def _id_da_chamada(entrada) -> str | None:
    """ID pedido ao `*_detalhes_*` (ponto_id, acordao_pk, key…), se houver."""
    if not isinstance(entrada, dict):
        return None
    params = entrada.get("params", entrada)
    if isinstance(params, dict):
        for k in ("ponto_id", "acordao_pk", "key", "id"):
            if params.get(k) not in (None, ""):
                return str(params[k]).strip()
    return None


_MEMO: dict = {}


def _saidas_mcp(arquivos: list[Path], explicito: bool) -> list[dict]:
    """Saídas de ferramenta MCP: [{texto, ordem, id_chamada, origem}]. Arquivo avulso
    passado com --transcript (não .jsonl) vale como uma saída do conector."""
    chamadas: dict[str, tuple[str, dict]] = {}
    saidas, lidos = [], set()
    for arq in arquivos:
        if arq.suffix != ".jsonl":
            continue
        chave = (str(arq), arq.stat().st_mtime_ns, arq.stat().st_size)
        if chave not in _MEMO:
            ch, rs = {}, []
            with open(arq, encoding="utf-8", errors="replace") as f:
                for n, linha in enumerate(f):
                    if '"tool_use' not in linha and '"tool_result"' not in linha:
                        continue
                    try:
                        obj = json.loads(linha)
                    except json.JSONDecodeError:
                        continue
                    conteudo = (obj.get("message") or {}).get("content")
                    if not isinstance(conteudo, list):
                        continue
                    for item in conteudo:
                        if not isinstance(item, dict):
                            continue
                        if item.get("type") == "tool_use":
                            ch[item.get("id")] = (item.get("name") or "", item.get("input"))
                        elif item.get("type") == "tool_result":
                            rs.append((item.get("tool_use_id"), obj.get("timestamp") or "", n,
                                       _texto_resultado(item.get("content"))))
            _MEMO[chave] = (ch, rs)
        ch, rs = _MEMO[chave]
        chamadas.update(ch)
        for tid, ts, n, texto in rs:
            origem = str(arq)
            if texto.lstrip().startswith("<persisted-output>"):
                m = re.search(r"saved to:\s*(.+?)\s*$", texto, re.M)
                salvo = Path(m.group(1)) if m else None
                if not (salvo and salvo.is_file()):
                    continue          # só a prévia: não serve como fonte
                lidos.add(str(salvo.resolve()))
                texto, origem = _texto_resultado(salvo.read_text(encoding="utf-8", errors="replace")), str(salvo)
            saidas.append({"tid": tid, "ordem": (ts, n), "texto": texto, "origem": origem})
    resultado = []
    for s in saidas:
        nome, entrada = chamadas.get(s["tid"], ("", None))
        if nome.startswith("mcp__"):
            resultado.append({**s, "id_chamada": _id_da_chamada(entrada)})
    for arq in arquivos:
        if arq.suffix == ".jsonl" or str(arq.resolve()) in lidos:
            continue
        nome, entrada = chamadas.get(arq.stem, ("", None))
        if nome.startswith("mcp__") or (explicito and arq.parent.name != "tool-results"):
            texto = _texto_resultado(arq.read_text(encoding="utf-8", errors="replace"))
            ordem = (datetime.datetime.fromtimestamp(arq.stat().st_mtime,
                                                     datetime.timezone.utc).isoformat(), 0)
            resultado.append({"tid": arq.stem, "ordem": ordem, "texto": texto,
                              "origem": str(arq), "id_chamada": _id_da_chamada(entrada)})
    return resultado


# --------------------------------------------------------------- blocos de resultado
# Busca:    "### Resultado N (ID: …)" (STJ/STF) ou "### N. <rótulo> — … ID `…`" (demais bases).
# Detalhes: "## <BASE> — Acórdão|Ementa|Solução <nº ou ID>" e "## Solução de Consulta … — ID …".
_BUSCA_HDR = re.compile(r"^###\s+(?:Resultado\b|\d+\.\s)", re.M)
_DETALHE_HDR = re.compile(r"^##\s+(?:[^\n]*?\s—\s+)?(?:Ac[óo]rd[ãa]o|Ementa|Solu[çc][ãa]o|Decis[ãa]o)\b[^\n]*$",
                          re.M | re.IGNORECASE)
_CAMPO_RE = re.compile(r"^\*\*([^*\n]+)\*\*:\s*(.*)$", re.M)
_ID_RES = [re.compile(r"\(ID:\s*([^)\s]+)\)"), re.compile(r"\bID\s*`([^`]+)`"),
           re.compile(r"\bID\s+([\w:.\-/]+)\s*$")]
# Partes e relator do cabeçalho do PJe que o TRF-5 põe antes da ementa.
_CAB_PJE = re.compile(r"^\s*(PROCESSO\s*N|PODER JUDICI|TRIBUNAL|APELA|AGRAVA|EMBARGA|RECORRE|"
                      r"IMPETRA|AUTOR|R[ÉE]U\b|ADVOGAD|PROCURAD|RELATOR)", re.IGNORECASE)
_PARTES = re.compile(r"\b(APELANTE|APELAD[OA]S?|AGRAVANTE|AGRAVAD[OA]|EMBARGANTE|EMBARGAD[OA]|"
                     r"RECORRENTE|RECORRID[OA]|IMPETRANTE|IMPETRAD[OA]|ADVOGAD[OA]S?|RELATOR)\b",
                     re.IGNORECASE)


def _campos(bloco: str) -> dict:
    out = {}
    for m in _CAMPO_RE.finditer(bloco):
        k = " ".join(_tokens(m.group(1)))
        out.setdefault(k, m.group(2).strip())
    for linha in bloco.split("\n")[:4]:          # "**Score**: … | **Processo**: … | …"
        for m in re.finditer(r"\*\*([^*]+)\*\*:\s*([^|]+)", linha):
            out.setdefault(" ".join(_tokens(m.group(1))), m.group(2).strip())
    return out


def _sem_cabecalho_pje(t: str) -> str:
    m = re.search(r"\bEMENTA\b", t)
    if m and m.start() > 0 and _CAB_PJE.match(t) and _PARTES.search(t[:m.start()]):
        return t[m.start():]
    return t


def _ementa_de(tipo: str, bloco: str) -> str:
    if tipo == "detalhes":
        m = re.search(r"^###\s*Ementa\s*$\n?(.*?)(?=^#{2,3}\s|^_[^\n]*_\s*$|\Z)", bloco, re.M | re.S)
        texto = m.group(1) if m else ""
    else:
        m = re.search(r"\*\*Ementa\*\*:\s*\n?(.*)", bloco, re.S)
        if m:
            texto = m.group(1)
        else:   # bases com a ementa em citação Markdown ('> ')
            texto = "\n".join(re.sub(r"^\s*>\s?", "", ln) for ln in bloco.split("\n")
                              if ln.lstrip().startswith(">"))
    return _sem_cabecalho_pje(texto.strip())


def _blocos(saida: dict):
    texto = saida["texto"]
    marcas = sorted([(m.start(), "busca") for m in _BUSCA_HDR.finditer(texto)]
                    + [(m.start(), "detalhes") for m in _DETALHE_HDR.finditer(texto)])
    for k, (ini, tipo) in enumerate(marcas):
        fim = marcas[k + 1][0] if k + 1 < len(marcas) else len(texto)
        bloco = texto[ini:fim]
        if tipo == "busca":
            corte = re.search(r"\n\s*---\s*(\n|$)", bloco)
            bloco = bloco[:corte.start()] if corte else bloco
        ementa = _ementa_de(tipo, bloco)
        if not ementa:
            continue
        cab = bloco.split("\n", 1)[0].strip()
        campos = _campos(bloco)
        ids = [m.group(1).strip() for r in _ID_RES for m in [r.search(cab)] if m]
        if campos.get("id"):
            ids.append(campos["id"])
        if tipo == "detalhes" and saida.get("id_chamada"):
            ids.insert(0, saida["id_chamada"])
        loc = " ".join([cab] + [campos.get(k, "") for k in
                                ("processo", "numero", "titulo", "classe", "registro", "descricao classe")])
        nums = set(_numeros(loc))
        if campos.get("numero") and campos.get("ano"):
            nums.add(re.sub(r"\D", "", campos["numero"]) + re.sub(r"\D", "", campos["ano"]))
        cab_sem_enum = re.sub(r"^#+\s*(?:Resultado\s+\d+|\d+\.)?\s*", "", cab)
        classe_src = campos.get("classe") or campos.get("processo") or cab_sem_enum
        classe_id = _classe(re.split(r"\(|\d", classe_src, maxsplit=1)[0])
        yield {"tipo": tipo, "cabecalho": cab, "ementa": ementa, "ids": ids, "numeros": nums,
               "tokens": frozenset(_tokens(loc)), "classe": classe_id,
               "ordem": saida["ordem"], "origem": saida["origem"]}


# --------------------------------------------------------------- escolha do julgado
def _casa(b: dict, num: str | None, classe: frozenset, id_: str | None) -> bool:
    if id_:
        return id_ in b["ids"] or (id_.isdigit() and id_ in b["numeros"])
    if not num or num not in b["numeros"]:
        return False
    # Número curto (STJ/STF) exige a classe: REsp 123 e AREsp 123 são processos diferentes.
    # Número CNJ (20 dígitos) identifica o processo sozinho; a classe varia entre bases.
    return classe <= b["tokens"] or len(num) >= 15


def _identidade(b: dict, num: str | None):
    if b["ids"]:
        return ("id", b["ids"][0])
    return ("num", num, b["classe"])


def _escolher(blocos: list[dict], processo: str, num, classe, id_) -> dict | None:
    achados = [b for b in blocos if _casa(b, num, classe, id_)]
    if not achados:
        return None
    grupos: dict = {}
    for b in achados:
        grupos.setdefault(_identidade(b, num), []).append(b)
    # busca e detalhes do mesmo julgado com IDs diferentes: mesma ementa = mesmo julgado
    def mesma_ementa(a: str, b: str) -> bool:
        a, b = collapse(a), collapse(b)
        return a[:300] == b[:300] or (min(len(a), len(b)) >= 200 and (a in b or b in a))

    fundidos: dict = {}
    for chave, bs in grupos.items():
        alvo = next((k for k, v in fundidos.items() if mesma_ementa(v[0]["ementa"], bs[0]["ementa"])), None)
        fundidos.setdefault(alvo or chave, []).extend(bs)
    if len(fundidos) > 1 and classe and not id_:
        exatos = {k: v for k, v in fundidos.items() if v[0]["classe"] == classe}
        fundidos = exatos or fundidos
    if len(fundidos) > 1:
        lista = "; ".join(f"{v[0]['cabecalho']} [ID {v[0]['ids'][0] if v[0]['ids'] else '?'}]"
                          for v in list(fundidos.values())[:5])
        raise LookupError(f"{processo!r} casa com {len(fundidos)} julgados diferentes: {lista}. "
                          f"Indique o julgado com `id:` (o ID do resultado do conector).")
    bs = next(iter(fundidos.values()))
    return max(bs, key=lambda b: (b["tipo"] == "detalhes", b["ordem"]))


# --------------------------------------------------------------- cache no workspace
def _chave_cache(processo: str | None, id_: str | None) -> str:
    if id_:
        base = "id-" + id_
    else:
        nums = _numeros(processo or "")
        base = "-".join(sorted(_classe(processo or "")) + [max(nums, key=len) if nums else ""])
    return re.sub(r"[^a-z0-9]+", "-", base.lower()).strip("-")[:80] or "citacao"


def _cache_ler(workspace, processo, num, classe, id_):
    if not workspace:
        return None
    p = Path(workspace) / "citacoes" / f"{_chave_cache(processo, id_)}.json"
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
        b = {**d, "ids": d.get("ids", []), "numeros": set(d.get("numeros", [])),
             "tokens": frozenset(d.get("tokens", [])), "classe": frozenset(d.get("classe", []))}
        return b if _casa(b, num, classe, id_) else None
    except (OSError, ValueError):
        return None


def _cache_gravar(workspace, processo, id_, b: dict) -> None:
    if not workspace:
        return
    pasta = Path(workspace) / "citacoes"
    try:
        pasta.mkdir(parents=True, exist_ok=True)
        dados = {"localizador": processo, "id": id_, "cabecalho": b["cabecalho"], "tipo": b["tipo"],
                 "ementa": b["ementa"], "ids": b["ids"], "numeros": sorted(b["numeros"]),
                 "tokens": sorted(b["tokens"]), "classe": sorted(b["classe"]),
                 "origem": b["origem"], "ordem": list(b["ordem"]),
                 "capturado_em": datetime.datetime.now().isoformat(timespec="seconds")}
        (pasta / f"{_chave_cache(processo, id_)}.json").write_text(
            json.dumps(dados, ensure_ascii=False, indent=1), encoding="utf-8")
    except OSError:
        pass   # cache é conveniência; não pode derrubar a geração do .docx


def find_ementa(processo, transcript=None, workspace=None, id_=None) -> tuple[str | None, dict]:
    """(ementa, procedência) do julgado; (None, {}) se não achou."""
    num = None
    if processo:
        nums = _numeros(processo)
        num = max(nums, key=len) if nums else None
    classe = _classe(processo or "")
    if not (num or id_):
        raise LookupError(f"Localizador sem número nem id: {processo!r}")
    arquivos = arquivos_da_sessao(transcript)
    blocos = [b for s in _saidas_mcp(arquivos, explicito=bool(transcript)) for b in _blocos(s)]
    b = _escolher(blocos, processo or id_, num, classe, id_)
    if b:
        _cache_gravar(workspace, processo, id_, b)
        return b["ementa"], {**b, "via": b["tipo"], "arquivos_lidos": len(arquivos)}
    b = _cache_ler(workspace, processo, num, classe, id_)
    if b:
        return b["ementa"], {**b, "via": f"cache ({b['tipo']})", "arquivos_lidos": len(arquivos)}
    return None, {"arquivos_lidos": len(arquivos)}


# --------------------------------------------------------------- defeitos do conector
_TRUNCADA = re.compile(r"\[\s*(?:…|\.{3})?\s*ementa\s+truncada\b[^\]]*\]", re.IGNORECASE)
_ASPA_TROCADA = re.compile(r"(?:^|(?<=[\s(\[]))\?(?=[^\W\d_])")
_TRAVESSAO_TROCADO = re.compile(r"(?<=\s)\?(?=\s)")


def defeito(texto: str) -> str | None:
    if _TRUNCADA.search(texto):
        return "a ementa veio truncada pelo conector ([…ementa truncada…])"
    for rx, o_que in ((_ASPA_TROCADA, "aspa de abertura"), (_TRAVESSAO_TROCADO, "travessão ou aspa")):
        m = rx.search(texto)
        if m:
            ctx = texto[max(0, m.start() - 40): m.end() + 40]
            return f"há '?' no lugar de {o_que} (defeito de codificação do conector): …{ctx}…"
    return None


def _checar(texto: str, rotulo: str) -> None:
    d = defeito(texto)
    if d:
        raise ValueError(
            f"{rotulo}: {d}. Reabra o julgado pela ferramenta `*_detalhes_*` da base, com o ID "
            f"do resultado, e gere de novo. Se o defeito continuar, transcreva do inteiro teor "
            f"oficial em @citacao comum e passe pela verificacao-citacoes.")


# --------------------------------------------------------------- recorte / grifo
_ITEM_RE = re.compile(r"(?:(?<=^)|(?<=\s))(\d{1,3})\s*[.)\-–]\s+(?=[\"“'(]?[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", re.M)
_ROMANO_RE = re.compile(r"(?:(?<=^)|(?<=\s))([IVXL]{1,6})\s*[.)\-–]\s+(?=[\"“'(]?[A-ZÁÉÍÓÚÂÊÔÃÕÇ])", re.M)
_TITULO_ROMANO_FINAL = re.compile(r"\s+[IVX]{1,4}\.\s+(?:CASO EM EXAME|QUEST[ÃA]O EM DISCUSS[ÃA]O|"
                                  r"RAZ[ÕO]ES DE DECIDIR|DISPOSITIVO(?: E TESE)?)\s*$", re.IGNORECASE)


def _romano(s: str) -> int:
    val = {"I": 1, "V": 5, "X": 10, "L": 50}
    total = 0
    for k, c in enumerate(s):
        v = val[c]
        total += -v if k + 1 < len(s) and val[s[k + 1]] > v else v
    return total


def _sequencia(cands: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
    out, esperado = [], 1
    for c in cands:
        if c[2] == esperado:
            out.append(c)
            esperado += 1
    return out


def _split_itens(ementa: str) -> dict[int, str]:
    """{n: 'n. texto do item'} — itens numerados no início da linha ou na mesma linha
    (STF, TRF-1, TJPE), na ordem 1, 2, 3…; sem arábicos, I, II, III… (TRF-5)."""
    def em_inicio_de_linha(pos):
        return pos == 0 or ementa[:pos].rstrip(" \t").endswith("\n") or not ementa[:pos].strip()

    arabicos = [(m.start(), m.end(), int(m.group(1))) for m in _ITEM_RE.finditer(ementa)]
    seq = _sequencia([c for c in arabicos if em_inicio_de_linha(c[0])])
    if len(seq) < 2:
        seq = _sequencia(arabicos)
    if len(seq) < 2:
        romanos = [(m.start(), m.end(), _romano(m.group(1))) for m in _ROMANO_RE.finditer(ementa)]
        seq = _sequencia(romanos) if len(_sequencia(romanos)) >= 2 else seq
    itens = {}
    for k, (ini, _fim, n) in enumerate(seq):
        fim = seq[k + 1][0] if k + 1 < len(seq) else len(ementa)
        itens[n] = _TITULO_ROMANO_FINAL.sub("", ementa[ini:fim].rstrip())
    return itens


def _parse_range(s: str) -> list[int]:
    nums = []
    for parte in re.split(r"[,\s]+", s.strip()):
        if not parte:
            continue
        a, _, b = parte.partition("-")
        conv = (lambda x: _romano(x.upper()) if re.fullmatch(r"[IVXLivxl]+", x) else int(x))
        try:
            ia, ib = conv(a), conv(b) if b else conv(a)
        except (ValueError, KeyError):
            raise LookupError(f"itens inválidos: {s!r} (use 1, 1-2, 1,3 ou II-IV)")
        nums += list(range(ia, ib + 1))
    return nums


def _parse_trecho(s):
    m = re.search(r'de\s+"(.+?)"\s+at[eé]\s+"(.+?)"', s, re.IGNORECASE | re.DOTALL)
    if m:
        return m.group(1), m.group(2)
    if "|" in s:
        a, b = s.split("|", 1)
        return a.strip(), b.strip()
    return s.strip(), None


def _extract_span(texto, ini, fim, processo):
    """Fatia de `ini` até `fim` (inclusive). Âncora inicial repetida só é aceita se todas
    as ocorrências derem exatamente o mesmo texto (passagem repetida na peça)."""
    ini_n = collapse(ini)
    fim_n = collapse(fim) if fim else None
    posicoes = [m.start() for m in re.finditer(re.escape(ini_n), texto)] if ini_n else []
    if not posicoes:
        raise LookupError(f"Âncora inicial não encontrada em {processo}: {ini_n!r}")
    fatias = []
    for i in posicoes:
        if fim_n is None:
            fatias.append(texto[i:])
            continue
        j = texto.find(fim_n, i)
        if j >= 0:
            fatias.append(texto[i:j + len(fim_n)])
    if not fatias:
        raise LookupError(f"Âncora final não encontrada em {processo}: {fim_n!r}")
    if len(set(fatias)) > 1:
        raise LookupError(f"Âncora inicial AMBÍGUA em {processo}: {ini_n!r} aparece "
                          f"{len(posicoes)} vezes com textos diferentes (amplie a âncora)")
    return fatias[0]


def find_grifo(texto, grifo):
    g = collapse(grifo)
    i = texto.find(g)
    if i < 0:
        return None
    return (i, i + len(g))


def _recortar(texto_bruto: str, itens, trecho, rotulo: str) -> str:
    if itens:
        mapa = _split_itens(texto_bruto)
        nums = _parse_range(itens)
        faltando = [n for n in nums if n not in mapa]
        if faltando:
            dica = (" A ementa parece truncada: reabra pelo `*_detalhes_*`."
                    if _TRUNCADA.search(texto_bruto) else
                    f" Itens achados: {sorted(mapa) or 'nenhum'}; use `trecho:`.")
            raise LookupError(f"Itens {faltando} não encontrados em {rotulo}.{dica}")
        texto = " ".join(collapse(mapa[n]) for n in nums)
    else:
        texto = collapse(texto_bruto)
    if trecho:
        ini, fim = _parse_trecho(trecho)
        texto = _extract_span(texto, ini, fim, rotulo)
    return texto


def resolve(processo, itens=None, trecho=None, transcript=None, workspace=None, id_=None,
            detalhes=False):
    """Texto verbatim do julgado. Devolve (texto, origem) ou, com detalhes=True,
    (texto, procedência completa)."""
    rotulo = processo or f"id {id_}"
    ementa, prov = find_ementa(processo, transcript, workspace, id_)
    if ementa is None:
        raise LookupError(
            f"Ementa não encontrada para {rotulo!r} ({prov.get('arquivos_lidos', 0)} arquivo(s) da "
            f"sessão lidos, só saídas do conector). Rode a busca (e o `*_detalhes_*`) nesta sessão "
            f"antes de citar; para outra sessão, passe --transcript <arquivo ou pasta>.")
    texto = _recortar(ementa, itens, trecho, rotulo)
    _checar(texto, rotulo)
    return (texto, prov) if detalhes else (texto, prov.get("origem"))


# --------------------------------------------------------------- fonte: autos (workspace)
def _clean_autos(text):
    """Remove artefatos da extração do PJe: front matter, marcadores de página,
    cabeçalhos 'Documento id N - Tipo' e rodapés 'Num. N - Pág. N Assinado...'.
    Só mexe em ruído estrutural; não altera o texto jurídico."""
    text = re.sub(r"^\s*---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)  # front matter
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.DOTALL)                    # <!-- pág. N -->
    text = re.sub(r"Num\.\s*\d+\s*-\s*P[áa]g\.\s*\d+\s*Assinado eletronicamente por:[^\n]*",
                  " ", text)                                                     # rodapé
    text = re.sub(r"Documento id \d+ -\s*\w+", " ", text)                        # cabeçalho de página
    # rodapé de página do inteiro teor do STJ (pdftotext), que quebra a frase no meio
    text = re.sub(r"(?m)^\s*Documento:\s*\d+\s*-\s*Inteiro Teor.*$", " ", text)
    return text


def _find_doc(workspace, doc=None, arquivo=None):
    base = Path(workspace or ".").resolve()
    if arquivo:
        p = Path(arquivo)
        p = (p if p.is_absolute() else base / p).resolve()
        try:
            p.relative_to(base)
        except ValueError:
            raise LookupError(f"arquivo fora do workspace do processo: {arquivo}")
        return str(p)
    if doc is not None and workspace:
        hits = sorted(glob.glob(os.path.join(str(base), f"doc_{int(doc):03d}_*.md")))
        if hits:
            return hits[0]
    return None


def resolve_autos(workspace, doc=None, arquivo=None, itens=None, trecho=None):
    """Extrai texto VERBATIM de um documento dos autos (workspace do processo)."""
    if not workspace:
        raise LookupError("fonte: autos precisa do workspace do processo (--workspace <pasta>).")
    path = _find_doc(workspace, doc, arquivo)
    if not path or not os.path.exists(path):
        raise LookupError(
            f"Documento dos autos não encontrado (doc={doc}, arquivo={arquivo}) em {workspace}. "
            f"Extraia com processo.py extract ou passe --workspace <pasta do processo>.")
    with open(path, encoding="utf-8") as f:
        bruto = _clean_autos(f.read())
    texto = _recortar(bruto, itens, trecho, os.path.basename(path))
    return texto, path


# --------------------------------------------------------------- CLI
def main():
    import argparse
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Resolve @citacao-ref e imprime só o texto resolvido.")
    ap.add_argument("--fonte", default="", help="'autos' para ler do workspace; vazio = jurisprudência")
    ap.add_argument("--processo", help="localizador do julgado (classe e número)")
    ap.add_argument("--id", dest="id_", help="ID do resultado do conector")
    ap.add_argument("--doc")
    ap.add_argument("--arquivo")
    ap.add_argument("--workspace", help="pasta do processo (fonte: autos e cache de ementas)")
    ap.add_argument("--itens")
    ap.add_argument("--trecho")
    ap.add_argument("--grifo", action="append", default=[])
    ap.add_argument("--transcript", help="transcript (.jsonl) ou pasta de outra sessão")
    ap.add_argument("--json", action="store_true", help="texto + procedência em JSON")
    a = ap.parse_args()
    try:
        if a.fonte.lower() == "autos":
            texto, src = resolve_autos(a.workspace, doc=a.doc, arquivo=a.arquivo,
                                       itens=a.itens, trecho=a.trecho)
            prov = {"via": "autos", "origem": src}
        else:
            if not (a.processo or a.id_):
                ap.error("informe --processo ou --id (ou --fonte autos)")
            texto, prov = resolve(a.processo, itens=a.itens, trecho=a.trecho, transcript=a.transcript,
                                  workspace=a.workspace, id_=a.id_, detalhes=True)
        grifos = []
        for g in a.grifo:
            sp = find_grifo(texto, g)
            if sp is None:
                raise LookupError(f"grifo não encontrado no texto resolvido: {collapse(g)!r}")
            grifos.append(list(sp))
    except (LookupError, ValueError) as e:
        print(f"ERRO: {e}", file=sys.stderr)
        sys.exit(2)
    if a.json:
        print(json.dumps({"texto": texto, "via": prov.get("via"), "cabecalho": prov.get("cabecalho"),
                          "ids": prov.get("ids"), "origem": prov.get("origem"), "grifos": grifos},
                         ensure_ascii=False, indent=1))
    else:
        print(texto)
        print(f"[{prov.get('via')}] {prov.get('cabecalho') or ''} — {prov.get('origem')}",
              file=sys.stderr)


if __name__ == "__main__":
    main()
