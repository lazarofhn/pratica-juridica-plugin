"""Offline behavioral checks for the OpenAI variant (synthetic sources only)."""
from contextlib import redirect_stdout
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/pratica-juridica-work'
sys.path.insert(0, str(PLUGIN / 'skills/formatacao-entrega/scripts'))
import citar


def load_script(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


processo = load_script('processo', PLUGIN / 'skills/analise-processo-pje/scripts/processo.py')


class WorkTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.ws = Path(self.temp.name)
        self.source = self.ws / 'fonte.txt'
        self.source.write_text('1. Texto sintético de teste.\n2. Conclusão distinta e verificável.\n', encoding='utf-8')

    def resolve(self, **kwargs):
        return citar.resolve_file(self.ws, 'fonte.txt', citar.digest(self.source), **kwargs)[0]

    def test_literal_items_keep_second_item(self):
        self.assertEqual(self.resolve(itens='2'), '2. Conclusão distinta e verificável.')

    def test_changed_source_rejected(self):
        old = citar.digest(self.source)
        self.source.write_text('Alterada', encoding='utf-8')
        with self.assertRaises(ValueError):
            citar.resolve_file(self.ws, 'fonte.txt', old)

    def test_no_hash_rejected(self):
        with self.assertRaises(ValueError):
            citar.resolve_file(self.ws, 'fonte.txt', None)

    def test_ambiguous_anchors_rejected(self):
        self.source.write_text('igual primeiro igual fim', encoding='utf-8')
        with self.assertRaises(LookupError):
            self.resolve(trecho='de "igual" ate "fim"')

    def test_wrong_document_cannot_match_by_process(self):
        (self.ws / 'outro.txt').write_text('Mesmo processo, outra decisão.', encoding='utf-8')
        self.assertEqual(self.resolve(trecho='de "Conclusão" ate "verificável."'), 'Conclusão distinta e verificável.')

    def test_path_escape_rejected(self):
        with self.assertRaises(ValueError):
            citar.source_path(self.ws, '../fora.txt')

    def test_missing_highlight_rejected(self):
        with self.assertRaises(LookupError):
            citar.find_grifo('Texto existente', 'ausente')

    def test_workspace_normalization_and_boundary(self):
        out = io.StringIO()
        with patch.dict(os.environ, {'PRATICA_JURIDICA_DATA': str(self.ws)}), redirect_stdout(out):
            processo.cmd_workspace(type('Args', (), {'cnj': '1234567-89.2024.4.05.8100'})())
        self.assertEqual(Path(out.getvalue().strip()), (self.ws / 'processos/12345678920244058100').resolve())
        for value in ('..', '../outro', '.', 'abc', '12/34'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                processo.cmd_workspace(type('Args', (), {'cnj': value})())

    def test_docx_contains_exact_quote_and_house_style(self):
        from docx import Document
        source = self.ws / 'peca.md'
        source.write_text('@titulo\nDocumento de teste\n@citacao-ref\narquivo: fonte.txt\nsha256: '
            + citar.digest(self.source) + '\nitens: 2\ngrifo: distinta\nref: Fonte sintética\n', encoding='utf-8')
        dest = self.ws / 'peca.docx'
        cmd = [sys.executable, str(PLUGIN / 'skills/formatacao-entrega/scripts/build_docx.py'), str(source), '--out', str(dest)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        doc = Document(dest)
        quote = next(p for p in doc.paragraphs if 'Conclusão' in p.text)
        self.assertIn('2. Conclusão distinta e verificável.', quote.text)
        self.assertNotIn('Texto sintético', quote.text)
        self.assertAlmostEqual(quote.paragraph_format.left_indent.cm, 2, places=2)
        self.assertTrue(any(r.font.highlight_color for r in quote.runs))
        # A stale hash must fail before overwriting an existing artifact.
        before = dest.read_bytes()
        self.source.write_text('Mutação posterior', encoding='utf-8')
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(dest.read_bytes(), before)

    def test_pje_pdf_index_and_selective_extraction(self):
        from reportlab.pdfgen import canvas
        from pypdf import PdfReader, PdfWriter
        raw = self.ws / 'raw.pdf'
        c = canvas.Canvas(str(raw))
        c.drawString(70, 700, 'DOCUMENTO UM TESTE')
        c.showPage()
        c.drawString(70, 700, 'DOCUMENTO DOIS TESTE')
        c.save()
        writer = PdfWriter()
        for page in PdfReader(raw).pages:
            writer.add_page(page)
        writer.add_outline_item('Peticao | NUM: 111111 | 01/01/2026', 0)
        writer.add_outline_item('Decisao | NUM: 222222 | 02/01/2026', 1)
        pdf = self.ws / 'autos.pdf'
        with pdf.open('wb') as stream:
            writer.write(stream)
        handle = processo._abrir(str(pdf))
        try:
            docs = processo.construir_indice(handle)
            self.assertEqual(len(docs), 2)
            text = processo.texto_doc(handle, docs[1])
            self.assertIn('DOCUMENTO DOIS', text)
            self.assertNotIn('DOCUMENTO UM', text)
            self.assertEqual(docs[1]['num'], '222222')
            self.assertEqual(docs[1]['pg_ini'], 2)
        finally:
            handle.close()

    def test_all_skills_and_relative_markdown_links(self):
        import re
        skills = list((PLUGIN / 'skills').glob('*/SKILL.md'))
        self.assertEqual(len(skills), 15)
        for p in (PLUGIN / 'skills').rglob('*.md'):
            for target in re.findall(r'\]\(([^)]+)\)', p.read_text(encoding='utf-8')):
                if '://' not in target and not target.startswith('#'):
                    self.assertTrue((p.parent / target.split('#')[0]).exists(), f'{p}: {target}')


if __name__ == '__main__':
    unittest.main()
