"""Leitura da tabela de cálculo — do texto extraído para competências.

Era o elo que faltava entre o que o extrator lê e o que o Calculador consome: a
planilha do escritório chega em **PDF**, não em xlsx, e sem isto o cálculo pronto
parava como documento indefinido e nunca chegava ao cálculo.

O leitor é deliberadamente tolerante com a forma e rigoroso com o resultado: aceita
`janeiro/2015`, `01/2015` e `R$ 1.234,56` em qualquer arranjo de colunas, mas devolve
**avisos** sempre que algo ficou duvidoso — buraco na série, competência repetida,
valor que não deu para ler. Aviso não é enfeite: a série é a base de todo o cálculo,
e um mês faltando desloca a cadeia inteira.
"""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation

from calcular_reajuste import Competencia, ANUAL, FAIXA_ETARIA, INDEFINIDO, d


MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
         "agosto", "setembro", "outubro", "novembro", "dezembro"]
MESES_SEM_ACENTO = [unicodedata.normalize("NFD", m).encode("ascii", "ignore").decode()
                    for m in MESES]

RE_MES_NOME = re.compile(r"\b(" + "|".join(MESES + MESES_SEM_ACENTO) + r")\s*/\s*(\d{4})\b",
                         re.IGNORECASE)
RE_MES_NUM = re.compile(r"\b(0?[1-9]|1[0-2])\s*/\s*(20\d{2})\b")
RE_VALOR = re.compile(r"R\$\s*([\d.]{1,15},\d{2})")
RE_PCT = re.compile(r"(-?\d{1,3},\d{1,2})\s*%")
RE_TIPO = re.compile(r"\b(anual|faixa\s*et[áa]ria)\b", re.IGNORECASE)

VALOR_DE_PLACEHOLDER = Decimal("0.01")


def competencia_da_linha(linha: str) -> tuple[int, int] | None:
    m = RE_MES_NOME.search(linha)
    if m:
        nome = unicodedata.normalize("NFD", m.group(1).lower()) \
            .encode("ascii", "ignore").decode()
        return int(m.group(2)), MESES_SEM_ACENTO.index(nome) + 1
    m = RE_MES_NUM.search(linha)
    if m:
        return int(m.group(2)), int(m.group(1))
    return None


def _valores(linha: str) -> list[Decimal]:
    saida = []
    for bruto in RE_VALOR.findall(linha):
        try:
            saida.append(d(bruto))
        except (InvalidOperation, ValueError):
            pass
    return saida


def analisar(linha: str) -> dict | None:
    """Análise única de uma linha de tabela. Tanto o Eixo A quanto o Calculador leem
    daqui — antes cada um reparseava do seu jeito, e a versão formatada perdia o
    "R$" que a outra procurava."""
    chave = competencia_da_linha(linha)
    if not chave:
        return None
    valores = _valores(linha)
    tipo = RE_TIPO.search(linha)
    return {
        "ano": chave[0], "mes": chave[1],
        "valores": valores,
        "percentuais": RE_PCT.findall(linha),
        "tipo": tipo.group(1) if tipo else "",
    }


def linhas_de_texto(texto: str) -> list[list[str]]:
    """Uma linha por competência, colunas como texto. Alimenta o Eixo A, que decide o
    regime pelo preenchimento das colunas de valor devido."""
    saida = []
    for linha in texto.split("\n"):
        a = analisar(linha)
        if not a:
            continue
        v, p = a["valores"], a["percentuais"]
        saida.append([
            f"{MESES[a['mes']-1]}/{a['ano']}",
            _brl(v[0]) if v else "",
            p[0] if p else "",
            a["tipo"],
            p[1] if len(p) > 1 else "",
            _brl(v[-2]) if len(v) >= 3 else "",
            _brl(v[-1]) if len(v) >= 2 else "",
        ])
    return saida


def _brl(valor: Decimal) -> str:
    return "R$ " + f"{valor:,.2f}".replace(",", "·").replace(".", ",").replace("·", ".")


def competencias_de(planilha: dict) -> tuple[list[Competencia], list[str]]:
    """Converte uma planilha extraída (grade ou texto) em competências."""
    avisos: list[str] = []

    if planilha.get("linhas"):
        brutas = [" ".join(str(c) for c in linha if c is not None)
                  for linha in planilha["linhas"]]
        numeros = {i: _numeros_soltos(linha)
                   for i, linha in enumerate(planilha["linhas"])}
    else:
        brutas = (planilha.get("texto_solto") or "").split("\n")
        numeros = {}

    comps: list[Competencia] = []
    vistas: set[tuple[int, int]] = set()
    ilegiveis = 0

    for i, bruto in enumerate(brutas):
        a = analisar(bruto)
        if not a:
            continue
        ano, mes = a["ano"], a["mes"]
        valores = a["valores"] or numeros.get(i, [])
        if not valores:
            ilegiveis += 1
            continue
        if (ano, mes) in vistas:
            avisos.append(f"competência repetida na planilha: {MESES[mes-1]}/{ano}")
            continue
        vistas.add((ano, mes))

        tipo = INDEFINIDO
        if a["tipo"]:
            tipo = ANUAL if a["tipo"].lower() == "anual" else FAIXA_ETARIA

        comps.append(Competencia(ano=ano, mes=mes, valor_pago=valores[0],
                                 tipo_reajuste=tipo))

    if ilegiveis:
        avisos.append(f"{ilegiveis} linha(s) com competência mas sem valor legível — "
                      f"confira se a leitura do arquivo saiu completa")

    comps.sort(key=lambda c: (c.ano, c.mes))
    avisos += _conferir_serie(comps)
    return comps, avisos


def _numeros_soltos(linha) -> list[Decimal]:
    """Planilha em grade traz número, não texto com R$."""
    saida = []
    for celula in linha:
        if isinstance(celula, (int, float, Decimal)):
            saida.append(Decimal(str(celula)))
    return saida


def _conferir_serie(comps: list[Competencia]) -> list[str]:
    """Buraco na série desloca a cadeia inteira do valor devido, e some sem alarde
    se ninguém olhar. Por isso vira aviso, não silêncio."""
    avisos = []
    reais = [c for c in comps if c.valor_pago > VALOR_DE_PLACEHOLDER]
    if not reais:
        return ["nenhuma competência com valor real — a planilha veio vazia?"]

    placeholders = len(comps) - len(reais)
    if placeholders:
        avisos.append(f"{placeholders} competência(s) com valor de R$ 0,01 — linhas de "
                      f"preenchimento do modelo, ignoradas no cálculo")

    faltando = []
    ano, mes = reais[0].ano, reais[0].mes
    existentes = {(c.ano, c.mes) for c in reais}
    while (ano, mes) <= (reais[-1].ano, reais[-1].mes):
        if (ano, mes) not in existentes:
            faltando.append(f"{MESES[mes-1]}/{ano}")
        mes += 1
        if mes == 13:
            mes, ano = 1, ano + 1
    if faltando:
        amostra = ", ".join(faltando[:6]) + ("…" if len(faltando) > 6 else "")
        avisos.append(f"{len(faltando)} competência(s) faltando na série: {amostra}")
    return avisos


def conferir_importado(planilha: dict, resultado) -> list[str]:
    """Compara o valor devido que veio na planilha com o que recalculamos.

    Vale mesmo quando o regime é CALCULO_PRONTO — e principalmente nele: planilha
    pronta também chega errada, e aceitar o número do arquivo sem recontar é abrir
    mão da única verificação independente que existe.
    """
    calculados = {l.competencia.chave: l.valor_devido for l in resultado.linhas}
    divergentes, sem_par = [], 0

    brutas = (planilha.get("texto_solto") or "").split("\n")
    if planilha.get("linhas") and not planilha.get("texto_solto"):
        brutas = [" ".join(str(c) for c in linha if c is not None)
                  for linha in planilha["linhas"]]

    for bruto in brutas:
        a = analisar(bruto)
        if not a or len(a["valores"]) < 3:
            continue
        importado = a["valores"][-2]
        if importado <= VALOR_DE_PLACEHOLDER:
            continue
        nosso = calculados.get((a["ano"], a["mes"]))
        if nosso is None:
            sem_par += 1
            continue
        if abs(importado - nosso) > Decimal("0.01"):
            divergentes.append(f"{MESES[a['mes']-1]}/{a['ano']}: planilha "
                               f"{_brl(importado)}, recálculo {_brl(nosso)}")

    avisos = []
    if divergentes:
        amostra = "; ".join(divergentes[:4]) + ("…" if len(divergentes) > 4 else "")
        avisos.append(f"{len(divergentes)} competência(s) com valor devido divergente "
                      f"entre a planilha e o recálculo — {amostra}")
    if sem_par:
        avisos.append(f"{sem_par} competência(s) da planilha ficaram sem par no "
                      f"recálculo")
    return avisos
