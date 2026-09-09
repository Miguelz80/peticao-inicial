"""Testes do Calculador. Rodar: python3 tests/test_calcular.py"""

import sys, pathlib
from decimal import Decimal
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                      / "skills" / "elaborador-inicial" / "scripts"))

from calcular_reajuste import (  # noqa: E402
    Competencia, calcular, periodo_ans, indice_do_aniversario, IndiceAusente,
    d, q, tabela, resumo, FAIXA_ETARIA, INDICES_ANS,
)


def serie(trechos):
    """[(ano_ini, mes_ini, ano_fim, mes_fim, valor)] → lista de Competencia."""
    comps = []
    for ai, mi, af, mf, valor in trechos:
        ano, mes = ai, mi
        while (ano, mes) <= (af, mf):
            comps.append(Competencia(ano, mes, d(valor)))
            mes += 1
            if mes == 13:
                mes, ano = 1, ano + 1
    return comps


# Série real de um caso do escritório (sem qualquer dado identificável).
CASO_REAL = serie([
    (2018, 3, 2018, 3, "605,45"), (2018, 4, 2018, 6, "660,54"),
    (2018, 7, 2019, 6, "762,92"), (2019, 7, 2020, 12, "883,00"),
    (2021, 1, 2021, 6, "1.074,76"), (2021, 7, 2022, 6, "1.176,39"),
    (2022, 7, 2023, 6, "1.366,95"), (2023, 7, 2024, 6, "1.498,86"),
    (2024, 7, 2025, 6, "1.947,02"), (2025, 7, 2026, 6, "2.529,18"),
    (2026, 7, 2026, 7, "3.092,93"),
])
DEVIDO_ESPERADO = {
    (2018, 7): "666,00", (2019, 7): "714,95", (2020, 7): "773,14",
    (2021, 7): "709,82", (2022, 7): "819,84", (2023, 7): "898,80",
    (2024, 7): "960,90", (2025, 7): "1.019,13", (2026, 7): "1.071,21",
}


# ------------------------------------------------------------ período ANS ----

def test_periodo_ans_maio_a_abril():
    assert periodo_ans(2024, 7) == 2024      # julho cai no período que abre em maio/24
    assert periodo_ans(2024, 5) == 2024
    assert periodo_ans(2024, 4) == 2023      # abril ainda é do período anterior
    assert periodo_ans(2024, 1) == 2023


def test_indice_do_aniversario():
    assert indice_do_aniversario(2024, 7) == Decimal("0.0691")
    assert indice_do_aniversario(2025, 3) == Decimal("0.0691")   # março/25 → período 24


def test_ano_sem_indice_levanta_e_nomeia_o_periodo():
    try:
        indice_do_aniversario(2012, 7)
        assert False, "deveria ter levantado"
    except IndiceAusente as erro:
        assert erro.periodo == 2012
        assert "não estimar" in str(erro)


# --------------------------------------------------------------- regressão ----

def test_cadeia_do_caso_real_bate_nos_nove_passos():
    res = calcular(CASO_REAL, mes_aniversario=7)
    obtidos = {l.competencia.chave: q(l.valor_devido)
               for l in res.linhas if l.competencia.chave in DEVIDO_ESPERADO}
    for chave, esperado in DEVIDO_ESPERADO.items():
        assert obtidos[chave] == d(esperado), \
            f"{chave}: obtido {obtidos[chave]}, esperado {esperado}"


def test_nao_arredonda_entre_os_anos():
    """Arredondando ano a ano a cadeia erra centavos que se acumulam."""
    base = d("605,45")
    anos = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026]
    cheio, passo = base, base
    for ano in anos:
        i = INDICES_ANS[ano]
        cheio = cheio * (1 + i)
        passo = q(passo * (1 + i))
    assert q(cheio) == d("1.071,21")
    assert q(passo) != q(cheio), "o teste perde o sentido se os dois coincidirem"


def test_reajuste_fora_do_aniversario_vira_pendencia_e_nao_entra_no_devido():
    res = calcular(CASO_REAL, mes_aniversario=7)
    rotulos = {p.competencia for p in res.pendencias}
    assert "abril/2018" in rotulos and "janeiro/2021" in rotulos
    assert res.bloqueado, "pendência de faixa etária tem que bloquear"
    # o devido segue a cadeia anual, ignorando os aumentos fora do aniversário
    assert q(dict((l.competencia.chave, l.valor_devido) for l in res.linhas)[(2021, 6)]) \
        == d("773,14")


def test_faixa_etaria_aceita_entra_no_devido():
    base = {l.competencia.chave: l.valor_devido
            for l in calcular(CASO_REAL, mes_aniversario=7).linhas}[(2020, 12)]
    aceita = {(2021, 1): d("0.10")}
    res = calcular(CASO_REAL, mes_aniversario=7, faixa_etaria_aceita=aceita)
    devidos = {l.competencia.chave: l.valor_devido for l in res.linhas}
    # comparação contra a precisão realmente carregada, não contra o valor exibido
    assert devidos[(2021, 1)] == base * Decimal("1.10")
    assert q(devidos[(2021, 1)]) == d("850,46")
    assert "janeiro/2021" not in {p.competencia for p in res.pendencias}


def test_pergunta_da_pendencia_e_em_linguagem_leiga():
    res = calcular(CASO_REAL, mes_aniversario=7)
    p = [p for p in res.pendencias if p.competencia == "janeiro/2021"][0]
    assert "faixa etária" in p.pergunta and "impugna" in p.pergunta
    assert "21,72%" in p.pergunta


# ------------------------------------------------------------------ totais ----

def test_totais_fecham_entre_si():
    """A planilha real do escritório reprova aqui — a nossa não pode."""
    res = calcular(CASO_REAL, mes_aniversario=7)
    assert res.conferir() == []
    assert q(res.total_pago - res.total_devido) == q(res.total_diferenca)


def test_restituicao_e_de_36_meses_e_declara_a_janela():
    res = calcular(CASO_REAL, mes_aniversario=7)
    valor = res.restituicao()
    ini, fim = res.janela_restituicao
    assert fim == "julho/2026" and ini == "agosto/2023"
    assert 0 < valor < res.total_diferenca


def test_ano_sem_indice_bloqueia_o_caso_inteiro():
    antigo = serie([(2012, 1, 2013, 12, "500,00")])
    res = calcular(antigo, mes_aniversario=7)
    assert res.bloqueios and "2012" in res.bloqueios[0]
    assert res.linhas == [] or res.bloqueado


def test_serie_vazia_nao_quebra():
    assert calcular([], mes_aniversario=7).bloqueios


# ------------------------------------------------------------------- saída ----

def test_tabela_tem_as_colunas_do_escritorio():
    res = calcular(CASO_REAL, mes_aniversario=7)
    t = tabela(res)
    assert t[0] == ["Mês/Ano", "Valor Pago", "Reajuste Aplicado", "Tipo de Reajuste",
                    "Reajuste Devido", "Valor Devido", "Diferença"]
    assert t[-1][0] == "Total"
    julho24 = [l for l in t if l[0] == "julho/2024"][0]
    assert julho24[3] == "Anual" and julho24[4] == "6,91%"
    assert julho24[5] == "R$ 960,90"


def test_resumo_traz_os_quatro_campos_da_planilha():
    r = resumo(calcular(CASO_REAL, mes_aniversario=7))
    for campo in ("Valor Pago (Atual)", "Valor Devido", "Diferença (Mensal)",
                  "Restituição (últimos 3 anos)"):
        assert campo in r
    assert r["Valor Pago (Atual)"] == "R$ 3.092,93"
    assert r["Valor Devido"] == "R$ 1.071,21"
    assert r["Diferença (Mensal)"] == "R$ 2.021,72"


def test_formata_moeda_no_padrao_brasileiro():
    from calcular_reajuste import _brl
    assert _brl(d("1234567.89")) == "R$ 1.234.567,89"





def test_janela_da_restituicao_e_parametrizavel():
    """A convenção muda o valor do pedido em mais de mil reais — por isso é parâmetro,
    não constante escondida. Ver pergunta A7."""
    res = calcular(CASO_REAL, mes_aniversario=7)
    padrao = res.restituicao()                                  # 36 meses até o fim
    planilha = res.restituicao(meses=37, ate=(2026, 5))          # convenção observada
    assert q(padrao) == d("38.576,42")
    assert q(planilha) == d("36.738,93"), "tem que reproduzir a planilha real"
    assert padrao - planilha > d("1.800,00")


def test_conferencia_acusa_marco_congelado():
    res = calcular(CASO_REAL, mes_aniversario=7)
    res.restituicao(meses=37, ate=(2026, 5))
    assert any("marco congelado" in e for e in res.conferir())


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
