"""Testes da Conferência. Cada caso reproduz um erro encontrado em peça real.
Rodar: python3 tests/test_conferir.py"""

import sys, pathlib, zipfile, tempfile, os
from decimal import Decimal
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "skills" / "elaborador-inicial" / "scripts"))
sys.path.insert(0, str(RAIZ / "tests"))

from calcular_reajuste import calcular, Linha, Resultado, Competencia, d, q  # noqa: E402
from conferir import (  # noqa: E402
    conferir, conferir_calculo, conferir_peca, conferir_editabilidade,
    BLOQUEIA, ALERTA,
)
from test_calcular import CASO_REAL  # noqa: E402


def caso_limpo() -> Resultado:
    """Série real com as duas pendências de faixa etária já decididas."""
    return calcular(CASO_REAL, mes_aniversario=7,
                    faixa_etaria_aceita={(2018, 4): d("0"), (2021, 1): d("0")})


def codigos(achados):
    return {a.codigo for a in achados}


# ------------------------------------------------- consistência do cálculo ----

def test_totais_que_nao_fecham_bloqueiam():
    """Reproduz a planilha real: 133.776,67 − 80.153,61 = 53.623,06, mas o total da
    coluna Diferença dizia 36.738,93."""
    res = Resultado()
    c = Competencia(2024, 1, d("133776.67"))
    res.linhas.append(Linha(competencia=c, reajuste_aplicado=Decimal(0),
                            reajuste_devido=Decimal(0), valor_devido=d("80153.61"),
                            diferenca=d("36738.93")))       # não é pago − devido
    achados = conferir_calculo(res)
    assert "C3" in codigos(achados)
    assert all(a.gravidade == BLOQUEIA for a in achados if a.codigo == "C3")


def test_marco_da_restituicao_congelado_bloqueia():
    """A peça real foi protocolada com a janela terminando dois meses antes do fim
    da série."""
    res = caso_limpo()
    res.restituicao(meses=37, ate=(2026, 5))
    assert "C4" in codigos(conferir_calculo(res))


def test_pendencia_de_faixa_etaria_nao_resolvida_bloqueia():
    res = calcular(CASO_REAL, mes_aniversario=7)      # sem decidir nada
    achados = [a for a in conferir_calculo(res) if a.codigo == "C11"]
    assert len(achados) == 2
    assert {a.onde for a in achados} == {"abril/2018", "janeiro/2021"}


def test_calculo_consistente_nao_gera_achado():
    res = caso_limpo()
    res.restituicao()
    assert conferir_calculo(res) == []


# ------------------------------------------------------- peça x cálculo ----

def test_valor_declarado_divergente_bloqueia():
    res = caso_limpo()
    achados = conferir_peca("", res, declarados={"restituicao": "R$ 36.738,93"})
    assert "C6" in codigos(achados)
    a = [x for x in achados if x.codigo == "C6"][0]
    assert "38.576,42" in a.esperado and "36.738,93" in a.encontrado


def test_valor_declarado_correto_passa():
    res = caso_limpo()
    achados = conferir_peca("", res, declarados={
        "restituicao": "R$ 38.576,42",
        "diferenca_mensal": "R$ 2.021,72",
        "valor_pago_atual": "R$ 3.092,93",
        "valor_devido_atual": "R$ 1.071,21",
    })
    assert "C6" not in codigos(achados)


def test_percentuais_divergentes_para_o_mesmo_reajuste():
    """Peça CASSI: a tabela de histórico dizia 12,79% e a da tutela 12,88%."""
    texto = ("os reajustes de 12,79% (2023) e 14,33% (2024) ... conforme demonstrado, "
             "+12,88% (2023) e +14,26% (2024) em desproporção com os índices da ANS")
    achados = conferir_peca(texto, caso_limpo())
    conflitos = [a for a in achados if a.codigo == "C2"]
    assert conflitos, "deveria acusar 12,79 x 12,88 e 14,26 x 14,33"
    todos = " ".join(a.encontrado for a in conflitos)
    assert "12,79%" in todos and "12,88%" in todos


def test_percentuais_realmente_distintos_nao_geram_falso_positivo():
    texto = "reajustes de 9,63% em 2023, 6,91% em 2024 e 23,88% em 2025"
    assert "C2" not in codigos(conferir_peca(texto, caso_limpo()))


def test_patamar_da_tutela_ausente_do_calculo_bloqueia():
    """Peça CASSI: pedia limitar a R$ 2.526,89, valor que não constava da própria
    tabela de histórico."""
    texto = ("requer a concessão da tutela para determinar que a Ré limite "
             "provisoriamente a mensalidade a patamar razoável, em torno de "
             "R$ 2.526,89, até que sejam exibidos os documentos.")
    achados = conferir_peca(texto, caso_limpo())
    assert "C1" in codigos(achados)


def test_patamar_que_existe_no_calculo_passa():
    texto = "requer limitar a mensalidade ao patamar de R$ 1.071,21, valor devido."
    assert "C1" not in codigos(conferir_peca(texto, caso_limpo()))


def test_valor_da_causa_que_nao_segue_a_formula_declarada():
    """Peça CASSI: valor da causa era o dobro da restituição, mas o texto o
    justificava como restituição mais doze meses de diferença."""
    res = caso_limpo()
    rest = q(res.restituicao())
    achados = conferir_peca("", res, formula_valor_da_causa="restituicao+12x_diferenca",
                            valor_da_causa=str(rest * 2))
    a = [x for x in achados if x.codigo == "C5"]
    assert a and a[0].gravidade == BLOQUEIA
    assert "2x_restituicao" in a[0].o_que


def test_valor_da_causa_coerente_passa():
    res = caso_limpo()
    esperado = q(res.restituicao() + res.diferenca_mensal * 12)
    achados = conferir_peca("", res, formula_valor_da_causa="restituicao+12x_diferenca",
                            valor_da_causa=str(esperado))
    assert "C5" not in codigos(achados)


def test_formula_desconhecida_alerta_mas_nao_bloqueia():
    achados = conferir_peca("", caso_limpo(), formula_valor_da_causa="chute",
                            valor_da_causa="1000,00")
    a = [x for x in achados if x.codigo == "C5"][0]
    assert a.gravidade == ALERTA


# ------------------------------------------------------- editabilidade ----

REL = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/'
       'package/2006/relationships">{}</Relationships>')


def docx_falso(diretorio, document_xml, settings_xml="<w:settings/>", media=None,
               rels_corpo="", rels_cabecalho=""):
    """`rels_corpo` liga imagens ao document.xml; `rels_cabecalho`, ao header —
    é essa diferença que separa tabela em imagem de timbre."""
    caminho = os.path.join(diretorio, "peca.docx")
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("word/document.xml", document_xml)
        z.writestr("word/settings.xml", settings_xml)
        z.writestr("word/_rels/document.xml.rels", REL.format(rels_corpo))
        z.writestr("word/_rels/header1.xml.rels", REL.format(rels_cabecalho))
        for nome, tamanho in (media or {}).items():
            z.writestr(f"word/media/{nome}", b"\x00" * tamanho)
    return caminho


def imagem(rid, alvo):
    return (f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/'
            f'officeDocument/2006/relationships/image" Target="media/{alvo}"/>')


def test_documento_protegido_bloqueia():
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, "<w:document><w:tbl/></w:document>",
                       '<w:settings><w:documentProtection w:edit="readOnly"/></w:settings>')
        assert "C9" in codigos(conferir_editabilidade(c))


def test_documentprotection_vazio_nao_bloqueia():
    """A peça CASSI real tinha <w:documentProtection /> sem atributos — elemento
    inofensivo, não trava nada."""
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, "<w:document><w:tbl/></w:document>",
                       "<w:settings><w:documentProtection /></w:settings>")
        assert "C9" not in codigos(conferir_editabilidade(c))


def test_content_control_travado_bloqueia():
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, '<w:document><w:sdt><w:sdtPr>'
                          '<w:lock w:val="sdtContentLocked"/></w:sdtPr></w:sdt></w:document>')
        assert "C10" in codigos(conferir_editabilidade(c))


def test_content_control_destravado_nao_bloqueia():
    """As duas peças reais do escritório têm w:sdt sem w:lock — são editáveis.
    Bloquear por w:sdt reprovaria todo documento do escritório."""
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, '<w:document><w:tbl/><w:sdt><w:sdtPr><w:tag w:val="x"/>'
                          '</w:sdtPr><w:t>editável</w:t></w:sdt></w:document>')
        assert "C10" not in codigos(conferir_editabilidade(c))


def test_tabela_em_imagem_bloqueia():
    """As duas tabelas centrais da peça CASSI eram PNG de 155 KB e 137 KB,
    referenciadas pelo corpo do documento."""
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, '<w:document><w:drawing><w:blip r:embed="rId9"/>'
                          "</w:drawing></w:document>",
                       media={"image4.png": 155_000},
                       rels_corpo=imagem("rId9", "image4.png"))
        achados = [a for a in conferir_editabilidade(c) if a.codigo == "C8"]
        assert achados and achados[0].gravidade == BLOQUEIA


def test_timbre_pesado_no_cabecalho_nao_e_confundido_com_tabela():
    """O timbre é referenciado pelo cabeçalho, não pelo corpo — não pode bloquear
    nem quando é pesado."""
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, "<w:document><w:tbl/></w:document>",
                       media={"timbre.png": 200_000},
                       rels_cabecalho=imagem("rId1", "timbre.png"))
        assert "C8" not in codigos(conferir_editabilidade(c))


def test_imagem_pequena_no_corpo_nao_bloqueia():
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, '<w:document><w:tbl/><w:drawing><w:blip r:embed="rId9"/>'
                          "</w:drawing></w:document>",
                       media={"icone.png": 3_000},
                       rels_corpo=imagem("rId9", "icone.png"))
        assert "C8" not in codigos(conferir_editabilidade(c))


def test_fonte_fora_do_padrao_alerta():
    """A peça CASSI tinha 113 runs em Quattrocento Sans."""
    with tempfile.TemporaryDirectory() as t:
        c = docx_falso(t, '<w:document><w:tbl/><w:rFonts w:ascii="Segoe UI"/>'
                          '<w:rFonts w:ascii="Quattrocento Sans"/></w:document>')
        a = [x for x in conferir_editabilidade(c) if x.codigo == "C14"]
        assert a and a[0].gravidade == ALERTA and "Quattrocento" in a[0].encontrado


# ------------------------------------------------------------ integração ----

def test_relatorio_bloqueia_e_diz_por_que():
    res = calcular(CASO_REAL, mes_aniversario=7)
    c = conferir(res, texto_peca="limitar a mensalidade a R$ 9.999,99.")
    assert not c.liberado
    texto = c.relatorio()
    assert "DOCUMENTO NÃO LIBERADO" in texto and "C11" in texto


def test_caso_integralmente_consistente_libera():
    res = caso_limpo()
    c = conferir(res, texto_peca="A diferença mensal é de R$ 2.021,72.",
                 declarados={"diferenca_mensal": "R$ 2.021,72"})
    assert c.liberado
    assert "LIBERADO" in c.relatorio()


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
