"""Testes do orquestrador. Rodar: python3 tests/test_elaborar.py"""

import sys, pathlib, tempfile, os
from decimal import Decimal
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "skills" / "elaborador-inicial" / "scripts"))
sys.path.insert(0, str(RAIZ / "tests"))

from classificar import Fato  # noqa: E402
from elaborar import (  # noqa: E402
    Caso, elaborar, TRIAGEM, CONFIRMACAO, CALCULO, REDACAO, GERACAO, CONCLUIDO,
)
from test_calcular import CASO_REAL  # noqa: E402
from test_gerar import modelo  # noqa: E402


FATOS = {"F1": Fato("AUTOGESTAO", "carteira", "CASSI", 0.95),
         "F2": Fato("PF_DIRETO", "contrato", "", 0.9),
         "F6": Fato("ATIVO", "demonstrativo", "", 0.9),
         "F7": Fato("SIM", "planilha", "", 0.9),
         "F9": Fato("81", "documento", "81 anos", 0.9),
         "F10": Fato("NAO", "informado", "", 0.9)}
DADOS = {"plano": "PLANO X", "inicio_contrato": "07/05/2001", "idade": "81",
         "comarca": "Salvador/BA", "competencia_atual": "julho de 2026",
         "maior_reajuste": "29,90%", "valor_da_causa": "R$ 51.170,42",
         "narrativa_hipossuficiencia": "Demonstrada nos autos."}
ACEITA = {(2018, 4): Decimal("0"), (2021, 1): Decimal("0")}


def caso_completo(diretorio):
    return Caso(cliente="Fulana", modelo_docx=modelo(diretorio),
                saida_docx=os.path.join(diretorio, "peca.docx"),
                competencias=CASO_REAL, mes_aniversario=7,
                faixa_etaria_aceita=dict(ACEITA), tese_confirmada="CASSI_AUTOGESTAO",
                fatos=dict(FATOS), dados=dict(DADOS))


# ------------------------------------------------------------------- fases ----

def test_fluxo_completo_termina_em_documento():
    with tempfile.TemporaryDirectory() as t:
        e = elaborar(caso_completo(t))
        assert e.fase == CONCLUIDO, (e.fase, e.perguntas)
        assert os.path.exists(e.docx)
        assert e.conferencia.liberado


def test_fluxo_por_etapas_converge():
    """Como a operadora usa de verdade: responde uma coisa por vez."""
    with tempfile.TemporaryDirectory() as t:
        caso = Caso(cliente="Fulana", modelo_docx=modelo(t),
                    saida_docx=os.path.join(t, "peca.docx"), competencias=CASO_REAL)
        fases = []
        for _ in range(10):
            e = elaborar(caso)
            fases.append(e.fase)
            if e.concluido:
                break
            if e.fase == TRIAGEM:
                caso.fatos.update(FATOS)
            elif e.fase == CONFIRMACAO:
                caso.tese_confirmada = e.dossie["eixo_b"]["tese"]
            elif e.fase == CALCULO:
                if caso.mes_aniversario is None:
                    caso.mes_aniversario = 7
                else:
                    caso.faixa_etaria_aceita = dict(ACEITA)
            elif e.fase == REDACAO:
                caso.dados.update(DADOS)
        assert fases[-1] == CONCLUIDO, fases
        assert fases.index(TRIAGEM) < fases.index(CONFIRMACAO) < fases.index(CALCULO)


def test_nao_gera_sem_confirmacao_da_tese():
    """G8: confiança alta não dispensa o Espelho."""
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.tese_confirmada = ""
        e = elaborar(caso)
        assert e.fase == CONFIRMACAO and e.travado
        assert not e.docx


def test_confirmacao_de_outra_tese_nao_destrava():
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.tese_confirmada = "INDIVIDUAL_COMUM"      # não é a classificada
        assert elaborar(caso).fase == CONFIRMACAO


def test_gate_do_classificador_trava_na_triagem():
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        del caso.fatos["F1"]                            # operadora não identificada
        e = elaborar(caso)
        assert e.fase == TRIAGEM and e.travado
        assert any("autogestão" in p for p in e.perguntas)


def test_gate_respondido_destrava_sem_mudar_fato():
    """Alguns gates não se resolvem preenchendo fato — a resposta é da operadora."""
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.competencias = []
        travado = elaborar(caso)
        assert travado.fase == TRIAGEM
        caso.respostas["G5-ausente"] = "não existe cálculo neste caso"
        assert elaborar(caso).fase != TRIAGEM


def test_pendencia_de_faixa_etaria_trava_no_calculo():
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.faixa_etaria_aceita = {}
        e = elaborar(caso)
        assert e.fase == CALCULO and len(e.perguntas) == 2
        assert all("faixa etária" in p for p in e.perguntas)


def test_mes_de_aniversario_e_perguntado_antes_de_calcular():
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.mes_aniversario = None
        e = elaborar(caso)
        assert e.fase == CALCULO and "aniversário" in e.perguntas[0]


def test_campo_sem_valor_trava_na_redacao_listando_tudo():
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        del caso.dados["plano"], caso.dados["idade"]
        e = elaborar(caso)
        assert e.fase == REDACAO
        assert "plano" in e.perguntas[0] and "idade" in e.perguntas[0]


def test_modelo_ausente_trava_na_geracao():
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.modelo_docx = os.path.join(t, "inexistente.docx")
        e = elaborar(caso)
        assert e.fase == GERACAO and "timbre" in e.perguntas[0]


# ---------------------------------------------------------------- espelho ----

def test_espelho_final_traz_classificacao_calculo_peca_e_conferencia():
    with tempfile.TemporaryDirectory() as t:
        e = elaborar(caso_completo(t))
        for secao in ("ESPELHO DE CLASSIFICAÇÃO", "Cálculo", "Peça", "CONFERÊNCIA"):
            assert secao in e.espelho, secao
        assert "R$ 38.576,42" in e.espelho, "a restituição calculada tem que aparecer"
        assert "12 capítulos" in e.espelho
        assert "tudo fecha" in e.espelho


def test_espelho_final_nao_repete_o_pedido_de_confirmacao():
    with tempfile.TemporaryDirectory() as t:
        e = elaborar(caso_completo(t))
        assert "Confirma a tese" not in e.espelho


def test_espelho_de_confirmacao_pede_confirmacao():
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.tese_confirmada = ""
        assert "Confirma a tese" in elaborar(caso).espelho


def test_aviso_de_texto_nao_revisado_chega_ao_espelho():
    """Tese redigida a partir dos fundamentos não pode passar em silêncio."""
    with tempfile.TemporaryDirectory() as t:
        caso = caso_completo(t)
        caso.fatos["F1"] = Fato("COMERCIAL", "carteira", "", 0.95)
        caso.tese_confirmada = "INDIVIDUAL_COMUM"
        e = elaborar(caso)
        assert e.avisos, "deveria avisar que o texto não foi lido por advogado"
        assert "ATENÇÃO" in e.espelho


def test_documentos_vazios_nao_somem_em_silencio():
    with tempfile.TemporaryDirectory() as t:
        e = elaborar(caso_completo(t))
        assert "nenhum arquivo enviado" in e.espelho


if __name__ == "__main__":
    import traceback
    testes = [(n, o) for n, o in sorted(globals().items())
              if n.startswith("test_") and callable(o)]
    falhas = 0
    for nome, fn in testes:
        try:
            fn(); print(f"  ok    {nome}")
        except Exception:
            falhas += 1; print(f"  FALHA {nome}"); traceback.print_exc()
    print(f"\n{len(testes)-falhas}/{len(testes)} passaram")
    raise SystemExit(1 if falhas else 0)
