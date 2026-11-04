#!/usr/bin/env python3
"""lint_peca.py — radar de estilo da escrita-juridica.

Lê peça ou relatório em markdown, ou em blocos @tag (formatacao-entrega), e aponta
arquivo:linha + regra para os padrões que a casa manda varrer:

  GO-2                travessão, meia-risca ou hífen com espaços usado como traço aditivo
  GO-4/paragrafo      parágrafo que passa da referência de palavras ou junta períodos demais
  GO-4/media          média de palavras por parágrafo fora da faixa-alvo (45 a 65)
  GO-4/aberturas      parágrafos seguidos com a mesma abertura (padrão: três)
  GO-1/abertura       parágrafos demais abertos sem conectivo (sujeito nominal, "O MPF",
                      ou demonstrativo, "Esse acórdão"): mais da metade ou três seguidos
  GO-1/remissao       remissão órfã: demonstrativo que retoma termo de dois ou mais
                      parágrafos atrás, ou que abre o capítulo apontando para o anterior
  GO-7/parafrase      parágrafo vizinho de citação que reconta o julgado ou repete as
                      palavras dela
  GO-7/repeticao      parágrafo que repete outro (conclusão anunciada e repetida)
  GO-7/precedente-narrado  precedente contado na prosa (o que o tribunal fez e por quê) em
                      vez de mostrado: apresentação de uma frase e trecho em bloco, com grifo
  GO-7/decisao-contraria   decisão invocada pela parte contrária transcrita em bloco, ou
                      decisões contrárias tratadas em três ou mais parágrafos
  GO-7/reformulacao   "ou seja", "vale dizer", "em outras palavras" mais de uma vez
  GO-5/ensaio         fórmula de crônica ou ensaio: avaliação impressionista, imagem,
                      contraste em suspense, dramatização, narrador comentando a peça
  GO-5/metadiscurso   arquitetura da tese exposta ("apenas para argumentar")
  GO-6                definição por negação ("não é X, mas Y"): alerta para triagem
  precisao/o-mesmo    "o mesmo"/"a mesma" como pronome
  persuasao/...       adjetivo de indignação; crítica dirigida ao julgador
  revisao/...         metalinguagem e enumeração-andaime
  cortesia/saturacao  latim ornamental, vênia ou bajulação repetidos
  padrao/vocativo     vocativo acima da dose (1 a 2 momentos decisivos)
  casa/lexico         léxico da casa ("impetração" → "ação"/"demanda")

É radar, não juiz: falso positivo é aceitável e a ausência de alerta não prova
qualidade. Cada alerta se confirma pelo teste da regra (references/revisao.md).
Ignora citação em bloco (@citacao, @citacao-ref, linhas "> "), trecho entre aspas,
código, tabelas e títulos.

Uso:
    python lint_peca.py peca.md [outra.md | pasta ...] [--json]
        [--max-palavras 120] [--limite-palavras 130] [--max-periodos 2] [--media 45-65]
        [--aberturas 3] [--max-abertura-nominal 30] [--max-nominais-seguidas 2]
        [--max-cortesia 2] [--ignorar GO-6,cortesia]

A régua do parágrafo é de ideia, não de número: um parágrafo diz uma coisa só,
normalmente em um ou dois períodos curtos. Os números só apontam onde olhar: média de
45 a 65 palavras por parágrafo na peça (consequência, nunca meta: não se alonga parágrafo
para chegar à faixa); 120 é referência de teto (125 ou 130 cabem se a ideia pede); acima
de 130, quase sempre há duas ideias.

Saída: uma linha por alerta (arquivo:linha: [regra] mensagem | trecho), a média de
palavras por parágrafo de cada arquivo e um resumo; com --json, um objeto
{"alertas": [...], "resumo": {...}, "paragrafos": {...}}. Código de saída 0 mesmo com
alertas; 2 se algum arquivo não puder ser lido.

Só biblioteca padrão.
"""

import argparse
import bisect
import glob
import json
import os
import re
import sys
import unicodedata
from dataclasses import asdict, dataclass, field


# ------------------------------------------------------------------ configuração
@dataclass
class Config:
    max_palavras: int = 120     # referência de teto: acima, confira se é uma ideia só
    limite_palavras: int = 130  # acima, o parágrafo quase sempre junta ideias
    max_periodos: int = 2       # o padrão é um ou dois períodos curtos
    periodos_a_partir: int = 90  # só parágrafo acima disso é cobrado pelos períodos
    media_min: int = 45         # faixa-alvo da média de palavras por parágrafo (versões
    media_max: int = 65         # definitivas do José, out. e nov./2026: 49 e 51)
    min_pars_media: int = 6     # com menos parágrafos de prosa (peça protocolar), sem média
    aberturas: int = 3
    max_abertura_nominal: int = 50   # % de parágrafos abertos sem conectivo (nominal ou
    max_nominais_seguidas: int = 2   # demonstrativo); a terceira seguida dispara
    max_cortesia: int = 2
    max_reformulacao: int = 1   # "ou seja" e afins: a segunda ocorrência dispara
    parafrase_min: float = 0.5  # parte do vocabulário do parágrafo que já está na citação
    repeticao_min: float = 0.75  # parte do vocabulário em comum com outro parágrafo
    ignorar: tuple = ()


@dataclass
class Alerta:
    arquivo: str
    linha: int
    regra: str
    mensagem: str
    trecho: str


# ------------------------------------------------------------------ segmentação
TAGS_CONHECIDAS = {
    "enderecamento", "identificacao", "titulo", "corpo", "secao",
    "citacao", "citacao-ref", "pedidos", "fecho", "data", "assinatura",
}
TAGS_TITULO = {"enderecamento", "identificacao", "titulo", "secao", "data", "assinatura"}
TAGS_ITENS = {"pedidos"}

RE_DIRETIVA = re.compile(r"^\s*@([a-z][a-z0-9-]*)\s*$", re.I)
RE_DIRETIVA_ARG = re.compile(r"^\s*@([a-z][a-z0-9-]*)\b", re.I)
RE_FENCE = re.compile(r"^\s*(```|~~~)")
RE_TITULO_MD = re.compile(r"^\s{0,3}#{1,6}(\s|$)")
RE_CITACAO_MD = re.compile(r"^\s*>")
RE_TABELA = re.compile(r"^\s*\|")
RE_REGUA = re.compile(r"^\s*([-*_])(\s*\1){2,}\s*$")
RE_COMENTARIO = re.compile(r"^\s*<!--.*-->\s*$")
RE_ITEM = re.compile(r"^\s*(?:[-*+•]|\d{1,3}[.)]|[a-z]\))\s+")


@dataclass
class Paragrafo:
    tipo: str                 # prosa | item | titulo | citacao
    linhas: list = field(default_factory=list)   # [(numero, texto)]
    texto: str = ""
    offsets: list = field(default_factory=list)

    def montar(self):
        partes, offs, pos = [], [], 0
        for _, t in self.linhas:
            t = t.strip()
            offs.append(pos)
            partes.append(t)
            pos += len(t) + 1
        self.texto = " ".join(partes)
        self.offsets = offs
        return self

    @property
    def inicio(self):
        return self.linhas[0][0] if self.linhas else 0

    def linha_de(self, pos):
        if not self.linhas:
            return 0
        i = bisect.bisect_right(self.offsets, pos) - 1
        return self.linhas[max(i, 0)][0]


def _tag_conhecida(linha):
    m = RE_DIRETIVA_ARG.match(linha)
    return bool(m) and m.group(1).lower() in TAGS_CONHECIDAS


def _diretiva(linha):
    m = RE_DIRETIVA.match(linha)
    if m:
        return m.group(1).lower()
    if _tag_conhecida(linha):
        return RE_DIRETIVA_ARG.match(linha).group(1).lower()
    return None


def _categoria(tag):
    if tag is None:
        return "md"
    if "citacao" in tag or "transcri" in tag:
        return "citacao"
    if tag in TAGS_TITULO:
        return "titulo"
    if tag in TAGS_ITENS:
        return "itens"
    return "prosa"


def segmentar(texto):
    """Divide o texto em parágrafos verificáveis e marcos (título, citação)."""
    linhas = texto.splitlines()
    modo_tag = any(_tag_conhecida(l) for l in linhas)
    saida = []
    atual = None
    tag = None
    em_fence = False
    em_frontmatter = bool(linhas) and linhas[0].strip() == "---" and not modo_tag

    def fechar():
        nonlocal atual
        if atual is not None and atual.linhas:
            saida.append(atual.montar())
        atual = None

    def marco(tipo, n, linha=""):
        """Citação ou título: blocos seguidos do mesmo tipo viram um marco só, que guarda
        o texto (a paráfrase e a remissão comparam com ele)."""
        fechar()
        if saida and saida[-1].tipo == tipo:
            if linha.strip():
                saida[-1].linhas.append((n, linha))
                saida[-1].montar()
            return
        saida.append(Paragrafo(tipo, [(n, linha)]).montar())

    for n, linha in enumerate(linhas, 1):
        if em_frontmatter:
            if n > 1 and linha.strip() in ("---", "..."):
                em_frontmatter = False
            continue
        if RE_FENCE.match(linha):
            fechar()
            em_fence = not em_fence
            continue
        if em_fence:
            continue
        if modo_tag:
            d = _diretiva(linha)
            if d:
                fechar()
                tag = d
                cat = _categoria(tag)
                if cat in ("titulo", "citacao"):
                    marco(cat, n)
                continue
        cat = _categoria(tag) if modo_tag else "md"
        if cat in ("titulo", "citacao"):
            marco(cat, n, linha)
            continue
        if not linha.strip():
            fechar()
            continue
        if RE_CITACAO_MD.match(linha):
            marco("citacao", n, re.sub(r"^\s*>\s?", "", linha))
            continue
        if RE_TITULO_MD.match(linha):
            marco("titulo", n, re.sub(r"^\s{0,3}#{1,6}\s*", "", linha))
            continue
        if RE_TABELA.match(linha) or RE_REGUA.match(linha) or RE_COMENTARIO.match(linha):
            fechar()
            continue
        if RE_ITEM.match(linha):
            fechar()
            atual = Paragrafo("item", [(n, RE_ITEM.sub("", linha, count=1))])
            continue
        if atual is None:
            atual = Paragrafo("item" if cat == "itens" else "prosa")
        atual.linhas.append((n, linha))
    fechar()
    return saida


# ------------------------------------------------------------------ utilidades
def mascarar(texto):
    """Troca por espaços o que está entre aspas e em código inline (mantém posições)."""
    chars = list(texto)

    def apagar(i, j):
        for k in range(i, j + 1):
            chars[k] = " "

    for abre, fecha in (("“", "”"), ("«", "»")):
        i = 0
        while True:
            a = texto.find(abre, i)
            if a < 0:
                break
            f = texto.find(fecha, a + 1)
            if f < 0:
                break
            apagar(a, f)
            i = f + 1
    retas = [m.start() for m in re.finditer('"', texto)]
    for a, f in zip(retas[0::2], retas[1::2]):
        apagar(a, f)
    for m in re.finditer(r"`[^`]*`", texto):
        apagar(m.start(), m.end() - 1)
    return "".join(chars)


def _trecho(texto, a, b, folga=30):
    ini, fim = max(0, a - folga), min(len(texto), b + folga)
    s = re.sub(r"\s+", " ", texto[ini:fim]).strip()
    return ("…" if ini > 0 else "") + s + ("…" if fim < len(texto) else "")


RE_ABREV = re.compile(
    r"\b(Rel|Min|Des|Dr|Dra|Sr|Sra|Exmos?|Exmas?|exmos?|exmas?|Exa|Ex|Ilmos?|Ilmas?|Profa?|Cf|cf|"
    r"V|v|Id|id|Ib|ib|n|art|arts|inc|incs|fls?|pp?|ss|al|Ltda|S\.A|eg|Eg|Docs?|c)\."
)


def contar_periodos(texto):
    t = RE_ABREV.sub(lambda m: m.group(0)[:-1] + "§", texto.strip())
    partes = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\"“(])", t)
    return len([p for p in partes if p.strip()])


# ------------------------------------------------------------------ GO-2: traço
RE_TRAVESSAO = re.compile(r"[—―]")
RE_MEIA_RISCA = re.compile(r"[–‒]")
RE_HIFEN_SOLTO = re.compile(r"(?<=\S)[ \t]+-{1,2}[ \t]+(?=\S)")
RE_HIFEN_DUPLO = re.compile(r"(?<=\w)--(?=\w)")
MSG_TRACO = "traço aditivo: troque por vírgulas"


def _entre_digitos(s, a, b):
    antes = s[:a].rstrip()
    depois = s[b:].lstrip()
    return bool(antes) and bool(depois) and antes[-1].isdigit() and depois[0].isdigit()


def checar_traco(par, masc):
    for rx, pular_digitos in ((RE_TRAVESSAO, False), (RE_MEIA_RISCA, True),
                              (RE_HIFEN_SOLTO, True), (RE_HIFEN_DUPLO, False)):
        for m in rx.finditer(masc):
            if pular_digitos and _entre_digitos(masc, m.start(), m.end()):
                continue
            yield m.start(), "GO-2", MSG_TRACO, _trecho(par.texto, m.start(), m.end())


# ------------------------------------------------------------------ GO-4
def checar_paragrafo(par, cfg):
    palavras = len(par.texto.split())
    periodos = contar_periodos(par.texto)
    if palavras > cfg.limite_palavras:
        msg = (f"parágrafo de {palavras} palavras e {periodos} período(s): passa bem da "
               f"referência de {cfg.max_palavras} e quase sempre junta mais de uma ideia; "
               f"ache a costura lógica e quebre, sem resumir")
    elif palavras > cfg.max_palavras:
        msg = (f"parágrafo de {palavras} palavras: acima da referência de {cfg.max_palavras}. "
               f"Mantenha se for uma ideia só que precisa desse espaço; se houver duas, quebre "
               f"na costura")
    elif periodos > cfg.max_periodos and palavras > cfg.periodos_a_partir:
        msg = (f"parágrafo de {palavras} palavras em {periodos} períodos: o padrão é uma ideia "
               f"em um ou dois períodos curtos; confira se não há duas ideias")
    else:
        return
    yield 0, "GO-4/paragrafo", msg, _trecho(par.texto, 0, 60, folga=0)


def estatisticas(pars):
    """Tamanho dos parágrafos de prosa (sem itens, títulos e citações)."""
    prosa = [p for p in pars if p.tipo == "prosa"]
    sem_apresentacao = [p for i, p in enumerate(pars)
                        if p.tipo == "prosa" and not apresenta_citacao(pars, i)]
    tamanhos = [len(p.texto.split()) for p in prosa]
    if not tamanhos:
        return {"paragrafos": 0, "media_palavras": 0.0, "maior": 0, "aberturas_nominais_pct": 0,
                "aberturas_sem_conectivo_pct": 0}
    nominais = sum(1 for p in prosa if abre_com_sujeito_nominal(p.texto))
    sem_conectivo = sum(1 for p in sem_apresentacao if abertura_sem_conectivo(p.texto))
    return {"paragrafos": len(tamanhos),
            "media_palavras": round(sum(tamanhos) / len(tamanhos), 1),
            "maior": max(tamanhos),
            "aberturas_nominais_pct": round(100 * nominais / len(prosa)),
            "aberturas_sem_conectivo_pct": round(100 * sem_conectivo
                                                 / max(len(sem_apresentacao), 1))}


def checar_media(pars, cfg, arquivo):
    prosa = [p for p in pars if p.tipo == "prosa"]
    if len(prosa) < cfg.min_pars_media:
        return
    est = estatisticas(pars)
    media = est["media_palavras"]
    if cfg.media_min <= media <= cfg.media_max:
        return
    faixa = f"faixa-alvo de {cfg.media_min} a {cfg.media_max}"
    if media > cfg.media_max:
        maiores = sorted(prosa, key=lambda p: -len(p.texto.split()))[:3]
        onde = ", ".join(str(l) for l in sorted(p.linha_de(0) for p in maiores))
        msg = (f"média de {media:.0f} palavras por parágrafo em {est['paragrafos']} "
               f"parágrafos, acima da {faixa}: há parágrafos juntando ideias (os maiores "
               f"começam nas linhas {onde})")
    else:
        msg = (f"média de {media:.0f} palavras por parágrafo em {est['paragrafos']} "
               f"parágrafos, abaixo da {faixa}: confira se há frases soltas em série, sem "
               f"conjunção que as ligue; não alongue parágrafo para atingir a faixa")
    yield Alerta(arquivo, prosa[0].linha_de(0), "GO-4/media", msg,
                 _trecho(prosa[0].texto, 0, 60, folga=0))


CONECTIVOS = sorted({
    "com efeito", "além disso", "ademais", "outrossim", "por sua vez", "nessa linha",
    "nesse sentido", "nesse contexto", "nesse passo", "desse modo", "dessa forma",
    "dessa maneira", "dessa feita", "assim sendo", "assim", "portanto", "logo",
    "por isso", "por conseguinte", "em consequência", "consequentemente", "contudo",
    "todavia", "entretanto", "no entanto", "porém", "ocorre que", "sucede que",
    "de fato", "ora", "cabe acrescentar", "importa notar", "importante frisar",
    "destaca-se", "ressalte-se", "registre-se", "note-se", "observe-se", "veja-se",
    "por fim", "finalmente", "em suma", "em síntese", "com isso", "não bastasse",
    "não obstante", "inclusive", "ainda", "também", "trata-se", "no caso",
    "na hipótese", "no ponto", "quanto ao", "quanto à", "quanto a", "a propósito",
    "em primeiro lugar", "em segundo lugar", "primeiro", "segundo", "terceiro",
    "ou seja", "isto é", "nesse ponto", "neste ponto", "aliás", "mais",
}, key=len, reverse=True)


def abertura(texto):
    t = re.sub(r"^[^\w]+", "", texto.strip().lower())
    for c in CONECTIVOS:
        if t.startswith(c) and (len(t) == len(c) or not t[len(c)].isalnum()):
            return c
    palavras = re.findall(r"\w+(?:-\w+)*", t)
    return " ".join(palavras[:2])


def checar_aberturas(pars, cfg, arquivo):
    run, chave, avisado = [], None, False
    for p in pars:
        if p.tipo == "titulo":
            run, chave, avisado = [], None, False
            continue
        if p.tipo != "prosa":
            continue
        k = abertura(p.texto)
        if not k:
            run, chave, avisado = [], None, False
            continue
        if k == chave:
            run.append(p)
        else:
            run, chave, avisado = [p], k, False
        if len(run) >= cfg.aberturas and not avisado:
            avisado = True
            linhas = ", ".join(str(x.inicio) for x in run)
            yield Alerta(arquivo, p.inicio, "GO-4/aberturas",
                         f"{len(run)} parágrafos seguidos abrem com \"{k}\" (linhas {linhas}): "
                         f"varie a abertura", _trecho(p.texto, 0, 50, folga=0))


# ------------------------------------------------------------------ GO-1: ligação
ARTIGOS = {"o", "a", "os", "as", "um", "uma", "uns", "umas"}
# palavra que, logo depois do artigo, faz da abertura uma locução ("A partir disso", "Uma
# vez que", "A meu ver"), uma retomada ("A essa altura", "O mesmo acórdão") ou uma relativa
# ("O que se discute"), e não um sujeito nominal seco
LOCUCAO_APOS_ARTIGO = {
    "partir", "despeito", "propósito", "proposito", "respeito", "fim", "par", "teor",
    "título", "titulo", "seguir", "exemplo", "vez", "rigor", "princípio", "principio",
    "meu", "nosso", "seu", "cada", "contar", "depender", "todo", "toda", "qualquer", "luz",
    "esse", "essa", "este", "esta", "isso", "isto", "tal", "tais", "aquele", "aquela",
    "mesmo", "mesma", "mesmos", "mesmas", "que", "qual", "quem",
}
MAX_ALERTAS_SEQUENCIA = 5


def abre_com_sujeito_nominal(texto):
    """True se o parágrafo abre com artigo + substantivo ("O MPF", "A sentença"), sem
    conectivo, circunstância ou retomada antes."""
    palavras = re.findall(r"\w+(?:-\w+)*", texto.strip()[:80])
    if len(palavras) < 2:
        return False
    return palavras[0].lower() in ARTIGOS and palavras[1].lower() not in LOCUCAO_APOS_ARTIGO


RE_ABRE_DEMONSTRATIVO = re.compile(r"^(?:est|ess|aquel)(?:e|a|es|as)\b|^(?:tal|tais)\b", re.I)
POSPOSTOS = [
    "contudo", "todavia", "portanto", "assim", "por isso", "pois", "entretanto", "no entanto",
    "porém", "por sua vez", "aliás", "ademais", "de fato", "com efeito", "então", "logo",
    "outrossim", "igualmente", "também", "ainda", "por conseguinte", "consequentemente",
    "dessa forma", "desse modo", "nesse sentido", "por outro lado", "de outro lado",
    "ao contrário", "inclusive", "sobretudo", "em consequência", "ademais disso",
]
RE_CONECTIVO_POSPOSTO = re.compile(
    r"^[^.;:!?]{1,80}?,\s*(?:" + "|".join(re.escape(c) for c in POSPOSTOS) + r")\s*,", re.I)


def abertura_sem_conectivo(texto):
    """"nominal" ("O MPF imputou"), "demonstrativo" ("Esse acórdão", "Essa lógica") ou None
    (abre pela conjunção, anteposta ou logo depois do primeiro termo, ou por circunstância)."""
    t = re.sub(r"^[^\w]+", "", mascarar(texto).strip())
    if RE_CONECTIVO_POSPOSTO.match(t):
        return None
    if RE_ABRE_DEMONSTRATIVO.match(t):
        return "demonstrativo"
    if abre_com_sujeito_nominal(texto):
        return "nominal"
    return None


def apresenta_citacao(pars, i):
    """A frase que apresenta a citação seguinte ("O STJ já enfrentou a questão…:")."""
    p = pars[i]
    return (p.tipo == "prosa" and i + 1 < len(pars) and pars[i + 1].tipo == "citacao"
            and p.texto.rstrip().endswith(":") and contar_periodos(p.texto) <= 2)


def checar_abertura(pars, cfg, arquivo):
    """Aberturas sem conectivo. A frase que apresenta a citação não conta, e a citação
    reinicia a sequência: o parágrafo seguinte a ela retoma a própria citação."""
    prosa = [p for i, p in enumerate(pars) if p.tipo == "prosa" and not apresenta_citacao(pars, i)]
    if len(prosa) < cfg.min_pars_media:
        return
    sequencias, run = [], []
    for i, p in enumerate(pars):
        if p.tipo in ("titulo", "citacao"):
            run = []
            continue
        if p.tipo != "prosa" or apresenta_citacao(pars, i):
            continue
        if abertura_sem_conectivo(p.texto):
            run.append(p)
            if len(run) == cfg.max_nominais_seguidas + 1:
                sequencias.append(run)
        else:
            run = []
    for run in sequencias[:MAX_ALERTAS_SEQUENCIA]:
        p = run[cfg.max_nominais_seguidas]
        linhas = ", ".join(str(x.inicio) for x in run)
        yield Alerta(arquivo, p.inicio, "GO-1/abertura",
                     f"{len(run)} parágrafos seguidos abrem sem conectivo (linhas {linhas}): "
                     f"abra pela conjunção da relação lógica com o anterior (Ademais, Portanto, "
                     f"Todavia…), anteposta ou logo depois do primeiro termo",
                     _trecho(p.texto, 0, 50, folga=0))
    sem = [p for p in prosa if abertura_sem_conectivo(p.texto)]
    teto = int(cfg.max_abertura_nominal * len(prosa) / 100 + 0.5)   # "cerca de": arredonda
    if len(sem) > teto:
        contagem = {}
        for p in sem:
            k = " ".join(re.findall(r"\w+(?:-\w+)*", p.texto.strip())[:2])
            contagem[k] = contagem.get(k, 0) + 1
        repetidas = sorted(contagem.items(), key=lambda kv: -kv[1])[:3]
        mais = ", ".join(f"\"{k}\" ({n})" for k, n in repetidas)
        extra = (f"; {len(sequencias)} sequência(s) de {cfg.max_nominais_seguidas + 1} ou mais"
                 if sequencias else "")
        pct = 100 * len(sem) / len(prosa)
        demonstrativos = sum(1 for p in sem if abertura_sem_conectivo(p.texto) == "demonstrativo")
        yield Alerta(arquivo, sem[0].inicio, "GO-1/abertura",
                     f"{len(sem)} de {len(prosa)} parágrafos ({pct:.0f}%) abrem sem conectivo "
                     f"({demonstrativos} por demonstrativo), acima do teto de cerca de "
                     f"{cfg.max_abertura_nominal}%{extra}: na maioria das vezes, a abertura vem "
                     f"pela conjunção da relação lógica (Ademais, Portanto, Todavia…). Mais "
                     f"repetidas: {mais}. Sujeito nominal fica quando nomeia o passo novo do "
                     f"argumento; trocar o artigo por demonstrativo não liga nada",
                     _trecho(sem[0].texto, 0, 50, folga=0))


# ------------------------------------------------------------------ GO-1: remissão à vista
def _sem_acento(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn").lower()


RE_DEMONSTRATIVO = re.compile(
    r"\b(?:n|d)?(?:est|ess|aquel)(?:e|a|es|as)\s+(?:mesm[oa]s?\s+)?(\w+(?:-\w+)?)"
    r"|\bàquel(?:e|a|es|as)\s+(?:mesm[oa]s?\s+)?(\w+(?:-\w+)?)"
    r"|\b(?:tal|tais)\s+(\w+(?:-\w+)?)", re.I)
# remete à situação do próprio processo ou é locução fixa, não a um termo anterior
DEITICOS = set(_sem_acento(w) for w in """
processo processos acao acoes autos feito writ lide demanda peca peticao manifestacao memorial
recurso agravo apelacao embargos mandado juizo tribunal corte turma camara secao plenario
pleno instancia grau sede colegiado julgamento sessao pauta ano mes data momento oportunidade
ocasiao ato caso ponto sentido modo forma maneira linha passo feita termos particular fase
etapa eg egregio egregia colendo colenda excelencia excelentissimo excelentissimos relator
relatora como qual quais sorte medida que quanto parte
""".split())
NAO_NOME = set(_sem_acento(w) for w in """
e é foi era sao são sera seria seja sejam fosse estava esta está estao ultimo ultima ultimos
ultimas primeiro primeira outro outra outros outras ja nao sim tambem ainda apenas so
""".split())
RE_NOMEIA = re.compile(r"^\s*,\s*(?:que|qual seja|quais sejam|isto é|ou seja|a saber"
                       r"|segundo o qual|segundo a qual|pel[oa] qual|de que)\b", re.I)


def _radical_nome(nome):
    n = _sem_acento(nome)
    return n[:6] if len(n) >= 7 else n[:-1] if len(n) >= 5 else n


def _contem(radical, texto):
    return re.search(r"\b" + re.escape(radical), _sem_acento(texto)) is not None


def _fim_do_primeiro_periodo(texto):
    t = RE_ABREV.sub(lambda m: m.group(0)[:-1] + "§", texto)
    m = re.search(r"[.!?](?=\s+[A-ZÀ-Ý\"“(])", t)
    return m.end() if m else len(texto)


def checar_remissao(pars, cfg, arquivo):
    """Remissão órfã. A que retoma o que acabou de ser dito, para construir o passo
    seguinte ("Nessa perspectiva, …"; "O decreto confirmou esse quadro."), fica: o vício é
    o referente longe da vista (parágrafos atrás, outro capítulo)."""
    prosa_idx = [i for i, p in enumerate(pars) if p.tipo in ("prosa", "item")]
    for k, i in enumerate(prosa_idx):
        p = pars[i]
        if p.tipo != "prosa":
            continue
        anterior = prosa_idx[k - 1] if k > 0 else -1
        entre = pars[anterior + 1:i]
        titulos = [b for b in entre if b.tipo == "titulo"]
        citacoes = [b for b in entre if b.tipo == "citacao"]
        masc = mascarar(p.texto)
        abertura_fim = _fim_do_primeiro_periodo(masc)
        for m in RE_DEMONSTRATIVO.finditer(masc):
            nome = m.group(1) or m.group(2) or m.group(3) or ""
            n = _sem_acento(nome)
            if len(n) < 3 or n in DEITICOS or n in NAO_NOME:
                continue
            if RE_NOMEIA.match(masc[m.end():]):
                continue
            rad = _radical_nome(nome)
            na_abertura = m.start() < abertura_fim
            if _contem(rad, p.texto[:m.start()]):
                continue
            expr = re.sub(r"\s+", " ", p.texto[m.start():m.end()])
            if titulos and na_abertura and not any(_contem(rad, t.texto) for t in titulos):
                yield Alerta(arquivo, p.linha_de(m.start()), "GO-1/remissao",
                             f"\"{expr}\" abre o capítulo apontando para o anterior: abra pela "
                             f"própria tese e, se preciso, repita o termo exato",
                             _trecho(p.texto, m.start(), m.end()))
                continue
            if (anterior >= 0 and _contem(rad, pars[anterior].texto)) \
                    or any(_contem(rad, c.texto) for c in citacoes) \
                    or any(_contem(rad, t.texto) for t in titulos):
                continue
            distancia = None
            for d, j in enumerate(reversed(prosa_idx[:max(k - 1, 0)]), start=2):
                if _contem(rad, pars[j].texto):
                    distancia = d
                    break
            if distancia:
                yield Alerta(arquivo, p.linha_de(m.start()), "GO-1/remissao",
                             f"\"{expr}\" retoma termo que só aparece {distancia} parágrafos "
                             f"atrás: repita o termo exato ou nomeie o referente na frase "
                             f"(\"Essa ratio, que afastou…\")",
                             _trecho(p.texto, m.start(), m.end()))


# ------------------------------------------------------------------ GO-7: dizer uma vez
STOP_CONTEUDO = set(_sem_acento(w) for w in """
sobre entre quando porque assim ainda tambem apenas mesmo mesma mesmos mesmas outro outra
outros outras todos todas qualquer quaisquer sendo tendo havia houve forma modo termos sentido
pelos pelas desse dessa deste desta nesse nessa neste nesta aquele aquela caput inciso incisos
paragrafo unico alinea artigo artigos tribunal tribunais superior supremo federal justica
turma secao camara relator relatora ministro ministra desembargador desembargadora recurso
especial extraordinario agravo interno regimental embargos declaracao apelacao acordao
acordaos julgamento julgado julgados regiao primeira segunda terceira quarta quinta sexta
corte pleno plenario processo processos civil decisao decisoes
""".split())
RE_ABRE_PARAFRASE = re.compile(
    r"^\W*(?:como se (?:vê|ve|observa|nota|percebe|depreende|extrai|verifica|infere|constata)"
    r"|depreende-se|extrai-se|infere-se|vê-se|observa-se|percebe-se|nota-se|verifica-se"
    r"|constata-se|nesse (?:julgado|precedente|acórdão|aresto|caso|feito)"
    r"|neste (?:julgado|precedente|acórdão|aresto)"
    r"|naquel[ea] (?:julgado|precedente|acórdão|aresto|caso|ocasião|feito|oportunidade)"
    r"|na(?:quela)? ocasião|naquela oportunidade"
    r"|n[oa] (?:referid|citad|mencionad|aludid|transcrit)[oa] (?:julgado|precedente|acórdão"
    r"|aresto|caso|decisão|ementa)"
    r"|n[oa] (?:julgado|precedente|acórdão|aresto|decisão|ementa) (?:acima|transcrit[oa]"
    r"|citad[oa]|em destaque))\b", re.I)
RE_SUJEITO_CORTE = re.compile(
    r"^\W*(?:(?:o|a|os|as)\s+)?(?:(?:e?g\.|egr[eé]gi[oa]|colend[oa]|c\.)\s+)?(?:STJ|STF|TST|TSE"
    r"|TCU|CARF|TRF\S*|TJ\w*|Superior Tribunal|Supremo Tribunal|Tribunal|Corte|Turma|Seção"
    r"|Câmara|Plenário|Pleno|Órgão Especial|Primeira|Segunda|Terceira|Quarta|Quinta|Sexta"
    r"|acórdão|julgado|precedente|aresto|relator|relatora|ministr[oa]|desembargador[a]?)\b",
    re.I)
RE_VERBO_DECISAO = re.compile(
    r"\b(?:decidiu|decide|decidem|decidiram|entendeu|entende|entenderam|assentou|assenta"
    r"|assentaram|reconheceu|reconhece|firmou|fixou|concluiu|afastou|consignou|registrou"
    r"|rejeitou|acolheu|negou|manteve|aplicou|adotou|enfrentou|julgou|reafirmou|situou"
    r"|resumiu|destacou|ressaltou|asseverou|pontuou|esclareceu|considerou|explicitou"
    r"|deixou claro|foi claro)\b", re.I)
RE_ANCORA_CASO = re.compile(
    r"\b(?:Impetrante|Impetrad[oa]|Agravante|Agravad[oa]|Recorrente|Recorrid[oa]|Apelante"
    r"|Apelad[oa]|Embargante|Embargad[oa]|Autora?|Réu|Ré|Requerente|Requerid[oa]|Executad[oa]"
    r"|Exequente|Reclamante|Reclamad[oa]|Consulente|cliente|autos|Docs?\.|fls?\.|inicial"
    r"|contrarrazões|informações|in casu|caso concreto|caso dos autos)\b|\bid\s*\d", re.I)
RE_CHAVE_REF = re.compile(r"^\s*(fonte|processo|id|itens|trecho|grifo|ref|doc|arquivo)\s*:\s*(.*)$",
                          re.I)


def radicais(texto):
    """Vocabulário de conteúdo: palavras de cinco letras ou mais, sem as de função e as de
    tribunal, reduzidas a seis letras."""
    out = set()
    for w in re.findall(r"[^\W\d_]{5,}", texto):
        n = _sem_acento(w)
        if n not in STOP_CONTEUDO:
            out.add(n[:6])
    return out


def texto_da_citacao(par):
    """Texto visível da citação: o bloco transcrito ou, no @citacao-ref, o grifo e o trecho."""
    linhas = [t for _, t in par.linhas if t.strip() and not RE_DIRETIVA_ARG.match(t)]
    chaves = [RE_CHAVE_REF.match(t) for t in linhas]
    if any(chaves):
        return " ".join(m.group(2) for m in chaves
                        if m and m.group(1).lower() in ("grifo", "trecho"))
    return " ".join(linhas)


def checar_parafrase(pars, cfg, arquivo):
    for i, p in enumerate(pars):
        if p.tipo != "prosa":
            continue
        vizinhas = [pars[j] for j in (i - 1, i + 1) if 0 <= j < len(pars)
                    and pars[j].tipo == "citacao"]
        if not vizinhas:
            continue
        texto = p.texto.strip()
        antes_da_citacao = i + 1 < len(pars) and pars[i + 1].tipo == "citacao"
        if antes_da_citacao and texto.endswith(":") and contar_periodos(texto) <= 2:
            continue   # a frase que apresenta a citação fica
        narra = bool(RE_ABRE_PARAFRASE.match(texto)
                     or (RE_SUJEITO_CORTE.match(texto) and RE_VERBO_DECISAO.search(texto)))
        narra = narra and not RE_ANCORA_CASO.search(texto)
        P = radicais(texto)
        Q = set().union(*(radicais(texto_da_citacao(v)) for v in vizinhas))
        parte = len(P & Q) / len(P) if P else 0.0
        repete = len(P) >= 8 and parte >= cfg.parafrase_min
        if not (narra or repete):
            continue
        motivo = ("reconta o julgado" if narra else
                  f"repete {parte:.0%} do vocabulário da citação vizinha")
        yield Alerta(arquivo, p.inicio, "GO-7/parafrase",
                     f"parágrafo vizinho de citação que {motivo}: em volta da citação fica só o "
                     f"que ela não mostra (a aplicação ao caso ou o arremate); o grifo já faz a "
                     f"leitura dirigida", _trecho(p.texto, 0, 60, folga=0))


RE_REF_PRECEDENTE = re.compile(
    r"\((?:STJ|STF|TST|TSE|TCU|CARF|TRF-?\d|TJ[A-Z]{2})\b"
    r"|\b(?:REsp|AREsp|EREsp|AgInt|AgRg|EDcl|RE|ARE|AI|RMS|MS|MI|ADI|ADC|ADPF|AMS|REOMS|Rcl)"
    r"\s+(?:(?:no|na|nos|nas)\s+\w+\s+)?\d")
RE_CORTE_DECIDE = re.compile(
    r"\b(?:o|a)\s+(?:mesm[oa]\s+)?(?:STJ|STF|TST|TCU|CARF|TRF\S*|Superior Tribunal de Justiça"
    r"|Supremo Tribunal Federal|Tribunal|Corte|(?:Primeira|Segunda|Terceira|Quarta|\d+ª)\s+"
    r"(?:Turma|Seção)|Turma|Seção|Plenário|Pleno)\b[^.;]{0,120}?\b(?:decidiu|entendeu|assentou"
    r"|reconheceu|firmou|fixou|concluiu|afastou|cassou|anulou|reformou|declarou|aplicou|admitiu"
    r"|rejeitou|acolheu|negou|manteve|julgou)\b", re.I)
RE_PORQUE_DO_JULGADO = re.compile(
    r"\bpor (?:reconhecer|entender|considerar|concluir)\b|\bao (?:fundamento|argumento) de que\b"
    r"|\bsob o fundamento\b|\bpel[oa] qual\b|\bporque (?:entendeu|reconheceu|considerou)\b"
    r"|\bpor ter (?:reconhecido|entendido|considerado)\b", re.I)
FONTE_ADVERSARIA = (
    r"(?:transcrit[oa]s?|invocad[oa]s?|trazid[oa]s?|citad[oa]s?|colacionad[oa]s?)\s+"
    r"(?:pel[oa]s?|n[oa]s?)\s+(?:própri[oa]s?\s+)?(?:informações|autoridade|União|Fazenda"
    r"|contestação|contrarrazões|razões|ré\b|réu\b|recorrente|recorrid[oa]|agravad[oa]|apelad[oa]"
    r"|parte contrária|adversári[oa])"
    r"|que (?:as|a|o) (?:informações|contestação|contrarrazões|autoridade|ré|réu|recorrente"
    r"|parte contrária) (?:transcrevem|transcreve|invocam|invoca|trazem|traz|cita|citam)"
    r"|d[ao]s? (?:informações|contestação|contrarrazões)\b")
RE_CITACAO_ADVERSARIA = re.compile(FONTE_ADVERSARIA, re.I)
RE_DECISOES_ADVERSAS = re.compile(
    r"\b(?:sentenças?|decisões|decisão|julgados?|precedentes?|acórdãos?|arestos?)\b[^.;]{0,60}?"
    r"(?:" + FONTE_ADVERSARIA + r")", re.I)


def _periodos_com_posicao(texto):
    t = RE_ABREV.sub(lambda m: m.group(0)[:-1] + "§", texto)
    ini = 0
    for m in re.finditer(r"(?<=[.!?])\s+(?=[A-ZÀ-Ý\"“(])", t):
        yield ini, texto[ini:m.start()]
        ini = m.end()
    if ini < len(texto):
        yield ini, texto[ini:]


def checar_precedente_narrado(pars, cfg, arquivo):
    """Precedente contado na prosa ("o STJ cassou acórdão…, por reconhecer que…") em vez de
    mostrado. A corroboração curta ("…, como assentou o STJ (REsp X)") e o trecho literal entre
    aspas na própria frase ficam."""
    for p in pars:
        if p.tipo != "prosa":
            continue
        for ini, frase in _periodos_com_posicao(p.texto):
            if any(c in frase for c in "\"“”"):
                continue
            if RE_REF_PRECEDENTE.search(frase) and RE_CORTE_DECIDE.search(frase) \
                    and RE_PORQUE_DO_JULGADO.search(frase):
                yield Alerta(arquivo, p.linha_de(ini), "GO-7/precedente-narrado",
                             "precedente contado na prosa (o que o tribunal fez e por quê): "
                             "mostre-o, com uma frase de apresentação e o trecho em bloco, com "
                             "grifo no que decide; na prosa, só a corroboração curta",
                             _trecho(p.texto, ini, ini + 60, folga=0))


def checar_decisao_contraria(pars, cfg, arquivo):
    """Decisões que a parte contrária invoca: a casa responde em conjunto, sem transcrevê-las."""
    for p in pars:
        if p.tipo == "citacao" and RE_CITACAO_ADVERSARIA.search(p.texto):
            yield Alerta(arquivo, p.inicio, "GO-7/decisao-contraria",
                         "transcrição de decisão invocada pela parte contrária: responda às "
                         "decisões contrárias em conjunto, numa oração, sem transcrevê-las; o "
                         "bloco de citação fica para o precedente favorável",
                         _trecho(p.texto.strip(), 0, 60, folga=0))
    adversas = [p for p in pars if p.tipo == "prosa" and RE_DECISOES_ADVERSAS.search(p.texto)]
    if len(adversas) >= 3:
        linhas = ", ".join(str(p.inicio) for p in adversas[:8])
        yield Alerta(arquivo, adversas[2].inicio, "GO-7/decisao-contraria",
                     f"decisões invocadas pela parte contrária tratadas em {len(adversas)} "
                     f"parágrafos (linhas {linhas}): responda em conjunto, num parágrafo, pelo que "
                     f"as desqualifica como bloco (grau, data, o que decidiram em uma linha) e "
                     f"pelos pronunciamentos favoráveis",
                     _trecho(adversas[2].texto, 0, 60, folga=0))


def checar_repeticao(pars, cfg, arquivo):
    prosa = [p for p in pars if p.tipo == "prosa"]
    rad = [radicais(p.texto) for p in prosa]
    alertas = 0
    for b in range(len(prosa)):
        if len(rad[b]) < 10:
            continue
        for a in range(b - 1):   # só parágrafos não vizinhos
            if len(rad[a]) < 10:
                continue
            comum = len(rad[a] & rad[b]) / min(len(rad[a]), len(rad[b]))
            if comum >= cfg.repeticao_min:
                yield Alerta(arquivo, prosa[b].inicio, "GO-7/repeticao",
                             f"repete o parágrafo da linha {prosa[a].inicio} ({comum:.0%} do "
                             f"vocabulário em comum): diga uma vez; a conclusão vem no fim do "
                             f"tópico, sem anúncio na abertura nem reprise adiante",
                             _trecho(prosa[b].texto, 0, 60, folga=0))
                alertas += 1
                break
        if alertas >= MAX_ALERTAS_SEQUENCIA:
            return


# ------------------------------------------------------------------ léxico
LEXICO = [
    # GO-5: avaliação impressionista do próprio argumento
    ("GO-5/ensaio", r"\bmelhor revela\b|\bsalta(?:m)? aos olhos\b|\b(?:se )?(?:sustenta|para)m? de pé\b"
     r"|\bcontraste é eloquente\b|\bmais simples do que parece\b",
     "registro ensaístico: nomeie o objeto processual e a operação jurídica"),
    # GO-5: contraste retórico em suspense e dramatização por reforço
    ("GO-5/ensaio", r"\buma coisa (?:seria|é|era)\b|\boutra,? bem diferente\b|\bnão uma, mas duas\b"
     r"|\be nunca o seguiu\b",
     "contraste em suspense ou dramatização: afirme direto, uma vez"),
    # GO-5: metáfora e imagem
    ("GO-5/ensaio", r"\bdescompasso\b|\bpano de fundo\b|\bmorre(?:u|m)? na praia\b"
     r"|\bca(?:i|iu|em) por terra\b|\bpá de cal\b|\bdivisor de águas\b|\bcalcanhar de aquiles\b"
     r"|\bcaminhos?\b",
     "imagem ou metáfora? troque pelo termo técnico: critério, premissa, incompatibilidade, "
     "fundamento"),
    # GO-5: metadiscurso estratégico
    ("GO-5/metadiscurso", r"\b(?:argumento|fundamento|tese)s? (?:é |são )?subsidiári[oa]s?\b"
     r"|\b(?:apenas|só) para argumentar\b|\bad argumentandum\b|\bpor amor ao debate\b"
     r"|\bprincipal,? (?:contudo|porém|todavia|entretanto|no entanto),? é outr[oa]\b",
     "metadiscurso estratégico: a peça mostra o resultado, não a arquitetura da tese"),
    # Persuasão calibrada
    ("persuasao/indignacao", r"\babsurd[oa]s?\b|\bteratol[óo]gic[oa]s?\b|\binaceit[áa]ve(?:l|is)\b"
     r"|\baberrantes?\b",
     "adjetivo de indignação: defenda com verbo e arquitetura; teratologia só se real "
     "(references/persuasao.md)"),
    ("persuasao/julgador", r"\b(?:o|a) (?:magistrad[oa]|julgador[a]?|ju[ií]z[a]?|relator[a]?"
     r"|desembargador[a]?|ministr[oa])\b[^.;]{0,30}?\b(?:ignorou|equivocou-se|se equivocou|errou"
     r"|desconsiderou|olvidou|desprezou|fechou os olhos)\b",
     "critique a decisão, não o julgador: \"o acórdão não enfrentou\" (references/persuasao.md)"),
    # Lentes de revisão
    ("revisao/metalinguagem", r"\bpassa-se (?:agora )?(?:à|a) (?:análise|analisar|examinar|exame"
     r"|demonstrar|demonstração)\b|\bpassemos (?:agora )?(?:à|a)\b|\bcomo se (?:verá|demonstrará)\b"
     r"|\bconforme se demonstrará\b|\bcomo (?:será|restará) demonstrado\b"
     r"|\b(?:argumento|fundamento|tese)s? (?:robust|irrefutáve|incontestáve)\w*|\breais e favoráveis\b",
     "metalinguagem: escreva o efeito em vez de anunciá-lo; adjetivo sobre o próprio "
     "argumento é corte (references/revisao.md)"),
    ("revisao/andaime", r"\b(?:primeiro|primeiramente|em primeiro lugar|segundo|em segundo lugar"
     r"|terceiro|em terceiro lugar),? porque\b|\bpor (?:duas|três|quatro) razões\b",
     "enumeração-andaime: funda com o conectivo certo; numere só requisitos, pedidos ou itens "
     "da lei (references/revisao.md)"),
    # Léxico da casa
    ("casa/lexico", r"\bimpetraç(?:ão|ões)\b",
     "léxico da casa: prefira \"ação\" ou \"demanda\" (fora de citação)"),
]
LEXICO = [(r, re.compile(p, re.I), m) for r, p, m in LEXICO]

SATURACAO = [
    ("cortesia/saturacao", "vênia", re.compile(
        r"\b(?:data|concessa) (?:maxima )?v[êe]nia\b|\b(?:com a )?devida v[êe]nia\b", re.I)),
    ("cortesia/saturacao", "latim ornamental", re.compile(
        r"\bin casu\b|\ba priori\b|\ba posteriori\b|\bin totum\b|\bab initio\b|\bex vi\b", re.I)),
    ("cortesia/saturacao", "adjetivação de cortesia", re.compile(
        r"\b[íi]nclit[oa]s?\b|\bpreclar[oa]s?\b|\binsignes?\b|\begr[ée]gi[oa]s?\b|\bcolend[oa]s?\b"
        r"|\bbrilhante (?:decisão|voto|sentença|acórdão)\b|\bdout[oa] (?:juízo|magistrad[oa]"
        r"|julgador[a]?)\b|\bvenerand[oa]\b", re.I)),
    ("GO-7/reformulacao", "reformulação", re.compile(
        r"\bou seja\b|\bem outras palavras\b|\bdito de outro modo\b|\bvale dizer\b", re.I)),
    ("padrao/vocativo", "vocativo", re.compile(
        r",\s+(?:Ex\.ª|Exa\.|Excelência|Exmos?\.\s+(?:Ministros?|Desembargador(?:es|as?)?)"
        r"|Nobres? Julgador(?:es|as?)?)\s*,", re.I)),
]


def checar_lexico(par, masc):
    for regra, rx, msg in LEXICO:
        for m in rx.finditer(masc):
            yield m.start(), regra, msg, _trecho(par.texto, m.start(), m.end())


# ------------------------------------------------------------------ GO-6
RE_NEG_MAS = re.compile(
    r"\bnão\s+(?:é|são|foi|foram|era|eram|será|seria|seriam|está|estão|estava|reside|residem"
    r"|constitui|constituem|configura|configuram|representa|representam"
    r"|se\s+trata\s+d[eoa]s?|se\s+cuida\s+d[eoa]s?)\b[^.;:!?]{1,120}?,?\s+"
    r"(?:mas|e\s+sim|senão)\b(?!\s+(?:também|ainda))", re.I)
RE_NEG_SOLTA = re.compile(
    r"\bnão\s+se\s+(?:trata|cuida)\s+d[eoa]s?\b|\blonge\s+de\s+(?:ser|constituir|configurar"
    r"|representar|se\s+tratar)\b|\bnão\s+diz(?:em)?\s+respeito\b", re.I)
MSG_NEG = ("definição por negação? se ninguém nos autos sustentou o que se nega, afirme "
           "direto; se sustentou, é refutação e fica")


def checar_negacao(par, masc):
    vistos = []
    for m in RE_NEG_MAS.finditer(masc):
        vistos.append((m.start(), m.end()))
        yield m.start(), "GO-6", MSG_NEG, _trecho(par.texto, m.start(), m.end(), folga=10)
    for m in RE_NEG_SOLTA.finditer(masc):
        if any(a <= m.start() < b for a, b in vistos):
            continue
        yield m.start(), "GO-6", MSG_NEG, _trecho(par.texto, m.start(), m.end())


# ------------------------------------------------------------------ "o mesmo"
RE_MESMO = re.compile(
    r"\b(?:o|a|os|as|do|da|dos|das|no|na|nos|nas|pelo|pela|pelos|pelas|ao|aos|à|às)\s+"
    r"mesm[oa]s?\b", re.I)
SEGUE_PRONOME = set("""
é são foi foram era eram será serão seria seriam seja sejam fosse fossem
está estão estava estavam esteve estiveram esteja estejam
tem têm tinha tinham teve tiveram tenha tenham tivesse
há houve havia haja possui possuem possuía possuíam
deve devem devia deviam deveria deveriam deverá deverão
pode podem podia podiam poderia poderiam poderá poderão possa possam
vem vêm veio vinha venha fica ficam ficou ficaram resta restam restou restaram
consta constam constava constou contém continha prevê previa previu dispõe dispunha dispôs
determina determinou estabelece estabeleceu encontra encontram encontrava
apresenta apresentam apresentou alega alegou sustenta sustentou afirma afirmou merece
faz fez faça deixa deixou passa passou permanece permaneceu continua continuou
ocorre ocorreu ocorria aplica aplicou vale valeu serve serviu decorre decorreu
trata tratou refere referiu alcança alcançou abrange abrangia menciona mencionou
indica indicou demonstra demonstrou comprova comprovou atende atendeu cumpre cumpriu
preenche preencheu sofre sofreu obteve requer requereu pede pediu juntou interpôs opôs
ajuizou manifestou recebeu carece careceu necessita precisa
não nunca jamais já também ainda sequer só apenas sempre tampouco
se lhe lhes me
em no na nos nas para por pelo pela pelos pelas com sem sobre perante contra até desde
após ante entre conforme junto ao aos à às
""".split())
SUFIXOS_VERBO = ("ou", "aram", "eram", "iram", "avam", "ará", "erá", "irá")
ENCLITICOS = ("-se", "-lhe", "-lhes", "-o", "-a", "-os", "-as")
MSG_MESMO = "\"o mesmo\" como pronome: repita o termo ou use o pronome adequado"


def _mesmo_pronominal(masc, fim):
    resto = masc[fim:]
    if not resto.strip():
        return True
    m = re.match(r"\s*([^\w\s])", resto)
    if m:
        return m.group(1) in ".,;:!?)"
    m = re.match(r"\s*(\w+(?:-\w+)*)", resto)
    if not m:
        return False
    w = m.group(1).lower()
    if w in SEGUE_PRONOME:
        return True
    if w.endswith(ENCLITICOS) and "-" in w:
        return True
    return len(w) > 4 and w.endswith(SUFIXOS_VERBO)


def checar_mesmo(par, masc):
    for m in RE_MESMO.finditer(masc):
        if _mesmo_pronominal(masc, m.end()):
            yield m.start(), "precisao/o-mesmo", MSG_MESMO, _trecho(par.texto, m.start(), m.end())


# ------------------------------------------------------------------ orquestração
def _ignorada(regra, cfg):
    return any(regra.lower().startswith(p.lower()) for p in cfg.ignorar if p)


def lint_texto(texto, arquivo="<texto>", cfg=None, **kw):
    """Devolve a lista de Alerta para um texto. kw sobrepõe campos de Config."""
    cfg = cfg or Config(**kw)
    pars = segmentar(texto)
    alertas = []
    contagem = {}   # (regra, família) -> [linhas]
    for p in pars:
        if p.tipo not in ("prosa", "item"):
            continue
        masc = mascarar(p.texto)
        for checagem in (checar_traco(p, masc), checar_paragrafo(p, cfg),
                         checar_lexico(p, masc), checar_negacao(p, masc), checar_mesmo(p, masc)):
            for pos, regra, msg, trecho in checagem:
                alertas.append(Alerta(arquivo, p.linha_de(pos), regra, msg, trecho))
        for regra, familia, rx in SATURACAO:
            for m in rx.finditer(masc):
                contagem.setdefault((regra, familia), []).append(
                    (p.linha_de(m.start()), _trecho(p.texto, m.start(), m.end(), folga=15)))
    for (regra, familia), ocorrencias in contagem.items():
        dose = cfg.max_reformulacao if regra == "GO-7/reformulacao" else cfg.max_cortesia
        if len(ocorrencias) > dose:
            linha, trecho = ocorrencias[dose]
            linhas = ", ".join(str(l) for l, _ in ocorrencias[:10])
            if regra == "GO-7/reformulacao":
                msg = (f"{familia} {len(ocorrencias)} vezes (linhas {linhas}): fica só a que "
                       f"acrescenta a consequência prática; a que repete o ponto com outras "
                       f"palavras sai")
            elif regra == "padrao/vocativo":
                msg = (f"{len(ocorrencias)} vocativos (linhas {linhas}): só nos 1 a 2 momentos "
                       f"decisivos (references/padroes-da-casa.md, padrão 6)")
            else:
                msg = (f"{familia} repetido {len(ocorrencias)} vezes (linhas {linhas}): uma vez ou "
                       f"outra é natural; a saturação é vício")
            alertas.append(Alerta(arquivo, linha, regra, msg, trecho))
    alertas.extend(checar_aberturas(pars, cfg, arquivo))
    alertas.extend(checar_abertura(pars, cfg, arquivo))
    alertas.extend(checar_remissao(pars, cfg, arquivo))
    alertas.extend(checar_parafrase(pars, cfg, arquivo))
    alertas.extend(checar_repeticao(pars, cfg, arquivo))
    alertas.extend(checar_precedente_narrado(pars, cfg, arquivo))
    alertas.extend(checar_decisao_contraria(pars, cfg, arquivo))
    alertas.extend(checar_media(pars, cfg, arquivo))
    alertas = [a for a in alertas if not _ignorada(a.regra, cfg)]
    alertas.sort(key=lambda a: (a.linha, a.regra))
    return alertas


def _ler(caminho):
    with open(caminho, "rb") as f:
        dados = f.read()
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return dados.decode(enc)
        except UnicodeDecodeError:
            continue
    return dados.decode("utf-8", errors="replace")


def _expandir(caminhos):
    for c in caminhos:
        if os.path.isdir(c):
            yield from sorted(glob.glob(os.path.join(c, "**", "*.md"), recursive=True))
        else:
            yield c


def resumo(alertas):
    r = {}
    for a in alertas:
        r[a.regra] = r.get(a.regra, 0) + 1
    return dict(sorted(r.items()))


def main(argv=None):
    for fluxo in (sys.stdout, sys.stderr):
        try:
            fluxo.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(
        description="Radar de estilo da escrita-juridica: aponta arquivo:linha + regra. "
                    "Falso positivo é aceitável; ausência de alerta não prova qualidade.")
    ap.add_argument("arquivos", nargs="+", help=".md/.txt (markdown ou blocos @tag) ou pasta com .md")
    ap.add_argument("--json", action="store_true", help="saída em JSON")
    ap.add_argument("--max-palavras", type=int, default=Config.max_palavras,
                    help="referência de teto por parágrafo (acima, confira se é uma ideia só)")
    ap.add_argument("--limite-palavras", type=int, default=Config.limite_palavras,
                    help="acima disso, o parágrafo quase sempre junta mais de uma ideia")
    ap.add_argument("--max-periodos", type=int, default=Config.max_periodos,
                    help="períodos por parágrafo antes do alerta (só em parágrafo acima da média-alvo)")
    ap.add_argument("--media", default=f"{Config.media_min}-{Config.media_max}",
                    help="faixa-alvo da média de palavras por parágrafo (ex.: 45-65)")
    ap.add_argument("--max-abertura-nominal", type=int, default=Config.max_abertura_nominal,
                    help="teto, em %%, de parágrafos abertos sem conectivo: sujeito nominal "
                         "(\"O MPF\") ou demonstrativo (\"Esse acórdão\")")
    ap.add_argument("--max-nominais-seguidas", type=int, default=Config.max_nominais_seguidas,
                    help="aberturas sem conectivo seguidas toleradas antes do alerta")
    ap.add_argument("--aberturas", type=int, default=Config.aberturas,
                    help="parágrafos seguidos com a mesma abertura que disparam o alerta")
    ap.add_argument("--max-cortesia", type=int, default=Config.max_cortesia,
                    help="ocorrências toleradas por família de latim, vênia, cortesia e vocativo")
    ap.add_argument("--ignorar", default="",
                    help="prefixos de regra a ignorar, separados por vírgula (ex.: GO-6,cortesia)")
    args = ap.parse_args(argv)
    try:
        media_min, media_max = (int(x) for x in args.media.split("-", 1))
    except ValueError:
        ap.error("--media deve ser uma faixa como 45-65")
    cfg = Config(max_palavras=args.max_palavras, limite_palavras=args.limite_palavras,
                 max_periodos=args.max_periodos, media_min=media_min, media_max=media_max,
                 aberturas=args.aberturas, max_cortesia=args.max_cortesia,
                 max_abertura_nominal=args.max_abertura_nominal,
                 max_nominais_seguidas=args.max_nominais_seguidas,
                 ignorar=tuple(x.strip() for x in args.ignorar.split(",") if x.strip()))

    alertas, erros, n_arq, paragrafos = [], 0, 0, {}
    for caminho in _expandir(args.arquivos):
        try:
            texto = _ler(caminho)
        except OSError as e:
            print(f"erro: não consegui ler {caminho}: {e}", file=sys.stderr)
            erros += 1
            continue
        n_arq += 1
        alertas.extend(lint_texto(texto, caminho, cfg))
        paragrafos[caminho] = estatisticas(segmentar(texto))

    if args.json:
        print(json.dumps({"alertas": [asdict(a) for a in alertas], "resumo": resumo(alertas),
                          "paragrafos": paragrafos}, ensure_ascii=False, indent=2))
    else:
        for a in alertas:
            print(f"{a.arquivo}:{a.linha}: [{a.regra}] {a.mensagem} | {a.trecho}")
        for caminho, est in paragrafos.items():
            if est["paragrafos"]:
                print(f"{caminho}: {est['paragrafos']} parágrafo(s) de prosa, média de "
                      f"{est['media_palavras']:.0f} palavras (faixa-alvo {cfg.media_min} a "
                      f"{cfg.media_max}), o maior com {est['maior']}; aberturas sem "
                      f"conectivo: {est['aberturas_sem_conectivo_pct']}% (teto "
                      f"{cfg.max_abertura_nominal}%)")
        if alertas:
            partes = ", ".join(f"{k}: {v}" for k, v in resumo(alertas).items())
            print(f"\n{len(alertas)} alerta(s) em {n_arq} arquivo(s) ({partes}). Radar: confirme "
                  f"cada alerta pelo teste da regra (references/revisao.md).")
        else:
            print(f"Nenhum alerta em {n_arq} arquivo(s). Radar: a ausência de alerta não prova "
                  f"qualidade; faça a leitura de revisão.")
    return 2 if erros else 0


if __name__ == "__main__":
    sys.exit(main())
