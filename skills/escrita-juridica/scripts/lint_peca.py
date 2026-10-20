#!/usr/bin/env python3
"""lint_peca.py — radar de estilo da escrita-juridica.

Lê peça ou relatório em markdown, ou em blocos @tag (formatacao-entrega), e aponta
arquivo:linha + regra para os padrões que a casa manda varrer:

  GO-2                travessão, meia-risca ou hífen com espaços usado como traço aditivo
  GO-4/paragrafo      parágrafo que passa da referência de palavras ou junta períodos demais
  GO-4/media          média de palavras por parágrafo fora da faixa-alvo (70 a 90)
  GO-4/aberturas      parágrafos seguidos com a mesma abertura (padrão: três)
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
        [--max-palavras 120] [--limite-palavras 130] [--max-periodos 2] [--media 70-90]
        [--aberturas 3] [--max-cortesia 2] [--ignorar GO-6,cortesia]

A régua do parágrafo é de ideia, não de número: um parágrafo diz uma coisa só,
normalmente em um ou dois períodos curtos. Os números só apontam onde olhar: média de
70 a 90 palavras por parágrafo na peça; 120 é referência de teto (125 ou 130 cabem se a
ideia pede); acima de 130, quase sempre há duas ideias.

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
from dataclasses import asdict, dataclass, field


# ------------------------------------------------------------------ configuração
@dataclass
class Config:
    max_palavras: int = 120     # referência de teto: acima, confira se é uma ideia só
    limite_palavras: int = 130  # acima, o parágrafo quase sempre junta ideias
    max_periodos: int = 2       # o padrão é um ou dois períodos curtos
    media_min: int = 70         # faixa-alvo da média de palavras por parágrafo
    media_max: int = 90
    min_pars_media: int = 6     # com menos parágrafos de prosa (peça protocolar), sem média
    aberturas: int = 3
    max_cortesia: int = 2
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

    def marco(tipo, n):
        fechar()
        if not saida or saida[-1].tipo != tipo:
            saida.append(Paragrafo(tipo, [(n, "")]).montar())

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
            marco(cat, n)
            continue
        if not linha.strip():
            fechar()
            continue
        if RE_CITACAO_MD.match(linha):
            marco("citacao", n)
            continue
        if RE_TITULO_MD.match(linha):
            marco("titulo", n)
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
    r"\b(Rel|Min|Des|Dr|Dra|Sr|Sra|Exmos?|Exmas?|Exa|Ex|Ilmos?|Ilmas?|Profa?|Cf|cf|V|v|"
    r"Id|id|Ib|ib|n|art|arts|inc|incs|fls?|pp?|ss|al|Ltda|S\.A)\."
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
    elif periodos > cfg.max_periodos and palavras > cfg.media_max:
        msg = (f"parágrafo de {palavras} palavras em {periodos} períodos: o padrão é uma ideia "
               f"em um ou dois períodos curtos; confira se não há duas ideias")
    else:
        return
    yield 0, "GO-4/paragrafo", msg, _trecho(par.texto, 0, 60, folga=0)


def estatisticas(pars):
    """Tamanho dos parágrafos de prosa (sem itens, títulos e citações)."""
    tamanhos = [len(p.texto.split()) for p in pars if p.tipo == "prosa"]
    if not tamanhos:
        return {"paragrafos": 0, "media_palavras": 0.0, "maior": 0}
    return {"paragrafos": len(tamanhos),
            "media_palavras": round(sum(tamanhos) / len(tamanhos), 1),
            "maior": max(tamanhos)}


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
               f"parágrafos, abaixo da {faixa}: confira se o raciocínio não ficou picotado "
               f"(frase solta sem função de ênfase)")
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
        if len(ocorrencias) > cfg.max_cortesia:
            linha, trecho = ocorrencias[cfg.max_cortesia]
            linhas = ", ".join(str(l) for l, _ in ocorrencias[:10])
            if regra == "padrao/vocativo":
                msg = (f"{len(ocorrencias)} vocativos (linhas {linhas}): só nos 1 a 2 momentos "
                       f"decisivos (references/padroes-da-casa.md, padrão 6)")
            else:
                msg = (f"{familia} repetido {len(ocorrencias)} vezes (linhas {linhas}): uma vez ou "
                       f"outra é natural; a saturação é vício")
            alertas.append(Alerta(arquivo, linha, regra, msg, trecho))
    alertas.extend(checar_aberturas(pars, cfg, arquivo))
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
                    help="faixa-alvo da média de palavras por parágrafo (ex.: 70-90)")
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
        ap.error("--media deve ser uma faixa como 70-90")
    cfg = Config(max_palavras=args.max_palavras, limite_palavras=args.limite_palavras,
                 max_periodos=args.max_periodos, media_min=media_min, media_max=media_max,
                 aberturas=args.aberturas, max_cortesia=args.max_cortesia,
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
                      f"{cfg.media_max}), o maior com {est['maior']}")
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
