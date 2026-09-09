"""Gerador da petição — monta o DOCX a partir do modelo real do escritório.

**Requisito não negociável:** o arquivo entregue é um `.docx` nativo, integralmente
editável no Word. A colega que opera precisa conseguir corrigir qualquer valor à mão,
sem rodar a skill de novo. Por isso, aqui não se emite proteção de documento, content
control travado, nem tabela em imagem — a tabela de reajuste é `w:tbl` de verdade, com
cada célula digitável.

**Não monta o arquivo do zero.** O timbre do escritório vive nas imagens do DOCX
original (logo no cabeçalho, contatos no rodapé) e é referenciado pelo `sectPr` do
corpo. O gerador copia o modelo real, troca só o `word/document.xml` e **reaproveita o
`sectPr` original palavra por palavra** — é o que mantém margens, tamanho de página e,
principalmente, os vínculos de cabeçalho e rodapé.

Aparência das tabelas: `references/estilo-tabelas.md`, medida da peça real. A decisão
foi não mudar o visual, só a técnica.
"""

from __future__ import annotations

import re
import shutil
import zipfile
from dataclasses import dataclass, field
from decimal import Decimal

from calcular_reajuste import Resultado, tabela as tabela_calculo, resumo as resumo_calculo


# --------------------------------------------------------------------------- #
# Estilo do escritório
# --------------------------------------------------------------------------- #

FONTE = "Segoe UI"
ENTRELINHA = "360"          # 1,5 linha
DEPOIS = "140"
RECUO = "1417"              # 2,5 cm

# Paleta medida pixel a pixel na peça real (references/estilo-tabelas.md).
CABECALHO_TABELA = "2C3E6B"
ZEBRA = "F5F8FB"
LINHA_VIGENTE = "FFF8E1"
LINHA_TOTAL = "EEF2F8"
CAIXA_RESUMO = "EEF5FB"
TEXTO_DESTAQUE = "C0392B"   # diferença e percentual
TEXTO_ROTULO = "1A5FA8"
TEXTO_CORPO = "1A1A2E"


def esc(texto: str) -> str:
    return (str(texto).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _rpr(negrito=False, italico=False, cor=None, tamanho=None, branco=False) -> str:
    p = [f'<w:rFonts w:ascii="{FONTE}" w:hAnsi="{FONTE}" w:cs="{FONTE}"/>']
    if negrito:
        p.append("<w:b/><w:bCs/>")
    if italico:
        p.append("<w:i/><w:iCs/>")
    if branco:
        p.append('<w:color w:val="FFFFFF"/>')
    elif cor:
        p.append(f'<w:color w:val="{cor}"/>')
    if tamanho:
        p.append(f'<w:sz w:val="{tamanho}"/><w:szCs w:val="{tamanho}"/>')
    return f"<w:rPr>{''.join(p)}</w:rPr>"


RE_NEGRITO = re.compile(r"\*\*(.+?)\*\*", re.S)


def runs(texto: str, **kw) -> str:
    """`**assim**` vira negrito. Mantém o resto do estilo do parágrafo."""
    saida, pos = [], 0
    for m in RE_NEGRITO.finditer(texto):
        if m.start() > pos:
            saida.append(f'<w:r>{_rpr(**kw)}<w:t xml:space="preserve">'
                         f'{esc(texto[pos:m.start()])}</w:t></w:r>')
        forte = dict(kw); forte["negrito"] = True
        saida.append(f'<w:r>{_rpr(**forte)}<w:t xml:space="preserve">'
                     f'{esc(m.group(1))}</w:t></w:r>')
        pos = m.end()
    if pos < len(texto):
        saida.append(f'<w:r>{_rpr(**kw)}<w:t xml:space="preserve">'
                     f'{esc(texto[pos:])}</w:t></w:r>')
    return "".join(saida)


def paragrafo(texto: str = "", recuo=True, alinhamento="both", esquerda=None,
              **kw) -> str:
    ppr = [f'<w:spacing w:after="{DEPOIS}" w:line="{ENTRELINHA}" w:lineRule="auto"/>']
    if esquerda:
        ppr.append(f'<w:ind w:left="{esquerda}"/>')
    elif recuo:
        ppr.append(f'<w:ind w:firstLine="{RECUO}"/>')
    ppr.append(f'<w:jc w:val="{alinhamento}"/>')
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{runs(texto, **kw) if texto else ''}</w:p>"


# --------------------------------------------------------------------------- #
# Blocos
# --------------------------------------------------------------------------- #

class Bloco:
    def xml(self) -> str:                       # pragma: no cover
        raise NotImplementedError


@dataclass
class Enderecamento(Bloco):
    texto: str

    def xml(self) -> str:
        return paragrafo(f"**{self.texto}**", recuo=False)


@dataclass
class Paragrafo(Bloco):
    texto: str
    recuo: bool = True

    def xml(self) -> str:
        return paragrafo(self.texto, recuo=self.recuo)


@dataclass
class Titulo(Bloco):
    numeral: str
    texto: str

    def xml(self) -> str:
        return paragrafo(f"**{self.numeral}\t{self.texto.upper()}**")


@dataclass
class Subtitulo(Bloco):
    texto: str

    def xml(self) -> str:
        return paragrafo(f"**{self.texto}**")


@dataclass
class Citacao(Bloco):
    texto: str

    def xml(self) -> str:
        return paragrafo(self.texto, esquerda="720", italico=True)


@dataclass
class Espaco(Bloco):
    def xml(self) -> str:
        return "<w:p/>"


@dataclass
class Assinatura(Bloco):
    nome: str
    oab: str

    def xml(self) -> str:
        return (paragrafo(f"**{self.nome}**", recuo=False, alinhamento="center")
                + paragrafo(f"**{self.oab}**", recuo=False, alinhamento="center"))


@dataclass
class Tabela(Bloco):
    """Tabela nativa. Nunca imagem — é o requisito central do projeto."""
    linhas: list[list[str]]
    larguras: list[int] | None = None
    destaque_colunas: tuple[int, ...] = ()      # texto em vermelho, negrito
    linha_vigente: int | None = None            # índice da linha em âmbar
    tem_total: bool = True

    def xml(self) -> str:
        n = len(self.linhas[0])
        larguras = self.larguras or [int(9070 / n)] * n
        grid = "".join(f'<w:gridCol w:w="{w}"/>' for w in larguras)
        corpo = []
        for i, linha in enumerate(self.linhas):
            corpo.append(self._linha(i, linha, larguras))
        return (
            "<w:tbl><w:tblPr>"
            '<w:tblW w:w="5000" w:type="pct"/>'
            "<w:tblBorders>"
            + "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="D0DCE8"/>'
                      for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
            + "</w:tblBorders>"
            '<w:tblCellMar><w:top w:w="60" w:type="dxa"/><w:left w:w="90" w:type="dxa"/>'
            '<w:bottom w:w="60" w:type="dxa"/><w:right w:w="90" w:type="dxa"/></w:tblCellMar>'
            f"</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{''.join(corpo)}</w:tbl>"
            + "<w:p/>")

    def _linha(self, i: int, linha: list[str], larguras: list[int]) -> str:
        cabecalho = i == 0
        total = self.tem_total and i == len(self.linhas) - 1
        vigente = self.linha_vigente is not None and i == self.linha_vigente

        if cabecalho:
            fundo = CABECALHO_TABELA
        elif total:
            fundo = LINHA_TOTAL
        elif vigente:
            fundo = LINHA_VIGENTE
        elif i % 2 == 0:
            fundo = ZEBRA
        else:
            fundo = "FFFFFF"

        celulas = []
        for j, valor in enumerate(linha):
            destaque = j in self.destaque_colunas and not cabecalho
            estilo = dict(
                negrito=cabecalho or total or destaque,
                branco=cabecalho,
                cor=TEXTO_DESTAQUE if destaque else (None if cabecalho else TEXTO_CORPO),
                tamanho="18",
            )
            alinhamento = "center" if cabecalho else ("right" if j > 0 else "left")
            p = paragrafo(valor or "", recuo=False,
                          alinhamento=alinhamento, **estilo)
            celulas.append(
                f'<w:tc><w:tcPr><w:tcW w:w="{larguras[j]}" w:type="dxa"/>'
                f'<w:shd w:val="clear" w:color="auto" w:fill="{fundo}"/>'
                f'<w:vAlign w:val="center"/></w:tcPr>{p}</w:tc>')
        cabecalho_repete = "<w:trPr><w:tblHeader/></w:trPr>" if cabecalho else ""
        return f"<w:tr>{cabecalho_repete}{''.join(celulas)}</w:tr>"


@dataclass
class CaixaDestaque(Bloco):
    """As caixas RESUMO e ANÁLISE da peça real: tabela de uma célula com fundo."""
    rotulo: str
    linhas: list[str]

    def xml(self) -> str:
        conteudo = paragrafo(f"**{self.rotulo.upper()}**", recuo=False,
                             cor=TEXTO_ROTULO, tamanho="18")
        conteudo += "".join(paragrafo(l, recuo=False, tamanho="20") for l in self.linhas)
        return (
            '<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/>'
            '<w:tblBorders><w:top w:val="none"/><w:left w:val="none"/>'
            '<w:bottom w:val="none"/><w:right w:val="none"/></w:tblBorders>'
            '<w:tblCellMar><w:top w:w="140" w:type="dxa"/><w:left w:w="180" w:type="dxa"/>'
            '<w:bottom w:w="140" w:type="dxa"/><w:right w:w="180" w:type="dxa"/>'
            "</w:tblCellMar></w:tblPr>"
            '<w:tblGrid><w:gridCol w:w="9070"/></w:tblGrid>'
            f'<w:tr><w:tc><w:tcPr><w:tcW w:w="9070" w:type="dxa"/>'
            f'<w:shd w:val="clear" w:color="auto" w:fill="{CAIXA_RESUMO}"/></w:tcPr>'
            f"{conteudo}</w:tc></w:tr></w:tbl><w:p/>")


# --------------------------------------------------------------------------- #
# Peça
# --------------------------------------------------------------------------- #

@dataclass
class Peca:
    blocos: list[Bloco] = field(default_factory=list)

    def add(self, *blocos: Bloco) -> "Peca":
        self.blocos.extend(blocos)
        return self

    def corpo(self) -> str:
        return "".join(b.xml() for b in self.blocos)


def tabela_de_reajuste(res: Resultado) -> Tabela:
    """Converte a saída do Calculador na tabela nativa, com o realce da peça real:
    Diferença e Reajuste Devido em vermelho, linha vigente em âmbar."""
    linhas = tabela_calculo(res)
    return Tabela(
        linhas=linhas,
        larguras=[1100, 1250, 1250, 1150, 1250, 1300, 1300],
        destaque_colunas=(6,),
        linha_vigente=len(linhas) - 2,
    )


def caixa_de_resumo(res: Resultado) -> CaixaDestaque:
    r = resumo_calculo(res)
    return CaixaDestaque(
        rotulo="Resumo",
        linhas=[f"**{k}:** {v}" for k, v in r.items()],
    )


# --------------------------------------------------------------------------- #
# Montagem do arquivo
# --------------------------------------------------------------------------- #

RE_SECTPR = re.compile(r"<w:sectPr\b.*?</w:sectPr>", re.S)
RE_RAIZ = re.compile(r"<w:document\b[^>]*>", re.S)

PROIBIDOS = {
    "w:documentProtection": "proteção de documento",
    "w:sdt": "content control",
    "w:drawing": "imagem no corpo",
}


class ModeloInvalido(Exception):
    pass


def montar(modelo_docx: str, peca: Peca, saida_docx: str) -> str:
    """Copia o modelo do escritório e troca só o `document.xml`.

    Preserva `_rels`, `word/media`, cabeçalhos, rodapés, estilos — e reaproveita o
    `sectPr` original, que é o que carrega as referências do timbre. Sem isso, a peça
    sai sem logo e sem rodapé.
    """
    with zipfile.ZipFile(modelo_docx) as z:
        original = z.read("word/document.xml").decode("utf-8")

    raiz = RE_RAIZ.search(original)
    if not raiz:
        raise ModeloInvalido(f"{modelo_docx}: não achei a raiz <w:document>")

    sectpr = RE_SECTPR.findall(original)
    if not sectpr:
        raise ModeloInvalido(
            f"{modelo_docx}: não achei <w:sectPr>. Sem ele a peça sai sem timbre, "
            f"sem margem e sem tamanho de página do escritório.")

    novo = f"{raiz.group(0)}<w:body>{peca.corpo()}{sectpr[-1]}</w:body></w:document>"

    for marca, nome in PROIBIDOS.items():
        if f"<{marca}" in novo:
            raise ModeloInvalido(
                f"o documento gerado contém {nome} ({marca}) — quebra o requisito de "
                f"edição manual no Word")

    shutil.copyfile(modelo_docx, saida_docx)
    _reescrever(saida_docx, novo)
    return saida_docx


RE_RID = re.compile(r'r:(?:id|embed|link)="([^"]+)"')
RE_REL = re.compile(r"<Relationship\b[^>]*/>")
RE_ATTR = re.compile(r'(\w+)="([^"]*)"')


def _reescrever(caminho: str, document_xml: str) -> None:
    """Troca o document.xml e **poda a mídia que ficou órfã**.

    O modelo do escritório carrega as imagens das tabelas antigas. Se elas viessem
    junto, a peça nova sairia com centenas de KB de peso morto e a Conferência
    acusaria imagem de tabela num documento que não tem nenhuma. Cabeçalho e rodapé
    ficam intactos: o timbre é referenciado por eles, não pelo corpo.
    """
    with zipfile.ZipFile(caminho) as z:
        itens = {i.filename: z.read(i.filename) for i in z.infolist()}
        infos = {i.filename: i for i in z.infolist()}

    usados_no_corpo = set(RE_RID.findall(document_xml))
    rels_nome = "word/_rels/document.xml.rels"
    if rels_nome in itens:
        rels = itens[rels_nome].decode("utf-8")
        mantidas = []
        for bloco in RE_REL.findall(rels):
            attrs = dict(RE_ATTR.findall(bloco))
            eh_imagem = "/image" in attrs.get("Type", "")
            if eh_imagem and attrs.get("Id") not in usados_no_corpo:
                continue                      # relação de imagem que ninguém mais usa
            mantidas.append(bloco)
        itens[rels_nome] = RE_REL.sub("", rels).replace(
            "</Relationships>", "".join(mantidas) + "</Relationships>").encode("utf-8")

    # mídia ainda referenciada por qualquer parte (corpo, cabeçalhos, rodapés)
    referenciada = set()
    for nome, dados in itens.items():
        if not nome.endswith(".rels"):
            continue
        for bloco in RE_REL.findall(dados.decode("utf-8", "replace")):
            attrs = dict(RE_ATTR.findall(bloco))
            alvo = attrs.get("Target", "")
            if "media/" in alvo:
                referenciada.add("word/" + alvo.lstrip("./").replace("../", ""))

    itens["word/document.xml"] = document_xml.encode("utf-8")
    orfas = [n for n in itens
             if n.startswith("word/media/") and n not in referenciada]
    for n in orfas:
        del itens[n]

    with zipfile.ZipFile(caminho, "w", zipfile.ZIP_DEFLATED) as z:
        for nome, dados in itens.items():
            z.writestr(infos.get(nome, nome), dados)
