"""Testes do radar de estilo da escrita-juridica (lint_peca.py), com textos sintéticos.

Rodar: python -m unittest tests.test_lint_peca   (ou: python tests/test_lint_peca.py)
"""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "escrita-juridica" / "scripts" / "lint_peca.py"

_spec = importlib.util.spec_from_file_location("lint_peca", SCRIPT)
lint = importlib.util.module_from_spec(_spec)
sys.modules["lint_peca"] = lint
_spec.loader.exec_module(lint)


def regras(texto, **kw):
    return [a.regra for a in lint.lint_texto(texto, **kw)]


def corpo(*paragrafos):
    return "@corpo\n" + "\n\n".join(paragrafos) + "\n"


class TracoAditivo(unittest.TestCase):
    def test_travessao_no_corpo(self):
        alertas = lint.lint_texto(corpo("A decisão — amplamente fundamentada — foi publicada."))
        self.assertEqual([a.regra for a in alertas], ["GO-2", "GO-2"])
        self.assertTrue(all(a.linha == 2 for a in alertas))

    def test_hifen_com_espacos_e_meia_risca(self):
        self.assertEqual(regras(corpo("A empresa - ré no processo - contestou.")), ["GO-2", "GO-2"])
        self.assertEqual(regras(corpo("A empresa – ré no processo – contestou.")), ["GO-2", "GO-2"])

    def test_hifen_de_palavra_numero_e_intervalo_nao_dispara(self):
        texto = corpo("O decreto-lei incide no processo 1234567-89.2024.4.05.8100, "
                      "nos exercícios 2019–2021 e na conta 10 - 5.")
        self.assertEqual(regras(texto), [])

    def test_citacao_em_bloco_e_por_referencia_sao_ignoradas(self):
        texto = ("@citacao\nA decisão — fundamentada — foi publicada.\n\n"
                 "@citacao-ref\nfonte: autos\ndoc: 12\ntrecho: de \"a parte — ora\" ate \"fim\"\n\n"
                 "@corpo\nTexto limpo.\n")
        self.assertEqual(regras(texto), [])

    def test_trecho_entre_aspas_e_ignorado(self):
        texto = corpo("O acórdão afirmou que “a parte — ora recorrente — não comprovou o fato”.")
        self.assertEqual(regras(texto), [])

    def test_markdown_ignora_lista_titulo_tabela_codigo_e_citacao(self):
        texto = ("# Título — com travessão\n\n- primeiro item\n- segundo item\n\n"
                 "| coluna — a | b |\n|---|---|\n\n```\nx — y\n```\n\n"
                 "> citação — com travessão\n\nTexto limpo.\n")
        self.assertEqual(regras(texto), [])

    def test_frontmatter_ignorado(self):
        self.assertEqual(regras("---\ntitulo: a — b\n---\n\nTexto limpo.\n"), [])

    def test_linha_reportada_no_paragrafo_quebrado(self):
        alertas = lint.lint_texto("Primeira linha sem traço,\nsegunda linha — com traço.\n")
        self.assertEqual([(a.regra, a.linha) for a in alertas], [("GO-2", 2)])


class ParagrafoLongo(unittest.TestCase):
    def test_paragrafo_acima_do_limiar_de_palavras(self):
        alertas = lint.lint_texto(corpo(" ".join(["prazo"] * 130) + "."))
        self.assertEqual([a.regra for a in alertas], ["GO-4/paragrafo"])
        self.assertIn("130 palavras", alertas[0].mensagem)

    def test_paragrafo_curto_nao_dispara(self):
        self.assertEqual(regras(corpo(" ".join(["prazo"] * 40) + ".")), [])

    def test_limiares_configuraveis(self):
        texto = corpo(" ".join(["prazo"] * 50) + ".")
        self.assertEqual(regras(texto), [])
        self.assertEqual(regras(texto, max_palavras=40), ["GO-4/paragrafo"])

    def test_entre_referencia_e_limite_e_aviso_brando(self):
        alertas = lint.lint_texto(corpo(" ".join(["prazo"] * 125) + "."))
        self.assertEqual([a.regra for a in alertas], ["GO-4/paragrafo"])
        self.assertIn("Mantenha se for uma ideia só", alertas[0].mensagem)

    def test_acima_do_limite_sugere_quebrar(self):
        alertas = lint.lint_texto(corpo(" ".join(["prazo"] * 140) + "."))
        self.assertEqual([a.regra for a in alertas], ["GO-4/paragrafo"])
        self.assertIn("mais de uma ideia", alertas[0].mensagem)

    def test_periodos_demais_so_em_paragrafo_cheio(self):
        self.assertEqual(regras(corpo("Primeiro ponto. Segundo ponto. Terceiro ponto.")), [])
        trecho = " ".join(["prazo"] * 30)
        cheio = corpo(f"A primeira frase tem {trecho}. A segunda frase tem {trecho}. "
                      f"A terceira frase tem {trecho}.")
        alertas = lint.lint_texto(cheio)
        self.assertEqual([a.regra for a in alertas], ["GO-4/paragrafo"])
        self.assertIn("3 períodos", alertas[0].mensagem)


class MediaDosParagrafos(unittest.TestCase):
    ABERTURAS = ["Primeiro", "Segundo", "Terceiro", "Quarto", "Quinto", "Sexto"]

    def peca(self, palavras, n=6):
        return corpo(*[f"{w} " + " ".join(["prazo"] * (palavras - 1)) + "."
                       for w in self.ABERTURAS[:n]])

    def test_media_na_faixa_nao_dispara(self):
        self.assertEqual(regras(self.peca(80)), [])

    def test_media_acima_da_faixa(self):
        alertas = lint.lint_texto(self.peca(100))
        self.assertEqual([a.regra for a in alertas], ["GO-4/media"])
        self.assertIn("acima da faixa-alvo de 70 a 90", alertas[0].mensagem)

    def test_media_abaixo_da_faixa(self):
        self.assertEqual(regras(self.peca(40)), ["GO-4/media"])

    def test_peca_curta_nao_avalia_media(self):
        self.assertEqual(regras(self.peca(100, n=3)), [])

    def test_faixa_configuravel(self):
        self.assertEqual(regras(self.peca(100), media_min=90, media_max=110), [])

    def test_estatisticas(self):
        est = lint.estatisticas(lint.segmentar(self.peca(80)))
        self.assertEqual((est["paragrafos"], est["media_palavras"], est["maior"]), (6, 80.0, 80))


class AberturasIguais(unittest.TestCase):
    def test_tres_aberturas_iguais(self):
        alertas = lint.lint_texto(corpo("Com efeito, a primeira.", "Com efeito, a segunda.",
                                        "Com efeito, a terceira."))
        self.assertEqual([(a.regra, a.linha) for a in alertas], [("GO-4/aberturas", 6)])

    def test_duas_aberturas_iguais_nao_disparam(self):
        self.assertEqual(regras(corpo("Com efeito, a primeira.", "Com efeito, a segunda.",
                                      "Além disso, a terceira.")), [])

    def test_titulo_reinicia_a_contagem(self):
        texto = (corpo("Com efeito, a primeira.", "Com efeito, a segunda.")
                 + "\n@secao\n2. DO MÉRITO\n\n" + corpo("Com efeito, a terceira."))
        self.assertEqual(regras(texto), [])

    def test_citacao_entre_paragrafos_nao_reinicia(self):
        texto = (corpo("Nesse sentido, a primeira.", "Nesse sentido, a segunda.")
                 + "\n@citacao\nEmenta qualquer.\n\n" + corpo("Nesse sentido, a terceira."))
        self.assertEqual(regras(texto), ["GO-4/aberturas"])

    def test_mesma_estrutura_sem_conectivo(self):
        self.assertEqual(regras(corpo("A decisão afirmou um ponto.", "A decisão negou outro.",
                                      "A decisão omitiu o terceiro.")), ["GO-4/aberturas"])


class Lexico(unittest.TestCase):
    def test_registro_ensaistico(self):
        r = regras(corpo("O segundo requisito é o que melhor revela o descompasso da apelação."))
        self.assertEqual(r, ["GO-5/ensaio", "GO-5/ensaio"])

    def test_lexico_em_citacao_nao_dispara(self):
        self.assertEqual(regras("@citacao\nIsso salta aos olhos.\n"), [])

    def test_metadiscurso_estrategico(self):
        self.assertEqual(regras(corpo("O que se admite apenas para argumentar.")),
                         ["GO-5/metadiscurso"])

    def test_indignacao_e_ataque_ao_julgador(self):
        self.assertEqual(regras(corpo("A decisão é teratológica.")), ["persuasao/indignacao"])
        self.assertEqual(regras(corpo("O magistrado ignorou os embargos.")), ["persuasao/julgador"])

    def test_metalinguagem_e_enumeracao_andaime(self):
        self.assertEqual(regras(corpo("Passa-se agora à análise da segunda tese.")),
                         ["revisao/metalinguagem"])
        self.assertEqual(regras(corpo("A pretensão se sustenta por duas razões.",
                                      "Primeiro, porque o contrato não previu reajuste.")),
                         ["revisao/andaime", "revisao/andaime"])

    def test_anuncio_de_citacao_da_casa_nao_dispara(self):
        self.assertEqual(regras(corpo("Nesse sentido, vejamos:")), [])

    def test_lexico_da_casa(self):
        self.assertEqual(regras(corpo("A impetração foi tempestiva.")), ["casa/lexico"])

    def test_saturacao_de_venia(self):
        dois = corpo("Data venia, a premissa falha.", "Data venia, a conclusão também.")
        self.assertEqual(regras(dois), [])
        tres = corpo("Data venia, a premissa falha.", "Com a devida vênia, a conclusão também.",
                     "Por fim, data venia, o dispositivo.")
        alertas = lint.lint_texto(tres)
        self.assertEqual([(a.regra, a.linha) for a in alertas], [("cortesia/saturacao", 6)])

    def test_vocativo_acima_da_dose(self):
        texto = corpo("Importante frisar, Ex.ª, que a premissa falha.",
                      "Note-se, Ex.ª, que o prazo correu.", "Registre-se, Ex.ª, que nada mudou.")
        self.assertEqual(regras(texto), ["padrao/vocativo"])


class DefinicaoPorNegacao(unittest.TestCase):
    def test_nao_e_x_mas_y(self):
        self.assertEqual(regras(corpo("A usina não é projeto anunciado, mas empreendimento "
                                      "regularmente outorgado.")), ["GO-6"])

    def test_nao_se_trata_de_conta_uma_vez(self):
        self.assertEqual(regras(corpo("Não se trata de mera irregularidade, mas de nulidade.")),
                         ["GO-6"])
        self.assertEqual(regras(corpo("Não se trata de mera irregularidade.")), ["GO-6"])

    def test_nao_so_mas_tambem_nao_dispara(self):
        self.assertEqual(regras(corpo("A cláusula não é apenas válida, mas também eficaz.")), [])


class OMesmo(unittest.TestCase):
    def test_pronome_seguido_de_verbo_ou_pontuacao(self):
        self.assertEqual(regras(corpo("O contrato foi assinado, e o mesmo previa multa.")),
                         ["precisao/o-mesmo"])
        self.assertEqual(regras(corpo("A parte juntou o laudo e impugnou o mesmo.")),
                         ["precisao/o-mesmo"])

    def test_adjetivo_e_locucoes_nao_disparam(self):
        texto = corpo("O mesmo dispositivo e a mesma Turma, ao mesmo tempo e do mesmo modo, "
                      "decidiram. A petição é a mesma que foi juntada.")
        self.assertEqual(regras(texto), [])


class LinhaDeComando(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.peca = Path(self.dir.name) / "peca.md"
        self.peca.write_text("@corpo\nA decisão — fundamentada — saiu.\n", encoding="utf-8")

    def rodar(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True)

    def test_json(self):
        r = self.rodar(str(self.peca), "--json")
        self.assertEqual(r.returncode, 0)
        dados = json.loads(r.stdout.decode("utf-8"))
        self.assertEqual(dados["resumo"], {"GO-2": 2})
        self.assertEqual(dados["alertas"][0]["linha"], 2)

    def test_saida_legivel_aponta_arquivo_linha_e_regra(self):
        saida = self.rodar(str(self.peca)).stdout.decode("utf-8")
        self.assertIn(f"{self.peca}:2: [GO-2]", saida)
        self.assertIn("2 alerta(s) em 1 arquivo(s)", saida)

    def test_pasta_e_ignorar(self):
        r = self.rodar(self.dir.name, "--ignorar", "GO-2", "--json")
        self.assertEqual(json.loads(r.stdout.decode("utf-8"))["alertas"], [])

    def test_arquivo_inexistente_sai_com_2(self):
        self.assertEqual(self.rodar(str(Path(self.dir.name) / "nao-existe.md")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
