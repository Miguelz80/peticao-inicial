"""Roteiro — liga o texto jurídico de cada tese aos blocos do Gerador.

Lê `references/teses.md`, escolhe os blocos que se aplicam ao caso, preenche os campos
e devolve uma `Peca` pronta para `gerar_peticao.montar()`.

Três travas, todas por motivo prático:

1. **Campo sem valor interrompe a geração.** Peça com `{restituicao}` literal, ou com
   um branco no lugar do valor, é pior do que peça nenhuma — passa despercebida na
   leitura rápida e vai a protocolo.
2. **Bloco sem texto do escritório vira marcador visível e bloqueia a entrega.** Nunca
   redigir fundamentação jurídica de improviso para tapar buraco de modelo faltando.
3. **Bloco condicional cujo fato é desconhecido não some em silêncio** — volta como
   pergunta. Um capítulo que deveria existir e não existe é invisível na revisão.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field

from gerar_peticao import (
    Peca, Titulo, Paragrafo, Citacao, Espaco, tabela_de_reajuste, caixa_de_resumo,
)

CATALOGO = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "references", "teses.md")

MARCA_PENDENTE = "⟦PENDENTE"


class CampoAusente(Exception):
    pass


class TeseSemCatalogo(Exception):
    pass


# --------------------------------------------------------------------------- #
# Leitura do catálogo
# --------------------------------------------------------------------------- #

@dataclass
class BlocoTese:
    numeral: str
    titulo: str
    condicao: str = "sempre"
    fundamentos: str = ""
    pendente: str = ""
    tabela: str = ""
    paragrafos: list[str] = field(default_factory=list)


@dataclass
class Tese:
    nome: str
    pendente: str = ""
    blocos: list[BlocoTese] = field(default_factory=list)


RE_TESE = re.compile(r"^## TESE:\s*(\S+)\s*$")
RE_BLOCO = re.compile(r"^### BLOCO:\s*([^|]+?)\s*\|\s*(.+?)\s*$")
RE_DIRETIVA = re.compile(r"^@(\w+):\s*(.*)$")


def carregar(caminho: str = CATALOGO) -> dict[str, Tese]:
    with open(caminho, encoding="utf-8") as fh:
        linhas = fh.read().split("\n")

    teses: dict[str, Tese] = {}
    tese = bloco = None
    dentro_do_formato = False
    buffer: list[str] = []

    def fechar_paragrafo():
        if bloco is not None and buffer:
            bloco.paragrafos.append(" ".join(buffer).strip())
        buffer.clear()

    for linha in linhas:
        if linha.startswith("```"):
            dentro_do_formato = not dentro_do_formato
            continue
        if dentro_do_formato:
            continue

        m = RE_TESE.match(linha)
        if m:
            fechar_paragrafo()
            tese = Tese(nome=m.group(1))
            teses[tese.nome] = tese
            bloco = None
            continue

        m = RE_BLOCO.match(linha)
        if m and tese is not None:
            fechar_paragrafo()
            bloco = BlocoTese(numeral=m.group(1), titulo=m.group(2))
            tese.blocos.append(bloco)
            continue

        m = RE_DIRETIVA.match(linha)
        if m and tese is not None:
            fechar_paragrafo()
            chave, valor = m.group(1), m.group(2).strip()
            alvo = bloco if bloco is not None else tese
            if hasattr(alvo, chave):
                setattr(alvo, chave, valor)
            continue

        if bloco is None:
            continue
        # separadores e outros títulos do arquivo não são texto da peça
        if linha.strip().startswith(("---", "#")):
            fechar_paragrafo()
            continue
        if linha.strip():
            buffer.append(linha.strip())
        else:
            fechar_paragrafo()

    fechar_paragrafo()
    return teses


# --------------------------------------------------------------------------- #
# Condições
# --------------------------------------------------------------------------- #

RE_CONDICAO = re.compile(r"^(\w+)\s*(==|!=|>=|<=)\s*(.+)$")


def avaliar(condicao: str, fatos: dict[str, str]) -> bool | None:
    """True aplica, False não aplica, None = o fato é desconhecido (vira pergunta)."""
    condicao = (condicao or "sempre").strip()
    if condicao in ("", "sempre"):
        return True
    m = RE_CONDICAO.match(condicao)
    if not m:
        return None
    fato, operador, esperado = m.group(1), m.group(2), m.group(3).strip()
    if fato not in fatos or fatos[fato] in (None, "", "DESCONHECIDO"):
        return None
    valor = str(fatos[fato])
    if operador in (">=", "<="):
        try:
            a, b = float(valor.replace(",", ".")), float(esperado.replace(",", "."))
        except ValueError:
            return None
        return a >= b if operador == ">=" else a <= b
    return (valor == esperado) if operador == "==" else (valor != esperado)


# --------------------------------------------------------------------------- #
# Preenchimento
# --------------------------------------------------------------------------- #

ROMANOS = [(1000, "M"), (900, "CM"), (500, "D"), (400, "CD"), (100, "C"), (90, "XC"),
           (50, "L"), (40, "XL"), (10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def romano(n: int) -> str:
    saida = []
    for valor, simbolo in ROMANOS:
        while n >= valor:
            saida.append(simbolo)
            n -= valor
    return "".join(saida)


RE_CAMPO = re.compile(r"\{(\w+)\}")


def preencher(texto: str, dados: dict[str, str]) -> tuple[str, set[str]]:
    faltando = {c for c in RE_CAMPO.findall(texto)
                if c not in dados or dados[c] in (None, "")}
    if faltando:
        return texto, faltando
    return RE_CAMPO.sub(lambda m: str(dados[m.group(1)]), texto), set()


# --------------------------------------------------------------------------- #
# Montagem
# --------------------------------------------------------------------------- #

@dataclass
class Roteiro:
    peca: Peca
    pendencias: list[str] = field(default_factory=list)
    perguntas: list[str] = field(default_factory=list)

    @property
    def pronto(self) -> bool:
        return not self.pendencias and not self.perguntas


def montar_peca(tese_nome: str, fatos: dict[str, str], dados: dict[str, str],
                resultado_calculo=None, catalogo: str = CATALOGO) -> Roteiro:
    teses = carregar(catalogo)
    if tese_nome not in teses:
        raise TeseSemCatalogo(
            f"tese “{tese_nome}” não está em {os.path.basename(catalogo)} — "
            f"disponíveis: {', '.join(sorted(teses))}")

    tese = teses[tese_nome]
    r = Roteiro(peca=Peca())
    if tese.pendente:
        r.pendencias.append(f"{tese_nome}: {tese.pendente}")

    faltando_geral: set[str] = set()
    numero = 0

    for bloco in tese.blocos:
        aplica = avaliar(bloco.condicao, fatos)
        if aplica is False:
            continue
        if aplica is None:
            r.perguntas.append(
                f"O capítulo “{bloco.titulo}” depende de “{bloco.condicao}”, e esse "
                f"dado não está definido. Ele entra na peça ou não?")
            continue

        numero += 1
        r.peca.add(Titulo(f"{romano(numero)}.", bloco.titulo))

        if bloco.pendente:
            r.pendencias.append(f"{tese_nome} · {bloco.titulo}: {bloco.pendente}")
            r.peca.add(Paragrafo(
                f"**{MARCA_PENDENTE}: texto não disponível.** Este capítulo precisa "
                f"sustentar: {bloco.fundamentos}⟧"))
            continue

        for paragrafo in bloco.paragrafos:
            # "> " marca ementa de julgado: sai recuada e em itálico, como no padrão
            # do escritório, e não como parágrafo comum de argumentação.
            citacao = paragrafo.startswith("> ")
            texto, faltando = preencher(paragrafo[2:] if citacao else paragrafo, dados)
            faltando_geral |= faltando
            r.peca.add(Citacao(texto) if citacao else Paragrafo(texto))

        if bloco.tabela == "reajuste" and resultado_calculo is not None:
            r.peca.add(caixa_de_resumo(resultado_calculo),
                       tabela_de_reajuste(resultado_calculo))

    if faltando_geral:
        raise CampoAusente(
            "faltam dados para preencher a peça: "
            + ", ".join(sorted(faltando_geral))
            + ". Peça com campo em branco ou com o marcador literal no meio do texto "
              "passa despercebida na revisão — a geração para aqui.")

    r.peca.add(Espaco())
    return r
