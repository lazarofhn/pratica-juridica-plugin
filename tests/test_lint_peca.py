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
        self.assertEqual(regras(self.peca(55)), [])

    def test_media_acima_da_faixa(self):
        alertas = lint.lint_texto(self.peca(80))
        self.assertEqual([a.regra for a in alertas], ["GO-4/media"])
        self.assertIn("acima da faixa-alvo de 45 a 65", alertas[0].mensagem)

    def test_media_abaixo_da_faixa_nao_manda_alongar(self):
        alertas = lint.lint_texto(self.peca(30))
        self.assertEqual([a.regra for a in alertas], ["GO-4/media"])
        self.assertIn("não alongue parágrafo", alertas[0].mensagem)

    def test_peca_curta_nao_avalia_media(self):
        self.assertEqual(regras(self.peca(100, n=3)), [])

    def test_faixa_configuravel(self):
        self.assertEqual(regras(self.peca(100), media_min=90, media_max=110), [])

    def test_estatisticas(self):
        est = lint.estatisticas(lint.segmentar(self.peca(55)))
        self.assertEqual((est["paragrafos"], est["media_palavras"], est["maior"]), (6, 55.0, 55))


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


class AberturaSemConectivo(unittest.TestCase):
    RESTO = " ".join(["prazo"] * 51) + "."   # cerca de 55 palavras: média na faixa

    def par(self, abertura):
        return f"{abertura} {self.RESTO}"

    def test_sequencia_e_parcela_disparam(self):
        texto = corpo(self.par("O MPF imputou"), self.par("O acórdão manteve"),
                      self.par("Essa conclusão ignora"), self.par("Diante disso, a defesa"),
                      self.par("Ainda assim, o tribunal"), self.par("A sentença acolheu"))
        alertas = lint.lint_texto(texto)
        self.assertEqual([(a.regra, a.linha) for a in alertas],
                         [("GO-1/abertura", 2), ("GO-1/abertura", 6)])
        self.assertIn("4 de 6 parágrafos (67%) abrem sem conectivo (1 por demonstrativo)",
                      alertas[0].mensagem)
        self.assertIn("linhas 2, 4, 6", alertas[1].mensagem)

    def test_texto_ligado_nao_dispara(self):
        texto = corpo(self.par("Na denúncia, o MPF imputou"), self.par("Ainda assim, o acórdão"),
                      self.par("Todavia, a sindicância"), self.par("O tribunal, contudo,"),
                      self.par("Quanto ao dolo, a sentença"), self.par("Diante disso, a defesa"))
        self.assertEqual(regras(texto), [])

    def test_metade_sem_conectivo_e_tolerada(self):
        # 3 de 6 (50%) não passa do teto de cerca de metade; 4 de 6 passa (teste acima)
        texto = corpo(self.par("O MPF imputou"), self.par("Diante disso, a defesa"),
                      self.par("A sentença acolheu"), self.par("Ainda assim, o tribunal"),
                      self.par("Esse acórdão manteve"), self.par("Portanto, a prova"))
        self.assertEqual(regras(texto), [])

    def test_titulo_e_citacao_reiniciam_a_sequencia(self):
        texto = (corpo(self.par("Na denúncia, o MPF"), self.par("O acórdão manteve"),
                       self.par("A sentença acolheu"))
                 + "\n@secao\n2. DO MÉRITO\n\n"
                 + corpo(self.par("O tribunal negou"), self.par("A parte recorreu"))
                 + "\n@citacao\nEmenta qualquer.\n\n"
                 + corpo(self.par("O caso dos autos"), self.par("Diante disso, a defesa")))
        self.assertEqual(regras(texto, max_abertura_nominal=100), [])

    def test_apresentacao_de_citacao_nao_conta(self):
        texto = corpo(self.par("A ação volta-se"),
                      "O Superior Tribunal de Justiça já enfrentou a questão em caso idêntico:"
                      ) + "\n@citacao\nEmenta qualquer.\n\n" + corpo(
            self.par("Esse é o caso"), self.par("Ademais, a lei"), self.par("Por isso, o dever"),
            self.par("Assim, a ameaça"), self.par("O lançamento é vinculado"))
        self.assertEqual(regras(texto), [])

    def test_peca_curta_nao_avalia(self):
        texto = corpo(self.par("O MPF imputou"), self.par("O acórdão manteve"),
                      self.par("A sentença acolheu"))
        self.assertEqual(regras(texto), [])

    def test_locucoes_e_retomadas_nao_contam_como_sujeito_nominal(self):
        for abertura in ("A partir disso, o acórdão", "Uma vez que a sentença", "A meu ver, o MPF",
                         "A despeito da prova", "O mesmo acórdão", "O que se discute",
                         "A essa altura, a defesa", "Diante disso, a sentença"):
            self.assertFalse(lint.abre_com_sujeito_nominal(abertura), abertura)
        for abertura in ("O MPF imputou", "A sentença acolheu", "Os autos revelam",
                         "Uma das premissas", "**O acórdão** manteve"):
            self.assertTrue(lint.abre_com_sujeito_nominal(abertura), abertura)

    def test_demonstrativo_conta_e_conectivo_posposto_nao(self):
        casos = {"Esse acórdão manteve": "demonstrativo", "Essa lógica impede": "demonstrativo",
                 "Tal registro é": "demonstrativo", "O MPF imputou": "nominal",
                 "A ordem postulada, contudo, dirige-se": None, "Impõe-se, assim, o": None,
                 'O pedido "d.2" não atribui ao mandado, portanto, efeito': None,
                 "Ademais, as receitas": None, "Nessa linha, o tribunal": None}
        for abertura, esperado in casos.items():
            self.assertEqual(lint.abertura_sem_conectivo(abertura), esperado, abertura)

    def test_estatisticas_trazem_as_parcelas(self):
        texto = corpo(self.par("O MPF imputou"), self.par("Diante disso, a defesa"),
                      self.par("Essa conclusão ignora"), self.par("Ainda assim, o tribunal"))
        est = lint.estatisticas(lint.segmentar(texto))
        self.assertEqual((est["aberturas_nominais_pct"], est["aberturas_sem_conectivo_pct"]),
                         (25, 50))


class Remissao(unittest.TestCase):
    def alertas(self, texto):
        return [a for a in lint.lint_texto(texto) if a.regra == "GO-1/remissao"]

    def test_remissao_que_constroi_o_passo_seguinte_fica(self):
        # Decisão do José (nov/2026): remeter ao que acabou de ser dito, para construir a
        # lógica, é legítimo; o vício é o referente longe da vista.
        texto = corpo("A omissão dos Ministérios impede o registro no cadastro.",
                      "Nessa perspectiva, a omissão compõe a causa de pedir.",
                      "O decreto confirmou esse quadro ao adiar o cadastro.")
        self.assertEqual(self.alertas(texto), [])

    def test_termo_repetido_da_frase_anterior_fica(self):
        texto = corpo("O decreto subordinou o cadastro a um ato conjunto dos Ministérios.",
                      "Esse ato conjunto não acrescenta condição ao benefício.")
        self.assertEqual(self.alertas(texto), [])

    def test_rotulo_nomeado_na_propria_frase_fica(self):
        texto = corpo("O acórdão excluiu o ressarcimento dos dois apelantes.",
                      "Essa ratio, que afastou o dano material e o moral, aproveita a todos.")
        self.assertEqual(self.alertas(texto), [])

    def test_termo_de_dois_paragrafos_atras(self):
        texto = corpo("O IRPJ é o tributo que incide sobre o lucro apurado no período.",
                      "A CSLL e a COFINS seguem a mesma apuração trimestral.",
                      "Este tributo, contudo, não alcança a receita de serviços ambientais.")
        alertas = self.alertas(texto)
        self.assertEqual(len(alertas), 1)
        self.assertIn("2 parágrafos atrás", alertas[0].mensagem)
        rotulo_distante = corpo("O STJ firmou entendimento sobre o justo receio.",
                                "A autoridade defendeu a exigência nas informações.",
                                "Ademais, a lei está em vigor.",
                                "Este entendimento aplica-se aos autos.")
        self.assertIn("3 parágrafos atrás", self.alertas(rotulo_distante)[0].mensagem)

    def test_remissao_atravessa_o_titulo(self):
        texto = (corpo("A sentença afastou o dano ao erário.")
                 + "\n@secao\n2. DO MÉRITO\n\n"
                 + corpo("Essa conclusão aproveita aos demais réus."))
        self.assertIn("abre o capítulo", self.alertas(texto)[0].mensagem)
        com_termo_no_titulo = (corpo("A sentença afastou o dano ao erário.")
                               + "\n@secao\n2. O REGISTRO NO CADASTRO\n\n"
                               + corpo("Esse registro é instrumento de fiscalização."))
        self.assertEqual(self.alertas(com_termo_no_titulo), [])

    def test_rotulo_de_decisao_logo_apos_a_citacao_fica(self):
        texto = (corpo("O STJ já enfrentou a questão:") + "\n@citacao\nEmenta qualquer.\n\n"
                 + corpo("Esse entendimento aplica-se aos autos, porque a exigência é a mesma."))
        self.assertEqual(self.alertas(texto), [])

    def test_deiticos_e_aspas_nao_disparam(self):
        texto = corpo("A Impetrante juntou a decisão.",
                      "Nesta ação, e neste ato, o pedido deste writ se limita ao ano corrente.",
                      'A lei fala em "esse conceito" e "nesse quadro" sem disciplina própria.')
        self.assertEqual(self.alertas(texto), [])


class DizerUmaVez(unittest.TestCase):
    CITACAO = ("@citacao\nEm matéria tributária, a vigência da lei instituidora do tributo, somada "
               "à natureza vinculada do lançamento, configura o justo receio apto a autorizar a "
               "impetração preventiva.\n\n")

    def regras7(self, texto):
        return [a.regra for a in lint.lint_texto(texto) if a.regra.startswith("GO-7")]

    def test_paragrafo_que_reconta_o_julgado(self):
        texto = (corpo("Por isso, a vigência da lei basta para o justo receio:") + self.CITACAO
                 + corpo("Nesse julgado, a Primeira Turma entendeu que a vigência da lei basta. "
                         "O Tribunal concluiu que não é preciso aguardar a autuação."))
        self.assertEqual(self.regras7(texto), ["GO-7/parafrase"])

    def test_corte_como_sujeito_que_decide(self):
        texto = (self.CITACAO + corpo("O Superior Tribunal de Justiça decidiu, assim, que a "
                                      "vigência da lei basta para o justo receio."))
        self.assertEqual(self.regras7(texto), ["GO-7/parafrase"])

    def test_aplicacao_ao_caso_fica(self):
        texto = (self.CITACAO + corpo("Esse é o caso dos autos, uma vez que a exigência vem "
                                      "declarada nas próprias informações (id 2294049828, p. 4)."))
        self.assertEqual(self.regras7(texto), [])

    def test_apresentacao_da_citacao_fica(self):
        texto = (corpo("O Superior Tribunal de Justiça já reconheceu que a vigência da lei "
                       "instituidora e o lançamento vinculado configuram o justo receio:")
                 + self.CITACAO)
        self.assertEqual(self.regras7(texto), [])

    def test_paragrafo_que_repete_as_palavras_da_citacao(self):
        texto = (self.CITACAO + corpo("A vigência da lei instituidora do tributo e a natureza "
                                      "vinculada do lançamento configuram o justo receio que "
                                      "autoriza a impetração preventiva."))
        self.assertEqual(self.regras7(texto), ["GO-7/parafrase"])

    def test_citacao_ref_compara_com_o_grifo(self):
        texto = ("@citacao-ref\nfonte: STJ\nprocesso: AgInt no AREsp 2.386.728\n"
                 "grifo: configura o justo receio do contribuinte apto a autorizar a impetração "
                 "preventiva\nref: STJ, Primeira Turma\n\n"
                 + corpo("O justo receio do contribuinte, portanto, está configurado, o que "
                         "autoriza a impetração preventiva."))
        self.assertEqual(self.regras7(texto), ["GO-7/parafrase"])

    def test_conclusao_repetida(self):
        conclusao = ("o art. 17 incide sobre os contratos da Impetrante nos termos em que foi "
                     "editado, e o registro, instrumento de fiscalização, não lhe pode ser "
                     "exigido enquanto não existir o meio de promovê-lo")
        texto = corpo(f"No mérito, {conclusao}.", "Ademais, o decreto adiou o cadastro.",
                      "Diante disso, a autoridade não pode lançar o tributo.",
                      f"Portanto, {conclusao}.")
        alertas = [a for a in lint.lint_texto(texto) if a.regra == "GO-7/repeticao"]
        self.assertEqual(len(alertas), 1)
        self.assertIn("repete o parágrafo da linha 2", alertas[0].mensagem)

    def test_reformulacao_so_a_partir_da_segunda(self):
        uma = corpo("O acórdão é genérico. Ou seja, serviria a qualquer processo.")
        duas = corpo("O acórdão é genérico. Ou seja, serviria a qualquer processo.",
                     "A omissão é relevante. Vale dizer, muda o resultado.")
        self.assertEqual(self.regras7(uma), [])
        self.assertEqual(self.regras7(duas), ["GO-7/reformulacao"])


class RemissoesNoParagrafo(unittest.TestCase):
    def regras(self, texto):
        return [a.regra for a in lint.lint_texto(texto) if a.regra == "GO-7/remissoes"]

    def test_tres_remissoes_no_texto_corrido(self):
        texto = corpo("O mandado de segurança preventivo é cabível (STJ, REsp 1.933.794), o que se "
                      "reafirmou no AgInt no REsp 2.245.419 e no RMS 44.021, à luz da Súmula 213.")
        self.assertEqual(self.regras(texto), ["GO-7/remissoes"])

    def test_duas_remissoes_e_trechos_entre_aspas_ficam(self):
        duas = corpo("O mandado de segurança preventivo é cabível (STJ, REsp 1.933.794; AgInt "
                     "no REsp 2.245.419).")
        aspas = corpo('A autoridade transcreve "RE 631.641, AI 360.461 e MS 29.374" sem análise.')
        self.assertEqual(self.regras(duas), [])
        self.assertEqual(self.regras(aspas), [])

    def test_mesmo_precedente_repetido_conta_uma_vez(self):
        texto = corpo("Como decidiu o STJ no REsp 1.933.794, o receio é justo; o REsp 1.933.794 "
                      "também afasta a Súmula 266.")
        self.assertEqual(self.regras(texto), [])


class PrecedenteEDecisaoContraria(unittest.TestCase):
    def regras7(self, texto):
        return [a.regra for a in lint.lint_texto(texto) if a.regra.startswith("GO-7")]

    def test_precedente_narrado_na_prosa(self):
        texto = corpo("Em causa com esse desenho, o Superior Tribunal de Justiça cassou acórdão que "
                      "remetera o contribuinte à injunção, por reconhecer que a eficácia da lei é "
                      "questão do próprio mandado de segurança (STJ, AgInt no RMS 53.659, "
                      "Primeira Turma).")
        self.assertEqual(self.regras7(texto), ["GO-7/precedente-narrado"])

    def test_corroboracao_curta_e_trecho_literal_ficam(self):
        curta = corpo("A vigência da lei basta para configurar o justo receio, como assentou o "
                      "STJ (REsp 1.933.794).")
        literal = corpo('O STJ afastou o óbice, por reconhecer que "o papel do regulamento é '
                        'secundário" (STJ, REsp 1.046.475).')
        self.assertEqual(self.regras7(curta), [])
        self.assertEqual(self.regras7(literal), [])

    def test_transcricao_de_decisao_da_parte_contraria(self):
        texto = (corpo("A sentença invocada pela autoridade acolhe a premissa da Impetrante:")
                 + "\n@citacao-ref\nfonte: autos\ndoc: 33\ntrecho: de \"A ausência\" ate "
                 "\"realizada.\"\nref: Sentença no MS 1003688, transcrita nas informações\n\n")
        self.assertIn("GO-7/decisao-contraria", self.regras7(texto))

    def test_precedente_favoravel_em_bloco_nao_dispara(self):
        texto = ("@citacao-ref\nfonte: STJ\nprocesso: EREsp 1770495\nitens: 2\n"
                 "ref: STJ, EREsp 1.770.495, Primeira Seção\n\n"
                 + corpo("O pedido d.2, portanto, não produz efeito patrimonial pretérito."))
        self.assertEqual(self.regras7(texto), [])

    def test_decisoes_contrarias_em_tres_paragrafos(self):
        tres = corpo("Os precedentes invocados pela autoridade tratam de situação diversa.",
                     "Ademais, a lei define o beneficiário.",
                     "As sentenças transcritas nas informações são de primeiro grau.",
                     "Assim, a ordem deve ser concedida.",
                     "Ora, o precedente trazido pela própria autoridade acolhe a premissa.")
        duas = corpo("Os precedentes trazidos nas informações estão ultrapassados.",
                     "Ademais, a lei define o beneficiário.",
                     "Assim, os precedentes das informações não se aplicam.")
        self.assertEqual(self.regras7(tres), ["GO-7/decisao-contraria"])
        self.assertEqual(self.regras7(duas), [])


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
        self.assertIn("aberturas sem conectivo: 100% (teto 50%)", saida)

    def test_pasta_e_ignorar(self):
        r = self.rodar(self.dir.name, "--ignorar", "GO-2", "--json")
        self.assertEqual(json.loads(r.stdout.decode("utf-8"))["alertas"], [])

    def test_arquivo_inexistente_sai_com_2(self):
        self.assertEqual(self.rodar(str(Path(self.dir.name) / "nao-existe.md")).returncode, 2)


if __name__ == "__main__":
    unittest.main()
