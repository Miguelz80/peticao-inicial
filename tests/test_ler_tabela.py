"""Testes do leitor de tabela. Rodar: python3 tests/test_ler_tabela.py"""

import sys, pathlib
from decimal import Decimal
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "skills" / "elaborador-inicial" / "scripts"))
sys.path.insert(0, str(RAIZ / "tests"))

from ler_tabela import (  # noqa: E402
    competencia_da_linha, analisar, linhas_de_texto, competencias_de,
    conferir_importado,
)
from calcular_reajuste import calcular, d, ANUAL, FAIXA_ETARIA, INDEFINIDO  # noqa: E402


# Texto no formato em que a planilha do escritório sai do PDF.
TEXTO = """Cliente FULANA Resultado Total
Mês/Ano Valor Pago Reajuste Aplicado Tipo de Reajuste Reajuste Devido Valor Devido Diferença
janeiro/2015 -R$ 0,01-   - 0,00% -R$ -  - -R$ 0,01-
março/2018 -R$ 605,45-   -% 0,00% -R$ 605,45- -R$ -  -
abril/2018 -R$ 660,54-  9,10% 0,00% -R$ 605,45- -R$ 55,09-
julho/2018 -R$ 762,92-  15,50% Anual 10,00% -R$ 666,00- -R$ 96,93-
julho/2019 -R$ 883,00-  15,74% Anual 7,35% -R$ 714,95- -R$ 168,05-
"""


def test_competencia_por_nome_e_por_numero():
    assert competencia_da_linha("julho/2024 R$ 1,00") == (2024, 7)
    assert competencia_da_linha("07/2024 R$ 1,00") == (2024, 7)
    assert competencia_da_linha("marco/2018 x") == (2018, 3), "sem acento também"
    assert competencia_da_linha("sem data aqui") is None


def test_analisar_separa_valores_percentuais_e_tipo():
    a = analisar("julho/2018 -R$ 762,92- 15,50% Anual 10,00% -R$ 666,00- -R$ 96,93-")
    assert a["valores"] == [d("762,92"), d("666,00"), d("96,93")]
    assert a["percentuais"] == ["15,50", "10,00"]
    assert a["tipo"].lower() == "anual"


def test_linhas_de_texto_alimenta_o_eixo_a():
    """O Eixo A decide o regime pelo preenchimento das colunas de devido — sem estas
    linhas, cálculo pronto vira AMBIGUO e trava o caso sem motivo."""
    import classificar as cls
    linhas = linhas_de_texto(TEXTO)
    assert len(linhas) == 5
    pl = cls.Planilha("calc.pdf",
                      ["mes/ano", "valor pago", "reajuste devido", "valor devido",
                       "diferenca"], linhas)
    assert cls.classificar_planilha(pl)["regime"] == "CALCULO_PRONTO"


def test_competencias_de_texto():
    comps, avisos = competencias_de({"texto_solto": TEXTO})
    assert [c.rotulo for c in comps] == ["janeiro/2015", "março/2018", "abril/2018",
                                         "julho/2018", "julho/2019"]
    assert comps[1].valor_pago == d("605,45")
    assert comps[3].tipo_reajuste == ANUAL
    assert comps[2].tipo_reajuste == INDEFINIDO, "reajuste fora do aniversário"


def test_linha_de_preenchimento_e_sinalizada_e_nao_entra_no_calculo():
    comps, avisos = competencias_de({"texto_solto": TEXTO})
    assert any("R$ 0,01" in a for a in avisos)
    res = calcular(comps, mes_aniversario=7,
                   faixa_etaria_aceita={(2018, 4): d("0")})
    assert res.linhas[0].competencia.rotulo == "março/2018", "base é o 1º valor real"


def test_buraco_na_serie_vira_aviso():
    """Mês faltando desloca a cadeia inteira do devido e some sem alarde."""
    texto = ("janeiro/2020 R$ 100,00 R$ 100,00 R$ 0,00\n"
             "fevereiro/2020 R$ 100,00 R$ 100,00 R$ 0,00\n"
             "maio/2020 R$ 100,00 R$ 100,00 R$ 0,00\n")
    comps, avisos = competencias_de({"texto_solto": texto})
    assert len(comps) == 3
    assert any("faltando" in a and "março/2020" in a for a in avisos), avisos


def test_competencia_repetida_vira_aviso():
    texto = ("janeiro/2020 R$ 100,00 R$ 100,00 R$ 0,00\n"
             "janeiro/2020 R$ 200,00 R$ 200,00 R$ 0,00\n")
    comps, avisos = competencias_de({"texto_solto": texto})
    assert len(comps) == 1
    assert any("repetida" in a for a in avisos)


def test_planilha_vazia_avisa_em_vez_de_devolver_nada():
    comps, avisos = competencias_de({"texto_solto": "cabeçalho sem dados"})
    assert comps == []
    assert any("vazia" in a for a in avisos)


def test_planilha_em_grade_com_numeros():
    pl = {"linhas": [["janeiro/2020", 100.0, 100.0], ["fevereiro/2020", 110.0, 100.0]]}
    comps, _ = competencias_de(pl)
    assert len(comps) == 2 and comps[0].valor_pago == Decimal("100.0")


# ------------------------------------------ conferência do cálculo pronto ----

def test_recalculo_fiel_nao_acusa_divergencia():
    comps, _ = competencias_de({"texto_solto": TEXTO})
    res = calcular(comps, 7, {(2018, 4): d("0")})
    assert conferir_importado({"texto_solto": TEXTO}, res) == []


def test_divergencia_entre_planilha_e_recalculo_e_acusada():
    """Planilha pronta também chega errada; recontar é a única verificação
    independente que existe."""
    adulterado = TEXTO.replace("-R$ 666,00-", "-R$ 999,00-")
    comps, _ = competencias_de({"texto_solto": TEXTO})
    res = calcular(comps, 7, {(2018, 4): d("0")})
    avisos = conferir_importado({"texto_solto": adulterado}, res)
    assert avisos and "julho/2018" in avisos[0]
    assert "999,00" in avisos[0] and "666,00" in avisos[0]


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
