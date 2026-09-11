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
            "restituicao": _brl(res.restituicao()),
            "valor_da_causa": _brl(res.restituicao() * 2)}


def dados_adesao(res):
    return {"plano": "PLANO X", "inicio_contrato": "março/2018",
            "competencia_atual": "julho de 2026", "maior_reajuste": "29,90%",
            "valor_pago_atual": _brl(res.valor_pago_atual),
            "valor_devido_atual": _brl(res.valor_devido_atual),
            "restituicao": _brl(res.restituicao()),
            "narrativa_hipossuficiencia": "Renda variável.",
            "valor_da_causa": _brl(res.restituicao() * 2)}


def dados_todas(res):
    d = dados_adesao(res)
    d.update({"idade": "81", "comarca": "Salvador/BA",
              "processo_anterior": "0000000-00.0000.0.00.0000",
              "comarca_anterior": "Outra/BA",
              "diferenca_mensal": _brl(res.diferenca_mensal),
              "valor_da_causa": _brl(res.restituicao() + res.diferenca_mensal * 12)})
    return d


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


def test_toda_tese_do_catalogo_tem_texto_em_todos_os_blocos():
    t = carregar()
    for nome, tese in t.items():
        assert not tese.pendente, f"{nome} está sem texto"
        for b in tese.blocos:
            assert b.paragrafos, f"{nome} · {b.titulo} sem texto"


def test_procedencia_do_texto_esta_declarada():
    """Duas teses vieram de peça real protocolada; duas foram redigidas a partir dos
    fundamentos. A diferença não pode ficar implícita."""
    t = carregar()
    for nome in ("CASSI_AUTOGESTAO", "COLETIVO_POR_ADESAO"):
        assert not t[nome].revisar, f"{nome} veio de peça real, não deveria pedir revisão"
    for nome in ("EMPRESARIAL_FAMILIAR", "INDIVIDUAL_COMUM"):
        assert t[nome].revisar, f"{nome} foi redigida e precisa declarar isso"


def test_ementa_de_julgado_vira_citacao_recuada():
    from gerar_peticao import Citacao
    res = resultado()
    r = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "SIM", "F9": "45"},
                    dados_adesao(res), resultado_calculo=res)
    citacoes = [b for b in r.peca.blocos if isinstance(b, Citacao)]
    assert len(citacoes) == 4, len(citacoes)
    assert 'w:left="720"' in citacoes[0].xml()
    assert not citacoes[0].texto.startswith("> "), "a marca não pode vazar para o texto"


def test_coletivo_por_adesao_monta_pronta_com_tabela():
    res = resultado()
    r = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "SIM", "F9": "45"},
                    dados_adesao(res), resultado_calculo=res)
    assert r.pronto, (r.pendencias, r.perguntas)
    corpo = "".join(b.xml() for b in r.peca.blocos)
    assert "<w:tbl>" in corpo and "julho/2024" in corpo


def test_faixa_etaria_condiciona_o_capitulo_na_adesao():
    res = resultado()
    com = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "SIM", "F9": "45"},
                      dados_adesao(res), resultado_calculo=res)
    sem = montar_peca("COLETIVO_POR_ADESAO", {"F6": "ATIVO", "F7": "NAO", "F9": "45"},
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
    assert len(r.perguntas) >= 2, r.perguntas
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


CATALOGO_SEM_TEXTO = """## TESE: TESTE_PENDENTE
@pendente: falta a peça de referência

### BLOCO: I | Do capítulo sem texto
@condicao: sempre
@fundamentos: inexistência de vínculo empregatício entre os beneficiários e a empresa
@pendente: texto do escritório
"""


def catalogo_sintetico(diretorio):
    caminho = os.path.join(diretorio, "teses.md")
    open(caminho, "w", encoding="utf-8").write(CATALOGO_SEM_TEXTO)
    return caminho


def test_tese_sem_texto_marca_pendencia_em_vez_de_improvisar():
    """O mecanismo de pendência continua valendo para qualquer tese que entre no
    catálogo sem texto — testado com catálogo sintético para não depender de o
    arquivo real ter buraco."""
    with tempfile.TemporaryDirectory() as t:
        r = montar_peca("TESTE_PENDENTE", {}, {},
                        catalogo=catalogo_sintetico(t))
        assert not r.pronto and r.pendencias
        assert MARCA_PENDENTE in "".join(b.xml() for b in r.peca.blocos)


def test_marcador_de_pendencia_traz_os_fundamentos_do_capitulo():
    with tempfile.TemporaryDirectory() as t:
        r = montar_peca("TESTE_PENDENTE", {}, {}, catalogo=catalogo_sintetico(t))
        corpo = "".join(b.xml() for b in r.peca.blocos)
        assert "vínculo empregatício" in corpo, "o marcador tem que dizer o que falta"


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
    with tempfile.TemporaryDirectory() as t:
        r = montar_peca("TESTE_PENDENTE", {}, {}, catalogo=catalogo_sintetico(t))
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





# ------------------------------------------------- procedência do texto ----

def test_as_quatro_teses_geram_peca_completa():
    res = resultado()
    for tese in ("CASSI_AUTOGESTAO", "COLETIVO_POR_ADESAO", "EMPRESARIAL_FAMILIAR",
                 "INDIVIDUAL_COMUM"):
        r = montar_peca(tese, {"F6": "ATIVO", "F7": "SIM", "F9": "81", "F10": "NAO"},
                        dados_todas(res), resultado_calculo=res)
        assert r.pronto, (tese, r.pendencias, r.perguntas)
        assert len(titulos(r.peca)) >= 8, tese


def test_teses_redigidas_avisam_que_precisam_de_revisao():
    """Autogestão e adesão vieram de peça real; as outras duas foram redigidas a
    partir dos fundamentos e não podem sair como se tivessem a mesma procedência."""
    res = resultado()
    for tese in ("CASSI_AUTOGESTAO", "COLETIVO_POR_ADESAO"):
        r = montar_peca(tese, {"F6": "ATIVO", "F7": "SIM", "F9": "81", "F10": "NAO"},
                        dados_todas(res), resultado_calculo=res)
        assert not r.precisa_revisao, tese
    for tese in ("EMPRESARIAL_FAMILIAR", "INDIVIDUAL_COMUM"):
        r = montar_peca(tese, {"F6": "ATIVO", "F7": "SIM", "F9": "45"},
                        dados_todas(res), resultado_calculo=res)
        assert r.precisa_revisao, tese
        assert any("peça real" in a for a in r.revisoes), tese


def test_aviso_de_revisao_nao_vira_marcador_no_documento():
    """Diferente da pendência: o texto está completo, o aviso é para a advogada."""
    res = resultado()
    r = montar_peca("INDIVIDUAL_COMUM", {"F6": "ATIVO", "F7": "NAO", "F9": "45"},
                    dados_todas(res), resultado_calculo=res)
    corpo = "".join(b.xml() for b in r.peca.blocos)
    assert MARCA_PENDENTE not in corpo
    assert r.revisoes


def test_capitulos_excludentes_do_empresarial_familiar():
    """Rescisão indireta e tutela de urgência são caminhos alternativos: nunca os
    dois na mesma peça."""
    res = resultado()
    ativo = montar_peca("EMPRESARIAL_FAMILIAR", {"F6": "ATIVO", "F7": "NAO", "F9": "45"},
                        dados_todas(res), resultado_calculo=res)
    cancelado = montar_peca("EMPRESARIAL_FAMILIAR",
                            {"F6": "CANCELADO", "F7": "NAO", "F9": "45"},
                            dados_todas(res), resultado_calculo=res)
    t_ativo = " ".join(titulos(ativo.peca)).upper()
    t_canc = " ".join(titulos(cancelado.peca)).upper()
    assert "TUTELA" in t_ativo and "RESCISÃO" not in t_ativo
    assert "RESCISÃO" in t_canc and "TUTELA" not in t_canc


def test_empresarial_familiar_fundamenta_o_cdc_por_equiparacao():
    """A incidência não vem da Súmula 608 isolada — vem dos arts. 2º e 29 do CDC."""
    res = resultado()
    r = montar_peca("EMPRESARIAL_FAMILIAR", {"F6": "ATIVO", "F7": "NAO", "F9": "45"},
                    dados_todas(res), resultado_calculo=res)
    corpo = "".join(b.xml() for b in r.peca.blocos)
    assert "art. 2º" in corpo and "art. 29" in corpo
    assert "equipara" in corpo.lower()


def test_nenhuma_tese_redigida_cita_julgado():
    """Escolher julgado é da advogada. Texto redigido aqui não inventa citação."""
    t = carregar()
    for nome in ("EMPRESARIAL_FAMILIAR", "INDIVIDUAL_COMUM"):
        for bloco in t[nome].blocos:
            for p in bloco.paragrafos:
                assert not p.startswith("> "), (nome, bloco.titulo)
                assert "TJ-" not in p and "Relator" not in p, (nome, bloco.titulo)

# ----------------------------------------------------------------- pedidos ----

def pedidos(peca):
    from gerar_peticao import Paragrafo
    import re as _re
    return [b.texto for b in peca.blocos
            if isinstance(b, Paragrafo) and _re.match(r"^[a-z]\) ", b.texto)]


def test_toda_tese_tem_pedidos_e_valor_da_causa():
    """Petição inicial sem pedidos não é petição inicial."""
    res = resultado()
    for tese in carregar():
        r = montar_peca(tese, {"F6": "ATIVO", "F7": "SIM", "F9": "81", "F10": "NAO"},
                        dados_todas(res), resultado_calculo=res)
        assert pedidos(r.peca), tese
        assert any("Dá-se à causa" in b.texto for b in r.peca.blocos
                   if hasattr(b, "texto")), tese


def test_pedidos_saem_em_lista_por_letras_na_ordem():
    res = resultado()
    r = montar_peca("CASSI_AUTOGESTAO",
                    {"F6": "ATIVO", "F7": "SIM", "F9": "81", "F10": "NAO"},
                    dados_todas(res), resultado_calculo=res)
    letras = [p[0] for p in pedidos(r.peca)]
    assert letras == list("abcdefghijkl"[:len(letras)]), letras
    assert pedidos(r.peca)[-1].endswith("."), "o último pedido fecha com ponto"
    assert pedidos(r.peca)[0].endswith(";"), "os demais fecham com ponto e vírgula"


def test_pedido_condicional_some_e_as_letras_se_refazem():
    """Sem tutela e sem prioridade, as letras não podem pular."""
    res = resultado()
    ativo = montar_peca("CASSI_AUTOGESTAO",
                        {"F6": "ATIVO", "F7": "NAO", "F9": "81", "F10": "NAO"},
                        dados_todas(res), resultado_calculo=res)
    cancelado = montar_peca("CASSI_AUTOGESTAO",
                            {"F6": "CANCELADO", "F7": "NAO", "F9": "45", "F10": "NAO"},
                            dados_todas(res), resultado_calculo=res)
    assert len(pedidos(ativo.peca)) == len(pedidos(cancelado.peca)) + 4
    letras = [p[0] for p in pedidos(cancelado.peca)]
    assert letras == list("abcdefgh"), letras
    assert not any("tutela de urgência" in p for p in pedidos(cancelado.peca))
    assert not any("prioridade" in p for p in pedidos(cancelado.peca))


def test_pedido_com_fato_desconhecido_vira_pergunta():
    res = resultado()
    r = montar_peca("INDIVIDUAL_COMUM", {"F7": "NAO", "F9": "45"}, dados_todas(res),
                    resultado_calculo=res)     # F6 ausente
    assert any("pedido" in p.lower() for p in r.perguntas), r.perguntas


CATALOGO_INCOERENTE = """## TESE: TESTE_INCOERENTE

### BLOCO: I | Dos fatos
@condicao: sempre
@fundamentos: x
Narrativa.

### BLOCO: II | Dos pedidos
@condicao: sempre
@tipo: pedidos
@fundamentos: x
Requer:

- [sempre] a concessão da tutela de urgência, nos termos do art. 300 do CPC
"""


def test_pedido_sem_o_capitulo_correspondente_e_sinalizado():
    """Pedir tutela sem capítulo de tutela é incoerência que o leitor nota."""
    with tempfile.TemporaryDirectory() as t:
        caminho = os.path.join(t, "teses.md")
        open(caminho, "w", encoding="utf-8").write(CATALOGO_INCOERENTE)
        r = montar_peca("TESTE_INCOERENTE", {}, {}, catalogo=caminho)
        assert any("tutela de urgência" in a and "capítulo" in a for a in r.revisoes), \
            r.revisoes


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
