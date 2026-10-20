"""Testes do processo.py (analise-processo-pje) com PDFs sintéticos.

Os PDFs são montados aqui mesmo, sem dependência externa: páginas com texto
Helvetica, rodapé e cabeçalho no padrão do PJe, imagem de página inteira (escaneada),
camada de OCR invisível e bookmarks. Nomes, números e textos são fictícios.

Rodar: python -m pytest tests/test_processo.py -q   (ou python -m unittest)
"""
from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "analise-processo-pje" / "scripts" / "processo.py"

try:
    import pypdfium2  # noqa: F401
    TEM_PDFIUM = True
except ImportError:
    TEM_PDFIUM = False


def carregar_processo():
    spec = importlib.util.spec_from_file_location("processo_v13", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# PDF sintético mínimo
# ---------------------------------------------------------------------------
def _esc(s: str) -> str:
    b = s.encode("cp1252", errors="replace").decode("latin-1")
    return b.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _texto_pdf(s: str) -> str:
    """String de texto do PDF em UTF-16BE (aceita qualquer caractere no bookmark)."""
    return "<FEFF" + s.encode("utf-16-be").hex().upper() + ">"


def montar_pdf(caminho: Path, paginas: list[dict], bookmarks: list[tuple[str, int]] | None = None):
    """paginas: dicts com 'linhas' (texto visível), 'ocr' (texto invisível, modo 3),
    'rodape' (linhas no pé da página) e 'imagem' (True = imagem cobrindo a página).
    bookmarks: [(título, índice da página 0-based)]."""
    objs: list[bytes] = []

    def novo(conteudo: bytes) -> int:
        objs.append(conteudo)
        return len(objs)

    fonte = novo(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    imagem = novo(b"<< /Type /XObject /Subtype /Image /Width 2 /Height 2 /ColorSpace /DeviceGray "
                  b"/BitsPerComponent 8 /Length 4 >>\nstream\n\x80\x40\x40\x80\nendstream")
    pages_id = novo(b"")  # preenchido depois
    page_ids = []
    for pg in paginas:
        ops = []
        if pg.get("imagem"):
            ops.append("q 595 0 0 842 0 0 cm /Im1 Do Q")
        if pg.get("linhas"):
            ops.append("BT /F1 11 Tf 14 TL 72 790 Td")
            ops += [f"({_esc(ln)}) Tj T*" for ln in pg["linhas"]]
            ops.append("ET")
        if pg.get("ocr"):
            ops.append("BT /F1 11 Tf 14 TL 3 Tr 72 600 Td")
            ops += [f"({_esc(ln)}) Tj T*" for ln in pg["ocr"]]
            ops.append("ET")
        if pg.get("rodape"):
            ops.append("BT /F1 7 Tf 9 TL 40 60 Td")
            ops += [f"({_esc(ln)}) Tj T*" for ln in pg["rodape"]]
            ops.append("ET")
        stream = "\n".join(ops).encode("latin-1")
        conteudo = novo(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
        page_ids.append(novo(
            (f"<< /Type /Page /Parent {pages_id} 0 R /MediaBox [0 0 595 842] "
             f"/Resources << /Font << /F1 {fonte} 0 R >> /XObject << /Im1 {imagem} 0 R >> >> "
             f"/Contents {conteudo} 0 R >>").encode("latin-1")))
    objs[pages_id - 1] = (f"<< /Type /Pages /Kids [{' '.join(f'{i} 0 R' for i in page_ids)}] "
                          f"/Count {len(page_ids)} >>").encode("latin-1")
    extra_catalogo = ""
    if bookmarks:
        raiz = novo(b"")
        itens = list(range(len(objs) + 1, len(objs) + 1 + len(bookmarks)))
        for k, (titulo, pg) in enumerate(bookmarks):
            rel = f"/Title {_texto_pdf(titulo)} /Parent {raiz} 0 R /Dest [{page_ids[pg]} 0 R /XYZ 0 842 0]"
            if k > 0:
                rel += f" /Prev {itens[k - 1]} 0 R"
            if k + 1 < len(itens):
                rel += f" /Next {itens[k + 1]} 0 R"
            novo(f"<< {rel} >>".encode("latin-1"))
        objs[raiz - 1] = (f"<< /Type /Outlines /First {itens[0]} 0 R /Last {itens[-1]} 0 R "
                          f"/Count {len(itens)} >>").encode("latin-1")
        extra_catalogo = f" /Outlines {raiz} 0 R /PageMode /UseOutlines"
    catalogo = novo(f"<< /Type /Catalog /Pages {pages_id} 0 R{extra_catalogo} >>".encode("latin-1"))

    saida = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
    offsets = []
    for i, conteudo in enumerate(objs, start=1):
        offsets.append(len(saida))
        saida += f"{i} 0 obj\n".encode("latin-1") + conteudo + b"\nendobj\n"
    xref = len(saida)
    saida += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode("latin-1")
    for off in offsets:
        saida += f"{off:010d} 00000 n \n".encode("latin-1")
    saida += (f"trailer\n<< /Size {len(objs) + 1} /Root {catalogo} 0 R >>\n"
              f"startxref\n{xref}\n%%EOF\n").encode("latin-1")
    caminho.write_bytes(bytes(saida))
    return caminho


def rodape(num: str, pag: int) -> list[str]:
    return [f"Num. {num} - Pág. {pag} Assinado eletronicamente por: FULANO DE TAL - 01/02/2026 10:00:00",
            "https://pje.exemplo.jus.br/consultapublica/Processo/ConsultaDocumento/listView.seam?x=1",
            "Número do documento: 26020110000000000000000000001"]


PARAGRAFO = ("A parte autora sustenta que a cobrança é indevida e requer a restituição dos valores, "
             "com correção pela taxa Selic, nos termos da legislação aplicável ao caso concreto.")


def autos_trf1(pasta: Path) -> Path:
    """Autos ao estilo do TRF-1: bookmark 'Tipo | Nome | NUM | data', cabeçalho de página."""
    pags, bms = [], []
    pags += [{"linhas": ["Número: 1234567-89.2024.4.05.8100", "Classe: APELAÇÃO CÍVEL",
                         "Partes: FULANO DE TAL (APELANTE)"]}]
    bms.append(("Cabeçalho", 0))
    pags += [{"linhas": ["Id. Data da Assinatura Documento Tipo Polo",
                         "111111111 01/02/2026 10:00 Inicial do autor Petição inicial Polo ativo"]}]
    bms.append(("Índice", 1))
    # seq 2: petição inicial (2 págs.)
    for k in (1, 2):
        pags.append({"linhas": ["Documento id 111111111 - Petição inicial (Inicial do autor)",
                                "EXCELENTÍSSIMO SENHOR JUIZ FEDERAL" if k == 1 else "DOS PEDIDOS",
                                PARAGRAFO, "A prescrição não se consumou."], "rodape": rodape("111111111", k)})
    bms.append(("Petição inicial | Inicial do autor | NUM: 111111111 | 01/02/2026 10:00", 2))
    # seq 3: procuração com barra vertical no nome
    pags.append({"linhas": ["Documento id 222222222 - Procuração (Procuração | outorgante Fulano)",
                            "Pelo presente instrumento, FULANO DE TAL nomeia e constitui seu procurador."],
                 "rodape": rodape("222222222", 1)})
    bms.append(("Procuração | Procuração | outorgante Fulano | NUM: 222222222 | 01/02/2026 10:05", 4))
    # seq 4: volume digitalizado: pág. 1 com OCR invisível, pág. 2 escaneada sem texto
    pags.append({"imagem": True, "linhas": ["Documento id 333333333 - Volume (VOL_001)"],
                 "ocr": ["TERMO DE AUTUACAO DO PROCESSO FISICO", PARAGRAFO, PARAGRAFO],
                 "rodape": rodape("333333333", 1)})
    pags.append({"imagem": True, "linhas": ["Documento id 333333333 - Volume (VOL_001)", "3/12"],
                 "rodape": rodape("333333333", 2)})
    bms.append(("Volume | VOL_001 | NUM: 333333333 | 02/02/2026 09:00", 5))
    # seq 5: sentença que cita o volume por id e página
    pags.append({"linhas": ["Documento id 444444444 - Sentença", "SENTENÇA", PARAGRAFO,
                            "Conforme o termo de autuação (ID 333333333 - Pág. 2), o feito foi migrado.",
                            "Ante o exposto, julgo procedente o pedido. A prescrição foi afastada."],
                 "rodape": rodape("444444444", 1)})
    bms.append(("Sentença | Sentença | NUM: 444444444 | 03/02/2026 15:00", 7))
    # seq 6: petição intercorrente de juntada
    pags.append({"linhas": ["Documento id 555555555 - Petição intercorrente (Juntada de substabelecimento)",
                            "Requer a juntada do substabelecimento anexo."], "rodape": rodape("555555555", 1)})
    bms.append(("Petição intercorrente | Juntada de substabelecimento ■ | NUM: 555555555 | 04/02/2026 11:00", 8))
    return montar_pdf(pasta / "autos_trf1.pdf", pags, bms)


def autos_trf5(pasta: Path) -> Path:
    """Autos ao estilo do TRF-5: bookmark só com o tipo; nomes no documento Índice."""
    pags = [
        {"linhas": ["Número: 7654321-00.2025.4.05.8300"]},
        {"linhas": ["Id. Data da", "Assinatura", "Documento Tipo",
                    "777777771 10/03/2026 09:00 Petição inicial - ação de", "repetição de indébito Petição Inicial",
                    "777777772 11/03/2026 10:00 Contestação da União Contestação",
                    "777777773 12/03/2026 11:00 Petição Petição (Outras)"]},
        {"linhas": ["EXCELENTÍSSIMO SENHOR JUIZ", PARAGRAFO], "rodape": rodape("777777771", 1)},
        {"linhas": ["CONTESTAÇÃO", PARAGRAFO], "rodape": rodape("777777772", 1)},
        {"linhas": ["Requer a juntada de documentos e a intimação da parte contrária."],
         "rodape": rodape("777777773", 1)},
    ]
    bms = [("Cabeçalho", 0), ("Índice", 1),
           ("Petição Inicial | NUM: 777777771 | 10/03/2026 09:00", 2),
           ("Contestação | NUM: 777777772 | 11/03/2026 10:00", 3),
           ("Petição (Outras) | NUM: 777777773 | 12/03/2026 11:00", 4)]
    return montar_pdf(pasta / "autos_trf5.pdf", pags, bms)


@unittest.skipUnless(TEM_PDFIUM, "pypdfium2 não instalado")
class ProcessoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.dir = Path(cls.tmp.name)
        cls.trf1 = autos_trf1(cls.dir)
        cls.trf5 = autos_trf5(cls.dir)
        cls.proc = carregar_processo()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def run_cli(self, *args, env_extra=None, cwd=None):
        env = {k: v for k, v in os.environ.items()
               if k not in ("PRATICA_JURIDICA_DATA", "CLAUDE_PLUGIN_DATA", "PYTHONUTF8")}
        env["PYTHONIOENCODING"] = "cp1252"   # reproduz o console do Windows
        env["TMP"] = env["TEMP"] = env["TMPDIR"] = str(self.dir / "tmp")
        (self.dir / "tmp").mkdir(exist_ok=True)
        env.update(env_extra or {})
        r = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True,
                           cwd=cwd or self.dir, env=env)
        return r.returncode, r.stdout.decode("utf-8"), r.stderr.decode("utf-8")

    # --- index ---------------------------------------------------------------
    def test_index_separa_tipo_e_nome_e_classifica(self):
        code, out, err = self.run_cli("index", self.trf1)
        self.assertEqual(code, 0, err)
        linhas = {ln.split("|")[1].strip(): ln for ln in out.splitlines() if ln.startswith("| ") and "seq" not in ln}
        self.assertIn("| 2 | Petição inicial | Inicial do autor | 111111111 |", linhas["2"])
        self.assertTrue(linhas["2"].rstrip().endswith("| sim |"))
        self.assertIn(r"Procuração \| outorgante Fulano", linhas["3"])     # barra escapada
        self.assertTrue(linhas["3"].rstrip().endswith("| — |"))
        self.assertTrue(linhas["4"].rstrip().endswith("| 1 | ? |"))        # volume: 1 pág. sem texto
        self.assertTrue(linhas["5"].rstrip().endswith("| sim |"))
        self.assertTrue(linhas["6"].rstrip().endswith("| — |"))            # juntada
        self.assertIn("■", out)                                             # UTF-8 com console cp1252
        self.assertIn("páginas sem texto: 1", out)

    def test_index_json_e_classificacao(self):
        code, out, err = self.run_cli("index", self.trf1, "--json")
        self.assertEqual(code, 0, err)
        docs = json.loads(out)
        self.assertEqual(docs[4]["tipo"], "Volume")
        self.assertEqual(docs[4]["nome"], "VOL_001")
        self.assertEqual(docs[4]["sem_texto"], 1)
        self.assertIsNone(docs[4]["is_peca"])
        self.assertNotIn("slug", docs[0])
        c = self.proc.classificar_peca
        self.assertTrue(c("Manifestação", "Razões finais"))
        self.assertFalse(c("Manifestação", "Ciência"))
        self.assertIsNone(c("Petição (Outras)", ""))
        self.assertFalse(c("Certidão", ""))

    def test_index_trf5_le_nomes_do_documento_indice(self):
        code, out, err = self.run_cli("index", self.trf5, "--json")
        self.assertEqual(code, 0, err)
        docs = {d["num"]: d for d in json.loads(out) if d["num"]}
        self.assertEqual(docs["777777771"]["tipo"], "Petição Inicial")
        self.assertEqual(docs["777777771"]["nome"], "Petição inicial - ação de repetição de indébito")
        self.assertEqual(docs["777777772"]["nome"], "Contestação da União")
        self.assertEqual(docs["777777773"]["nome"], "Petição")
        self.assertIsNone(docs["777777773"]["is_peca"])
        code, out, _ = self.run_cli("index", self.trf5)
        self.assertIn("nomes lidos do documento Índice", out)

    def test_sem_bookmarks_remonta_pelo_rodape(self):
        pags = [{"linhas": ["Documento id 900000001 - Decisão", "DECISÃO", PARAGRAFO], "rodape": rodape("900000001", 1)},
                {"linhas": ["Documento id 900000001 - Decisão", PARAGRAFO], "rodape": rodape("900000001", 2)},
                {"linhas": ["Documento id 900000002 - Certidão", "Certifico o decurso do prazo."],
                 "rodape": rodape("900000002", 1)}]
        pdf = montar_pdf(self.dir / "sem_bm.pdf", pags)
        code, out, err = self.run_cli("index", pdf, "--json")
        self.assertEqual(code, 0, err)
        self.assertIn("SEM BOOKMARKS", err)
        docs = json.loads(out)
        self.assertEqual([(d["num"], d["pg_ini"], d["pg_fim"], d["tipo"]) for d in docs],
                         [("900000001", 1, 2, "Decisão"), ("900000002", 3, 3, "Certidão")])
        code, out, err = self.run_cli("extract", pdf, "--docs", "0", "--out", self.dir / "ext_sem_bm")
        self.assertEqual(code, 0, err)

    def test_sem_bookmarks_e_sem_rodape_vira_faixas(self):
        pags = [{"linhas": [f"Página avulsa número {k} com algum texto corrido do documento."]} for k in range(60)]
        pdf = montar_pdf(self.dir / "faixas.pdf", pags)
        code, out, err = self.run_cli("index", pdf)
        self.assertEqual(code, 0, err)
        self.assertIn("AVISO", err)
        self.assertIn("faixa de 50 páginas", out)
        self.assertIn("| 1 | Faixa de páginas |", out)
        self.assertIn("51-60 (10)", out)

    # --- extract ---------------------------------------------------------------
    def test_extract_marca_paginas_e_limpa_pje(self):
        out_dir = self.dir / "ext"
        code, out, err = self.run_cli("extract", self.trf1, "--docs", "4,5", "--out", out_dir)
        self.assertEqual(code, 0, err)
        vol = (out_dir / "doc_004_volume-vol-001.md").read_text(encoding="utf-8")
        self.assertIn("fonte: misto", vol)
        self.assertIn("paginas_sem_texto: 7", vol)
        self.assertIn("paginas_ocr: 6", vol)
        self.assertIn("<!-- pág. 6 · texto de OCR", vol)
        self.assertIn("<!-- pág. 7 · sem texto extraível (imagem)", vol)
        self.assertIn("render autos_trf1.pdf --pages 7", vol)
        self.assertIn("3/12", vol)                      # resíduo preservado, mas marcado
        sent = (out_dir / "doc_005_sentenca-sentenca.md").read_text(encoding="utf-8")
        self.assertIn("fonte: texto-nativo", sent)
        self.assertNotIn("Documento id", sent)
        self.assertNotIn("Assinado eletronicamente", sent)
        self.assertNotIn("Número do documento", sent)
        self.assertIn("julgo procedente", sent)

    def test_extract_paginas_e_aviso_de_tamanho(self):
        out_dir = self.dir / "ext_pags"
        code, out, err = self.run_cli("extract", self.trf1, "--pages", "3-4", "--out", out_dir)
        self.assertEqual(code, 0, err)
        txt = (out_dir / "paginas_0003-0004.md").read_text(encoding="utf-8")
        self.assertIn("paginas: 3-4", txt)
        self.assertIn("documentos: 2", txt)
        code, out, err = self.run_cli("extract", self.trf1, "--docs", "2,4", "--out", out_dir,
                                      "--limite-tokens", "100")
        self.assertEqual(code, 3)
        self.assertIn("AVISO DE TAMANHO", err)
        code, out, err = self.run_cli("extract", self.trf1, "--docs", "2,4", "--out", out_dir,
                                      "--limite-tokens", "100", "--confirmar")
        self.assertEqual(code, 0, err)

    def test_extract_sem_out_usa_workspace_do_cnj(self):
        dados = self.dir / "dados_ws"
        code, out, err = self.run_cli("extract", self.trf1, "--docs", "5",
                                      env_extra={"PRATICA_JURIDICA_DATA": str(dados)})
        self.assertEqual(code, 0, err)
        self.assertTrue((dados / "processos" / "1234567-89.2024.4.05.8100" / "doc_005_sentenca-sentenca.md").exists())

    # --- grep, find, refs --------------------------------------------------------
    def test_grep_sem_acento_com_pagina_e_documento(self):
        code, out, err = self.run_cli("grep", self.trf1, "prescricao")
        self.assertEqual(code, 0, err)
        self.assertIn("3 ocorrência(s)", out)
        self.assertIn("pág. 3 · seq 2 Petição inicial", out)
        self.assertIn("**prescrição**", out)
        code, out, _ = self.run_cli("grep", self.trf1, "prescricao", "--exato")
        self.assertIn("Nenhuma ocorrência", out)
        code, out, _ = self.run_cli("grep", self.trf1, r"JULGO\s+\S+dente", "--regex", "--docs", "5")
        self.assertIn("pág. 8 · seq 5 Sentença", out)
        code, out, _ = self.run_cli("find", self.trf1, "--pattern", "substabelecimento", "--docs", "6")
        self.assertIn("seq 6", out)

    def test_find_id_e_refs(self):
        code, out, err = self.run_cli("find", self.trf1, "--id", "444444444")
        self.assertEqual(code, 0, err)
        self.assertEqual(json.loads(out.splitlines()[0])["seq"], 5)
        code, out, _ = self.run_cli("find", self.trf1, "--id", "999999999")
        self.assertIn("Nenhum documento", out)
        code, out, err = self.run_cli("refs", self.trf1, "--docs", "5")
        self.assertEqual(code, 0, err)
        self.assertIn("id 333333333, pág. 2 → seq 4 Volume", out)
        self.assertIn("pág. 2 do documento = pág. 7 do PDF", out)
        self.assertNotIn("id 444444444", out)          # o próprio documento não conta

    # --- páginas sem texto -------------------------------------------------------
    def test_sem_texto_json(self):
        code, out, err = self.run_cli("sem-texto", self.trf1, "--json")
        self.assertEqual(code, 0, err)
        dados = json.loads(out)
        self.assertEqual(dados["paginas_sem_texto"], 1)
        self.assertEqual(dados["documentos"][0]["seq"], 4)
        self.assertEqual(dados["documentos"][0]["paginas"], [7])
        self.assertIn("80 caracteres", dados["criterio"])
        code, out, _ = self.run_cli("sem-texto", self.trf1, "--doc", "5")
        self.assertIn("Nenhuma página sem texto", out)

    def test_render_png(self):
        out_dir = self.dir / "img"
        code, out, err = self.run_cli("render", self.trf1, "--pages", "7", "--out", out_dir, "--escala", "0.5")
        self.assertEqual(code, 0, err)
        self.assertEqual((out_dir / "pag_0007.png").read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        destino = self.dir / "cinza.png"
        self.proc._png_cinza(destino, 3, 2, 4, bytes([0, 128, 255, 9, 10, 20, 30, 9]))
        self.assertEqual(destino.read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
        code, out, err = self.run_cli("render", self.trf1, "--pages", "1-9", "--out", out_dir)
        self.assertEqual(code, 0, err)
        code, _, err = self.run_cli("render", self.trf1, "--pages", "1-99", "--out", out_dir)
        self.assertNotEqual(code, 0)

    # --- workspace ---------------------------------------------------------------
    def test_workspace_normaliza_cnj_e_reaproveita_layout_antigo(self):
        dados = self.dir / "dados"
        env = {"PRATICA_JURIDICA_DATA": str(dados)}
        code, out, err = self.run_cli("workspace", "12345678920244058100", env_extra=env)
        self.assertEqual(code, 0, err)
        self.assertEqual(Path(out.strip()), (dados / "processos" / "1234567-89.2024.4.05.8100").resolve())
        antigo = dados / "7654321-00.2025.4.05.8300"
        antigo.mkdir(parents=True)
        code, out, err = self.run_cli("workspace", "7654321-00.2025.4.05.8300", env_extra=env)
        self.assertEqual(Path(out.strip()), antigo.resolve())
        self.assertIn("layout antigo", err)
        for ruim in ("..", ".", "/", "\\"):
            code, out, err = self.run_cli("workspace", ruim, env_extra=env)
            self.assertNotEqual(code, 0, ruim)
        self.assertEqual(self.proc.normalizar_cnj("../outro"), "outro")

    def test_workspace_sem_variavel_avisa_pasta_temporaria(self):
        sessao = self.dir / "sessao"
        sessao.mkdir(exist_ok=True)
        code, out, err = self.run_cli("workspace", "1234567-89.2024.4.05.8100", cwd=sessao)
        self.assertEqual(code, 0, err)
        self.assertIn("PASTA TEMPORÁRIA", err)
        self.assertIn("PRATICA_JURIDICA_DATA", err)
        self.assertTrue(Path(out.strip()).is_dir())

    def test_workspace_detecta_dados_juridicos(self):
        sessao = self.dir / "cowork" / "mnt" / "outputs"
        sessao.mkdir(parents=True, exist_ok=True)
        pasta_usuario = self.dir / "cowork" / "mnt" / "Processos" / "dados-juridicos"
        pasta_usuario.mkdir(parents=True, exist_ok=True)
        code, out, err = self.run_cli("workspace", "1234567-89.2024.4.05.8100", cwd=sessao)
        self.assertEqual(code, 0, err)
        self.assertEqual(Path(out.strip()),
                         (pasta_usuario / "processos" / "1234567-89.2024.4.05.8100").resolve())


if __name__ == "__main__":
    unittest.main()
