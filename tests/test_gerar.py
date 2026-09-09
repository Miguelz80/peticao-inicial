"""Testes do Gerador. Rodar: python3 tests/test_gerar.py"""

import sys, pathlib, zipfile, tempfile, os, re
RAIZ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "skills" / "elaborador-inicial" / "scripts"))
sys.path.insert(0, str(RAIZ / "tests"))

from gerar_peticao import (  # noqa: E402
    Peca, Enderecamento, Paragrafo, Titulo, Assinatura, Espaco, Tabela, CaixaDestaque,
    montar, runs, esc, ModeloInvalido, tabela_de_reajuste, caixa_de_resumo,
    CABECALHO_TABELA, ZEBRA, LINHA_TOTAL, TEXTO_DESTAQUE, FONTE,
)
from conferir import conferir_editabilidade  # noqa: E402
from calcular_reajuste import calcular, d  # noqa: E402
from test_calcular import CASO_REAL  # noqa: E402


SECTPR = ('<w:sectPr><w:headerReference w:type="default" r:id="rId7"/>'
          '<w:footerReference w:type="default" r:id="rId8"/>'
          '<w:pgSz w:w="11906" w:h="16838"/>'
          '<w:pgMar w:top="2037" w:right="1562" w:bottom="1560" w:left="1560"/>'
          "</w:sectPr>")
RELS = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/'
        'package/2006/relationships">'
        '<Relationship Id="rId7" Type="http://x/header" Target="header1.xml"/>'
        '<Relationship Id="rId9" Type="http://x/image" Target="media/tabela.png"/>'
        "</Relationships>")
RELS_HEADER = ('<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.'
               'org/package/2006/relationships">'
               '<Relationship Id="rId1" Type="http://x/image" Target="media/timbre.png"/>'
               "</Relationships>")


def modelo(diretorio, sectpr=SECTPR):
    caminho = os.path.join(diretorio, "modelo.docx")
    with zipfile.ZipFile(caminho, "w") as z:
        z.writestr("word/document.xml",
                   '<w:document xmlns:w="http://schemas.openxmlformats.org/'
                   'wordprocessingml/2006/main" xmlns:r="http://schemas.openxmlformats.'
                   'org/officeDocument/2006/relationships"><w:body>'
                   '<w:p><w:r><w:t>modelo antigo</w:t></w:r></w:p>'
                   '<w:drawing><a:blip r:embed="rId9"/></w:drawing>'
                   f"{sectpr}</w:body></w:document>")
        z.writestr("word/_rels/document.xml.rels", RELS)
        z.writestr("word/_rels/header1.xml.rels", RELS_HEADER)
        z.writestr("word/header1.xml", "<w:hdr/>")
        z.writestr("word/styles.xml", "<w:styles/>")
        z.writestr("word/media/timbre.png", b"\x00" * 44_000)     # timbre, do cabeçalho
        z.writestr("word/media/tabela.png", b"\x00" * 150_000)    # tabela em imagem
    return caminho


def gerar(diretorio, peca, sectpr=SECTPR):
    saida = os.path.join(diretorio, "peca.docx")
    montar(modelo(diretorio, sectpr), peca, saida)
    return saida


def corpo(caminho):
    return zipfile.ZipFile(caminho).read("word/document.xml").decode("utf-8")


# ------------------------------------------------------------- formatação ----

def test_negrito_por_marcacao():
    xml = runs("valor de **R$ 100,00** apenas")
    assert xml.count("<w:b/>") == 1
    assert "R$ 100,00" in xml and "apenas" in xml


def test_caracteres_especiais_sao_escapados_uma_vez_so():
    xml = runs("Autora & Ré <fim>")
    assert "&amp;" in xml and "&lt;fim&gt;" in xml
    assert "&amp;amp;" not in xml, "escape duplo"


def test_fonte_do_escritorio_em_todo_run():
    xml = runs("texto")
    assert f'w:ascii="{FONTE}"' in xml


# ----------------------------------------------------------------- tabela ----

def test_tabela_e_nativa_e_nunca_imagem():
    t = Tabela([["A", "B"], ["1", "2"]]).xml()
    assert "<w:tbl>" in t and "<w:tr>" in t and "<w:tc>" in t
    assert "<w:drawing>" not in t and "image" not in t


def test_tabela_usa_a_paleta_medida_da_peca_real():
    t = Tabela([["A", "B"], ["1", "2"], ["3", "4"], ["T", "0"]],
               destaque_colunas=(1,)).xml()
    assert CABECALHO_TABELA in t, "cabeçalho azul-escuro"
    assert ZEBRA in t, "zebra"
    assert LINHA_TOTAL in t, "linha de total"
    assert TEXTO_DESTAQUE in t, "realce vermelho na coluna de destaque"


def test_cabecalho_da_tabela_repete_entre_paginas():
    assert "<w:tblHeader/>" in Tabela([["A"], ["1"]]).xml()


def test_tabela_de_reajuste_sai_do_calculador():
    res = calcular(CASO_REAL, mes_aniversario=7,
                   faixa_etaria_aceita={(2018, 4): d("0"), (2021, 1): d("0")})
    t = tabela_de_reajuste(res).xml()
    assert "Mês/Ano" in t and "julho/2024" in t and "R$ 960,90" in t
    assert "Total" in t


def test_caixa_de_resumo_traz_os_quatro_campos():
    res = calcular(CASO_REAL, mes_aniversario=7,
                   faixa_etaria_aceita={(2018, 4): d("0"), (2021, 1): d("0")})
    x = caixa_de_resumo(res).xml()
    for campo in ("Valor Pago (Atual)", "Valor Devido", "Diferença (Mensal)",
                  "Restituição"):
        assert campo in x


# ---------------------------------------------------------------- montagem ----

def test_preserva_o_sectpr_original_com_o_timbre():
    """Sem o sectPr original a peça sai sem logo, sem rodapé e fora do formato."""
    with tempfile.TemporaryDirectory() as t:
        doc = corpo(gerar(t, Peca().add(Paragrafo("texto"))))
        assert "headerReference" in doc and 'r:id="rId7"' in doc
        assert 'w:w="11906"' in doc and 'w:top="2037"' in doc


def test_preserva_cabecalhos_rodapes_e_estilos():
    with tempfile.TemporaryDirectory() as t:
        z = zipfile.ZipFile(gerar(t, Peca().add(Paragrafo("x"))))
        for parte in ("word/header1.xml", "word/styles.xml",
                      "word/_rels/header1.xml.rels"):
            assert parte in z.namelist()


def test_conteudo_antigo_do_modelo_nao_sobrevive():
    with tempfile.TemporaryDirectory() as t:
        doc = corpo(gerar(t, Peca().add(Paragrafo("conteúdo novo"))))
        assert "modelo antigo" not in doc and "conteúdo novo" in doc


def test_imagem_orfa_do_modelo_e_podada():
    """O modelo carrega as tabelas em imagem das peças antigas. Se viessem junto, a
    peça nova sairia com peso morto e reprovaria na Conferência."""
    with tempfile.TemporaryDirectory() as t:
        z = zipfile.ZipFile(gerar(t, Peca().add(Paragrafo("x"))))
        assert "word/media/tabela.png" not in z.namelist()
        assert "word/media/timbre.png" in z.namelist(), "timbre não pode sumir"


def test_relacao_da_imagem_orfa_tambem_sai():
    with tempfile.TemporaryDirectory() as t:
        z = zipfile.ZipFile(gerar(t, Peca().add(Paragrafo("x"))))
        rels = z.read("word/_rels/document.xml.rels").decode()
        assert "rId9" not in rels and "rId7" in rels


def test_modelo_sem_sectpr_e_recusado():
    with tempfile.TemporaryDirectory() as t:
        try:
            gerar(t, Peca().add(Paragrafo("x")), sectpr="")
            assert False, "deveria recusar"
        except ModeloInvalido as erro:
            assert "sectPr" in str(erro) and "timbre" in str(erro)


def test_gerador_nunca_emite_elemento_que_trava_a_edicao():
    with tempfile.TemporaryDirectory() as t:
        doc = corpo(gerar(t, Peca().add(
            Enderecamento("AO JUÍZO"), Titulo("I.", "Dos fatos"),
            Paragrafo("texto"), Tabela([["A"], ["1"]]),
            Assinatura("NOME", "OAB/BA 1"))))
        for proibido in ("<w:documentProtection", "<w:sdt", "<w:drawing"):
            assert proibido not in doc


# -------------------------------------------------------------- integração ----

def test_peca_gerada_passa_na_conferencia_de_editabilidade():
    res = calcular(CASO_REAL, mes_aniversario=7,
                   faixa_etaria_aceita={(2018, 4): d("0"), (2021, 1): d("0")})
    with tempfile.TemporaryDirectory() as t:
        caminho = gerar(t, Peca().add(
            Enderecamento("AO JUÍZO DA VARA CÍVEL DA COMARCA DE SALVADOR/BA"),
            Titulo("I.", "Dos fatos"),
            Paragrafo("Reajustes acima dos índices da ANS."),
            caixa_de_resumo(res), tabela_de_reajuste(res),
            Espaco(), Assinatura("NOME", "OAB/BA 1")))
        achados = conferir_editabilidade(caminho)
        assert achados == [], [str(a) for a in achados]


def test_xml_gerado_e_bem_formado():
    import xml.etree.ElementTree as ET
    res = calcular(CASO_REAL, mes_aniversario=7,
                   faixa_etaria_aceita={(2018, 4): d("0"), (2021, 1): d("0")})
    with tempfile.TemporaryDirectory() as t:
        doc = corpo(gerar(t, Peca().add(
            Paragrafo("Autora & Ré"), tabela_de_reajuste(res),
            CaixaDestaque("Resumo", ["**a:** b"]))))
        ET.fromstring(doc)     # levanta se estiver malformado


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
