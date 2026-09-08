"""Testes da extração de evidências. Rodar: python3 tests/test_extrair.py"""

import sys, pathlib, tempfile, os
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                      / "skills" / "elaborador-inicial" / "scripts"))

from extrair_evidencias import (  # noqa: E402
    identificar_papel, _linha_de_cabecalho, extrair,
)


def test_peca_processual_nao_vira_contrato():
    """Regressão: a peça compartilha vocabulário com o contrato do plano
    ('cláusula', 'cobertura'). Ler uma inicial como contrato do cliente é erro grave."""
    texto = ("AO JUÍZO DA VARA CÍVEL DA COMARCA DE SALVADOR/BA ... cláusula contratual "
             "... cobertura assistencial ... Pede deferimento. OAB/BA 41.438")
    assert identificar_papel(texto)[0] == "PECA_PROCESSUAL"


def test_demonstrativo_da_operadora():
    texto = ("BEN120 - Demonstrativo de Pagamento de Faturas  Competência  Vencimento  "
             "Data Baixa  Valor  Tipo Lançamento  Mensalidade")
    assert identificar_papel(texto)[0] == "DEMONSTRATIVO_OPERADORA"


def test_transcricao_por_turnos_de_fala():
    texto = "\n".join(f"Entrevistador: pergunta {i}\nCliente: resposta {i}" for i in range(5))
    assert identificar_papel(texto)[0] == "TRANSCRICAO"


def test_texto_sem_marcador_fica_indefinido_e_nao_chuta():
    assert identificar_papel("bom dia, tudo bem com você")[0] == "INDEFINIDO"


def test_cabecalho_abaixo_de_linhas_de_titulo():
    linhas = [["DEMONSTRATIVO DE CÁLCULO", None, None],
              [None, None, None],
              ["Mês/Ano", "Valor Pago", "Diferença"],
              ["01/2023", 1000, 50]]
    assert _linha_de_cabecalho(linhas) == 2


def test_csv_e_lido_com_separador_ponto_e_virgula():
    with tempfile.TemporaryDirectory() as d:
        caminho = os.path.join(d, "calc.csv")
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write("Mês/Ano;Valor Pago;Reajuste Devido;Valor Devido;Diferença\n")
            fh.write("01/2023;1000;5;950;50\n")
        ex = extrair([caminho])
        assert len(ex.planilhas) == 1
        assert ex.planilhas[0]["cabecalhos"][0] == "Mês/Ano"


def test_formato_nao_suportado_nao_derruba_o_lote():
    with tempfile.TemporaryDirectory() as d:
        bom = os.path.join(d, "a.txt")
        ruim = os.path.join(d, "b.zip")
        open(bom, "w").write("AO JUÍZO ... Pede deferimento.")
        open(ruim, "wb").write(b"PK\x03\x04")
        ex = extrair([ruim, bom])
        assert len(ex.trechos) == 1 and len(ex.ilegiveis) == 1


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
