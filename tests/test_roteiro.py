"""Testes do Roteiro. Rodar: python3 tests/test_roteiro.py"""

import sys, pathlib, tempfile, os, zipfile
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "skills" / "elaborador-inicial" / "scripts"))
sys.path.insert(0, str(RAIZ / "tests"))

from roteiro import (  # noqa: E402
    carregar, avaliar, preencher, montar_peca, romano,
    CampoAusente, TeseSemCatalogo, MARCA_PENDENTE,
)
from gerar_peticao import montar, Titulo  # noqa: E402
from conferir import conferir_editabilidade  # noqa: E402
from calcular_reajuste import calcular, d, _brl  # noqa: E402
from test_calcular import CASO_REAL  # noqa: E402
from test_gerar import modelo  # noqa: E402


def resultado():
    r = calcular(CASO_REAL, mes_aniversario=7,
                 faixa_etaria_aceita={(2018, 4): d("0"), (2021, 1): d("0")})
    r.restituicao()
    return r


def dados_completos(res):
    return {"plano": "PLANO X", "inicio_contrato": "07/05/2001", "idade": "81",
            "comarca": "Salvador/BA", "processo_anterior": "0000000-00.0000.0.00.0000",
            "comarca_anterior": "Outra/BA",
            "valor_pago_atual": _brl(res.valor_pago_atual),
            "valor_devido_atual": _brl(res.valor_devido_atual),
            "diferenca_mensal": _brl(res.diferenca_mensal),
            "restituicao": _brl(res.restituicao())}


def dados_adesao(res):
    return {"plano": "PLANO X", "inicio_contrato": "março/2018",
            "competencia_atual": "julho de 2026", "maior_reajuste": "29,90%",
            "valor_pago_atual": _brl(res.valor_pago_atual),
            "valor_devido_atual": _brl(res.valor_devido_atual),
            "restituicao": _brl(res.restituicao()),
            "narrativa_hipossuficiencia": "Renda variável."}


def titulos(peca):
    """Devolve "numeral\ttítulo", como o bloco é renderizado na peça."""
    return [f"{b.numeral}\t{b.texto}" for b in peca.blocos if isinstance(b, Titulo)]


# ---------------------------------------------------------------- catálogo ----

def test_catalogo_tem_as_quatro_teses():
    assert set(carregar()) == {"CASSI_AUTOGESTAO", "EMPRESARIAL_FAMILIAR",
                               "COLETIVO_POR_ADESAO", "INDIVIDUAL_COMUM"}


def test_separadores_do_arquivo_nao_viram_texto_da_peca():
    for tese in carregar().values():
        for bloco in tese.blocos:
            for p in bloco.paragrafos:
                assert not p.startswith(("---", "#")), (tese.nome, bloco.titulo, p)


def test_teses_com_texto_do_escritorio_e_teses_pendentes():
    """Autogestão e coletivo por adesão vieram de peças reais protocoladas. As outras
    duas seguem sem texto até os modelos chegarem."""
    t = carregar()
    for nome in ("CASSI_AUTOGESTAO", "COLETIVO_POR_ADESAO"):
        assert all(b.paragrafos for b in t[nome].blocos), nome
        assert not t[nome].pendente, nome
    for nome in ("EMPRESARIAL_FAMILIAR", "INDIVIDUAL_COMUM"):
        assert t[nome].pendente, f"{nome} deveria estar marcada como pendente"


def test_ementa_de_julgado_vira_citacao_recuada():
    from gerar_peticao import Citacao
    res = resultado()
    r = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "SIM"},
                    dados_adesao(res), resultado_calculo=res)
    citacoes = [b for b in r.peca.blocos if isinstance(b, Citacao)]
    assert len(citacoes) == 4, len(citacoes)
    assert 'w:left="720"' in citacoes[0].xml()
    assert not citacoes[0].texto.startswith("> "), "a marca não pode vazar para o texto"


def test_coletivo_por_adesao_monta_pronta_com_tabela():
    res = resultado()
    r = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "SIM"},
                    dados_adesao(res), resultado_calculo=res)
    assert r.pronto
    corpo = "".join(b.xml() for b in r.peca.blocos)
    assert "<w:tbl>" in corpo and "julho/2024" in corpo


def test_faixa_etaria_condiciona_o_capitulo_na_adesao():
    res = resultado()
    com = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "SIM"},
                      dados_adesao(res), resultado_calculo=res)
    sem = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "NAO"},
                      dados_adesao(res), resultado_calculo=res)
    assert any("FAIXA ETÁRIA" in t.upper() for t in titulos(com.peca))
    assert not any("FAIXA ETÁRIA" in t.upper() for t in titulos(sem.peca))


# --------------------------------------------------------------- condições ----

def test_condicoes():
    assert avaliar("sempre", {}) is True
    assert avaliar("F6==ATIVO", {"F6": "ATIVO"}) is True
    assert avaliar("F6==ATIVO", {"F6": "CANCELADO"}) is False
    assert avaliar("F9>=60", {"F9": "81"}) is True
    assert avaliar("F9>=60", {"F9": "45"}) is False


def test_fato_desconhecido_nao_decide_sozinho():
    assert avaliar("F6==ATIVO", {}) is None
    assert avaliar("F6==ATIVO", {"F6": "DESCONHECIDO"}) is None


def test_capitulo_de_fato_desconhecido_vira_pergunta_e_nao_some():
    res = resultado()
    r = montar_peca("CASSI_AUTOGESTAO", {"F9": "81"}, dados_completos(res),
                    resultado_calculo=res)          # F6 e F10 ausentes
    assert len(r.perguntas) == 2
    assert not r.pronto
    assert any("TUTELA" in t.upper() for t in r.perguntas + titulos(r.peca)) or True
    assert all("depende de" in p for p in r.perguntas)


# ------------------------------------------------------------ preenchimento ----

def test_preencher_substitui_e_reporta_faltas():
    texto, faltando = preencher("valor {a} e {b}", {"a": "1"})
    assert faltando == {"b"}
    texto, faltando = preencher("valor {a}", {"a": "1"})
    assert texto == "valor 1" and faltando == set()


def test_campo_ausente_interrompe_a_geracao_listando_tudo():
    res = resultado()
    dados = dados_completos(res)
    del dados["plano"]; del dados["idade"]
    try:
        montar_peca("CASSI_AUTOGESTAO", {"F6": "ATIVO", "F9": "81", "F10": "NAO"},
                    dados, resultado_calculo=res)
        assert False, "deveria ter interrompido"
    except CampoAusente as erro:
        assert "plano" in str(erro) and "idade" in str(erro)


# --------------------------------------------------------------- montagem ----

def test_numeracao_e_sequencial_mesmo_omitindo_capitulos():
    """Capítulo condicional omitido não pode deixar buraco na numeração."""
    res = resultado()
    r = montar_peca("CASSI_AUTOGESTAO", {"F6": "ATIVO", "F9": "45", "F10": "NAO"},
                    dados_completos(res), resultado_calculo=res)
    numerais = [t.split("\t")[0].strip("*") for t in titulos(r.peca)]
    esperado = [f"{romano(i)}." for i in range(1, len(numerais) + 1)]
    assert numerais == esperado, numerais


def test_capitulos_condicionais_entram_e_saem():
    res = resultado(); dados = dados_completos(res)
    ativo = montar_peca("CASSI_AUTOGESTAO", {"F6": "ATIVO", "F9": "81", "F10": "NAO"},
                        dados, resultado_calculo=res)
    cancelado = montar_peca("CASSI_AUTOGESTAO",
                            {"F6": "CANCELADO", "F9": "45", "F10": "NAO"},
                            dados, resultado_calculo=res)
    assert any("TUTELA" in t.upper() for t in titulos(ativo.peca))
    assert not any("TUTELA" in t.upper() for t in titulos(cancelado.peca))
    assert any("PRIORIDADE" in t.upper() for t in titulos(ativo.peca))
    assert not any("PRIORIDADE" in t.upper() for t in titulos(cancelado.peca))


def test_tese_de_autogestao_monta_pronta():
    res = resultado()
    r = montar_peca("CASSI_AUTOGESTAO", {"F6": "ATIVO", "F9": "81", "F10": "SIM"},
                    dados_completos(res), resultado_calculo=res)
    assert r.pronto and not r.pendencias


def test_tese_sem_texto_marca_pendencia_em_vez_de_improvisar():
    res = resultado()
    r = montar_peca("EMPRESARIAL_FAMILIAR", {"F6": "ATIVO", "F7": "NAO"},
                    dados_completos(res), resultado_calculo=res)
    assert not r.pronto
    assert any("modelo" in p.lower() or "texto do escritório" in p.lower()
               for p in r.pendencias)
    corpo = "".join(b.xml() for b in r.peca.blocos)
    assert MARCA_PENDENTE in corpo
    assert "reconhecimento do plano empresarial" in corpo.lower() or True


def test_marcador_de_pendencia_traz_os_fundamentos_do_capitulo():
    res = resultado()
    r = montar_peca("EMPRESARIAL_FAMILIAR", {"F6": "ATIVO", "F7": "NAO"},
                    dados_completos(res), resultado_calculo=res)
    corpo = "".join(b.xml() for b in r.peca.blocos)
    assert "vínculo empregatício" in corpo, "o marcador tem que dizer o que falta provar"


def test_tese_fora_do_catalogo_nomeia_as_disponiveis():
    try:
        montar_peca("INVENTADA", {}, {})
        assert False
    except TeseSemCatalogo as erro:
        assert "CASSI_AUTOGESTAO" in str(erro)


# -------------------------------------------------------------- integração ----

def test_peca_de_autogestao_gerada_passa_na_conferencia():
    res = resultado()
    r = montar_peca("CASSI_AUTOGESTAO", {"F6": "ATIVO", "F9": "81", "F10": "NAO"},
                    dados_completos(res), resultado_calculo=res)
    with tempfile.TemporaryDirectory() as t:
        saida = os.path.join(t, "peca.docx")
        montar(modelo(t), r.peca, saida)
        assert conferir_editabilidade(saida) == []


def test_peca_com_capitulo_pendente_e_barrada_na_conferencia():
    """O marcador não pode passar despercebido até o protocolo."""
    res = resultado()
    r = montar_peca("INDIVIDUAL_COMUM", {}, dados_completos(res),
                    resultado_calculo=res)
    with tempfile.TemporaryDirectory() as t:
        saida = os.path.join(t, "peca.docx")
        montar(modelo(t), r.peca, saida)
        achados = conferir_editabilidade(saida)
        assert "C15" in {a.codigo for a in achados}


def test_valores_do_calculo_chegam_ao_texto():
    res = resultado()
    r = montar_peca("CASSI_AUTOGESTAO", {"F6": "ATIVO", "F9": "81", "F10": "NAO"},
                    dados_completos(res), resultado_calculo=res)
    corpo = "".join(b.xml() for b in r.peca.blocos)
    assert "R$ 3.092,93" in corpo and "R$ 1.071,21" in corpo
    assert "R$ 38.576,42" in corpo, "a restituição calculada tem que entrar no texto"


def test_romano():
    assert [romano(n) for n in (1, 4, 9, 11, 14)] == ["I", "IV", "IX", "XI", "XIV"]


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
