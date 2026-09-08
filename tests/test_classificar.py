"""Testes do Classificador. Rodar: python3 -m pytest tests/ -q  (ou python3 tests/test_classificar.py)"""

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]
                      / "skills" / "elaborador-inicial" / "scripts"))

from classificar import (  # noqa: E402
    Planilha, Fato, normalizar, classificar_planilha, decidir_eixo_a,
    decidir_eixo_b, classificar, espelho, SIM, NAO, DESCONHECIDO,
)


# --------------------------------------------------------------- Eixo A ----

def test_tipo1_calculo_pronto():
    p = Planilha("calc.xlsx",
                 ["Mês/Ano", "Valor Pago", "Reajuste Aplicado", "Tipo de Reajuste",
                  "Reajuste Devido", "Valor Devido", "Diferença"],
                 [["01/2023", 1000, "10%", "anual", "5%", 950, 50]] * 10)
    assert classificar_planilha(p)["regime"] == "CALCULO_PRONTO"


def test_tipo2_faturamento_bruto():
    p = Planilha("fat.xlsx", ["Competência", "Beneficiário", "Valor", "Valor Total"],
                 [["01/2023", "X", 1000, 1000]] * 10)
    assert classificar_planilha(p)["regime"] == "FATURAMENTO_BRUTO"


def test_armadilha_reajuste_aplicado_nao_e_devido():
    """A armadilha do §3.1: 'Reajuste Aplicado' é o que a operadora cobrou.
    Um match por substring em 'reajuste' pularia o cálculo inteiro."""
    p = Planilha("fat.xlsx", ["Mês/Ano", "Valor Pago", "Reajuste Aplicado"],
                 [["01/2023", 1000, "10%"]] * 10)
    v = classificar_planilha(p)
    assert v["regime"] == "FATURAMENTO_BRUTO", "não pode virar CALCULO_PRONTO"
    assert any("não é valor devido" in e for e in v["evidencias"])


def test_calculo_pela_metade_vira_ambiguo():
    linhas = [["01/2023", 1000, 5, 950, 50] for _ in range(3)]
    linhas += [["02/2023", 1000, None, None, None] for _ in range(7)]
    p = Planilha("meio.xlsx",
                 ["Mês/Ano", "Valor Pago", "Reajuste Devido", "Valor Devido", "Diferença"],
                 linhas)
    assert classificar_planilha(p)["regime"] == "AMBIGUO"


def test_demonstrativo_pdf_da_operadora_nao_vira_ausente():
    """Regressão do caso real: o insumo veio como demonstrativo BEN120, não planilha.
    Pela regra antiga cairia em AUSENTE e bloquearia um caso trabalhável."""
    p = Planilha("demonstrativo.pdf", [],
                 texto_solto="BEN120 - Demonstrativo de Pagamento de Faturas "
                             "Competência Vencimento Data Baixa Valor Tipo Lançamento")
    assert classificar_planilha(p)["regime"] == "DEMONSTRATIVO_OPERADORA"


def test_cabecalho_desconhecido_vira_pergunta_nao_erro():
    p = Planilha("estranha.xlsx", ["Coluna A", "Coluna B", "Coluna C"], [[1, 2, 3]] * 5)
    v = classificar_planilha(p)
    assert v["regime"] == "AMBIGUO"
    assert any("não reconhecidos" in e for e in v["evidencias"])


def test_planilhas_divergentes_nao_sao_resolvidas_por_heuristica():
    pronta = Planilha("a.xlsx", ["Mês/Ano", "Valor Pago", "Reajuste Devido",
                                 "Valor Devido", "Diferença"],
                      [["01/2023", 1000, 5, 950, 50]] * 10)
    bruta = Planilha("b.xlsx", ["Competência", "Valor", "Valor Total"],
                     [["01/2023", 1000, 1000]] * 10)
    v = decidir_eixo_a([pronta, bruta])
    assert v["regime"] == "AMBIGUO"
    assert "divergentes" in v["evidencias"][0]


def test_sem_planilha_nenhuma():
    assert decidir_eixo_a([])["regime"] == "AUSENTE"


# --------------------------------------------------------------- Eixo B ----

def _fatos(**kw):
    return {k: (v if isinstance(v, Fato) else Fato(valor=v, fonte="teste", confianca=0.9))
            for k, v in kw.items()}


def test_autogestao_sobrepoe_tudo():
    """Autogestão é override total: nem PJ, nem família, nem nada muda a tese."""
    v = decidir_eixo_b(_fatos(F1="AUTOGESTAO", F2="PJ", F3=NAO, F4=SIM, F5=NAO))
    assert v["tese"] == "CASSI_AUTOGESTAO"
    assert any(d["tese"] == "EMPRESARIAL_FAMILIAR" for d in v["descartadas"])


def test_empresarial_familiar():
    v = decidir_eixo_b(_fatos(F1="COMERCIAL", F2="PJ", F3=NAO, F4=SIM, F5=NAO))
    assert v["tese"] == "EMPRESARIAL_FAMILIAR"


def test_pj_com_atividade_real_sai_do_padrao():
    v = decidir_eixo_b(_fatos(F1="COMERCIAL", F2="PJ", F3=SIM))
    assert v["tese"] == "FORA_DO_PADRAO" and v["bloqueio"] == "G6"


def test_silencio_sobre_vinculo_nao_vira_nao():
    """Ausência de sinal é DESCONHECIDO, jamais NAO. Silêncio da transcrição sobre
    vínculo empregatício não prova que não existe vínculo."""
    v = decidir_eixo_b(_fatos(F1="COMERCIAL", F2="PJ", F3=NAO, F4=SIM))  # F5 ausente
    assert v["tese"] == "INDEFINIDA"
    assert "F5" in v["faltando"]


def test_operadora_desconhecida_bloqueia():
    v = decidir_eixo_b(_fatos(F2="PF_DIRETO"))
    assert v["tese"] == "INDEFINIDA" and v["bloqueio"] == "G4"


def test_adesao_e_individual():
    assert decidir_eixo_b(_fatos(F1="COMERCIAL", F2="PF_VIA_ASSOCIACAO"))["tese"] \
        == "COLETIVO_POR_ADESAO"
    assert decidir_eixo_b(_fatos(F1="COMERCIAL", F2="PF_DIRETO"))["tese"] \
        == "INDIVIDUAL_COMUM"


# ---------------------------------------------------------- Gates/dossiê ----

def _planilha_ok():
    return [Planilha("c.xlsx", ["Mês/Ano", "Valor Pago", "Reajuste Devido",
                                "Valor Devido", "Diferença"],
                     [["01/2023", 1000, 5, 950, 50]] * 10)]


def test_nunca_gera_sem_confirmacao_mesmo_com_tudo_certo():
    """G8: confiança alta não dispensa o Espelho."""
    d = classificar([], _planilha_ok(),
                    _fatos(F1="COMERCIAL", F2="PJ", F3=NAO, F4=SIM, F5=NAO))
    assert d["status"] == "PRECISA_CONFIRMACAO"
    assert d["status"] != "PRONTO_PARA_GERAR"


def test_bloqueio_impede_geracao():
    d = classificar([], _planilha_ok(), _fatos(F2="PJ"))
    assert d["status"] == "BLOQUEADO"
    assert any(p["bloqueante"] for p in d["perguntas"])


def test_toda_pergunta_oferece_nao_sei():
    d = classificar([], [], _fatos(F2="PJ"))
    for p in d["perguntas"]:
        assert any("Não sei" in o for o in p["opcoes"]), p["id"]


def test_documento_indefinido_nao_e_descartado_em_silencio():
    docs = [{"arquivo": "misterio.pdf", "papel": "INDEFINIDO"}]
    d = classificar(docs, _planilha_ok(),
                    _fatos(F1="COMERCIAL", F2="PF_DIRETO"))
    assert any(p["id"].startswith("DOC-") for p in d["perguntas"])


def test_fato_lido_de_digitalizacao_sempre_confirma():
    fatos = _fatos(F1="AUTOGESTAO")
    fatos["F9"] = Fato(valor="81", fonte="doc pessoal", citacao="81 anos",
                       confianca=0.6, origem="ocr")
    d = classificar([], _planilha_ok(), fatos)
    assert any(p["id"] == "OCR-F9" for p in d["perguntas"])


def test_sinais_conflitantes_mostram_os_dois_lados():
    fatos = _fatos(F1="COMERCIAL", F2="PJ", F4=SIM, F5=NAO)
    fatos["F3"] = Fato(valor=NAO, fonte="transcrição", citacao="empresa inativa há 3 anos",
                       confianca=0.9, conflitos=["contrato social mostra faturamento"])
    d = classificar([], _planilha_ok(), fatos)
    conflito = [p for p in d["perguntas"] if p["id"] == "G2-F3"]
    assert conflito and len(conflito[0]["evidencias"]) == 2


def test_outro_tipo_de_peca_e_recusado_por_escopo():
    d = classificar([], _planilha_ok(), _fatos(F1="COMERCIAL", F2="PF_DIRETO"),
                    tipo_peca="RECURSO_INOMINADO")
    assert d["status"] == "BLOQUEADO"
    assert d["perguntas"][0]["id"] == "G7"


def test_subdecisoes_da_autogestao():
    fatos = _fatos(F1="AUTOGESTAO", F6="ATIVO")
    fatos["F9"] = Fato(valor="81", fonte="qualificação", confianca=0.95)
    d = classificar([], _planilha_ok(), fatos)
    s = d["subdecisoes"]
    assert "simples" in s["restituicao"]              # sem CDC, sem dobra
    assert "tutela de urgência" in s["caminho_processual"]
    assert s["prioridade_idoso"].startswith("sim")


def test_espelho_nao_quebra_e_mostra_o_essencial():
    d = classificar([{"arquivo": "x.pdf", "papel": "TRANSCRICAO", "origem": "texto_nativo"}],
                    _planilha_ok(),
                    _fatos(F1="COMERCIAL", F2="PJ", F3=NAO, F4=SIM, F5=NAO))
    texto = espelho(d, "Fulano")
    assert "ESPELHO DE CLASSIFICAÇÃO" in texto
    assert "FALSO COLETIVO EMPRESARIAL" in texto
    assert "Confirma a tese" in texto


def test_normalizar():
    assert normalizar("  Mês/Ano  ") == "mes/ano"
    assert normalizar("DIFERENÇA") == "diferenca"


if __name__ == "__main__":
    import traceback
    testes = [(n, o) for n, o in sorted(globals().items())
              if n.startswith("test_") and callable(o)]
    falhas = 0
    for nome, fn in testes:
        try:
            fn()
            print(f"  ok    {nome}")
        except Exception:
            falhas += 1
            print(f"  FALHA {nome}")
            traceback.print_exc()
    print(f"\n{len(testes) - falhas}/{len(testes)} passaram")
    raise SystemExit(1 if falhas else 0)
