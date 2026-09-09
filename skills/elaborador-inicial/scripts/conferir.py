"""Conferência — última barreira antes de liberar a peça.

Compara os valores da petição com os valores de origem e verifica se o DOCX cumpre o
requisito de edição. Cada verificação aqui existe porque um erro real passou: as duas
peças protocoladas analisadas em `docs/04` e `docs/05` reprovam neste módulo.

Achado com gravidade BLOQUEIA impede a liberação do documento. A skill não "avisa e
segue" — peça errada protocolada é o pior cenário do projeto.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass, field
from decimal import Decimal

from calcular_reajuste import Resultado, d, q, _brl, _pct


BLOQUEIA, ALERTA = "BLOQUEIA", "ALERTA"
TOLERANCIA = Decimal("0.01")        # arredondamento de exibição


@dataclass
class Achado:
    codigo: str
    gravidade: str
    onde: str
    o_que: str
    esperado: str = ""
    encontrado: str = ""

    def __str__(self) -> str:
        base = f"[{self.codigo}] {self.gravidade}  {self.onde}: {self.o_que}"
        if self.esperado or self.encontrado:
            base += f"\n        esperado: {self.esperado}\n        na peça:  {self.encontrado}"
        return base


@dataclass
class Conferencia:
    achados: list[Achado] = field(default_factory=list)

    @property
    def liberado(self) -> bool:
        return not any(a.gravidade == BLOQUEIA for a in self.achados)

    def bloqueios(self) -> list[Achado]:
        return [a for a in self.achados if a.gravidade == BLOQUEIA]

    def relatorio(self) -> str:
        if not self.achados:
            return "CONFERÊNCIA: nada a apontar.\nDOCUMENTO LIBERADO para revisão humana."
        L = [f"CONFERÊNCIA: {len(self.bloqueios())} bloqueio(s), "
             f"{len(self.achados) - len(self.bloqueios())} alerta(s)", ""]
        for a in sorted(self.achados, key=lambda x: x.gravidade != BLOQUEIA):
            L.append(str(a))
        L.append("")
        L.append("DOCUMENTO LIBERADO para revisão humana." if self.liberado
                 else "DOCUMENTO NÃO LIBERADO. Corrija os bloqueios acima.")
        return "\n".join(L)


# --------------------------------------------------------------------------- #
# Parte 1 — consistência interna do cálculo
# --------------------------------------------------------------------------- #

def conferir_calculo(res: Resultado) -> list[Achado]:
    achados: list[Achado] = []

    # C3 — a linha de totais tem que fechar consigo mesma.
    # A planilha real do escritório reprova aqui: 133.776,67 − 80.153,61 = 53.623,06,
    # mas o total da coluna Diferença diz 36.738,93.
    dif_totais = res.total_pago - res.total_devido
    if abs(q(dif_totais) - q(res.total_diferenca)) > TOLERANCIA:
        achados.append(Achado(
            "C3", BLOQUEIA, "totais do cálculo",
            "total pago menos total devido não fecha com o total da coluna Diferença",
            esperado=_brl(dif_totais), encontrado=_brl(res.total_diferenca)))

    # C4 — janela da restituição congelada antes do fim da série.
    for erro in res.conferir():
        if "marco congelado" in erro:
            achados.append(Achado(
                "C4", BLOQUEIA, "restituição", erro,
                esperado=f"janela terminando em {res.linhas[-1].competencia.rotulo}",
                encontrado=f"janela terminando em {res.janela_restituicao[1]}"))

    # C11 — pendência de faixa etária não resolvida.
    for p in res.pendencias:
        achados.append(Achado(
            "C11", BLOQUEIA, p.competencia,
            "reajuste fora do mês de aniversário sem decisão sobre faixa etária",
            esperado="decisão humana registrada", encontrado=_pct(p.percentual)))

    for b in res.bloqueios:
        achados.append(Achado("C13", BLOQUEIA, "cálculo", b))

    return achados


# --------------------------------------------------------------------------- #
# Parte 2 — a peça contra os valores de origem
# --------------------------------------------------------------------------- #

RE_VALOR = re.compile(r"R\$\s?([\d.]{1,15},\d{2})")
RE_PCT = re.compile(r"(-?\d{1,3},\d{1,2})\s?%")

# Nomes com que a peça se refere a cada valor calculado.
CAMPOS = {
    "restituicao": "restituição dos últimos 3 anos",
    "diferenca_mensal": "diferença mensal",
    "valor_pago_atual": "valor pago atual",
    "valor_devido_atual": "valor devido atual",
}


def valores_de_origem(res: Resultado, meses_restituicao: int = 36,
                      ate: tuple[int, int] | None = None) -> dict[str, Decimal]:
    return {
        "restituicao": res.restituicao(meses_restituicao, ate),
        "diferenca_mensal": res.diferenca_mensal,
        "valor_pago_atual": res.valor_pago_atual,
        "valor_devido_atual": res.valor_devido_atual,
    }


def conferir_peca(texto: str, res: Resultado,
                  declarados: dict[str, str] | None = None,
                  formula_valor_da_causa: str = "",
                  valor_da_causa: str = "") -> list[Achado]:
    """`declarados` mapeia campo → valor como escrito na peça (ex.: 'R$ 36.738,93')."""
    achados: list[Achado] = []
    origem = valores_de_origem(res)
    declarados = declarados or {}

    # C6/C7/C12 — cada valor nomeado tem que bater com o cálculo.
    for campo, escrito in declarados.items():
        if campo not in origem:
            continue
        try:
            na_peca = d(escrito)
        except Exception:
            achados.append(Achado("C6", BLOQUEIA, CAMPOS.get(campo, campo),
                                  "valor ilegível na peça", encontrado=escrito))
            continue
        if abs(na_peca - q(origem[campo])) > TOLERANCIA:
            achados.append(Achado(
                "C6", BLOQUEIA, CAMPOS.get(campo, campo),
                "valor da peça diverge do cálculo",
                esperado=_brl(origem[campo]), encontrado=_brl(na_peca)))

    # C2 — o mesmo dado citado com números diferentes em pontos diferentes da peça.
    # A peça CASSI trazia 12,79% numa tabela e 12,88% em outra, para o mesmo reajuste.
    for pct, ocorrencias in _percentuais_conflitantes(texto).items():
        achados.append(Achado(
            "C2", BLOQUEIA, "corpo da peça",
            f"percentuais próximos e divergentes para o que parece ser o mesmo reajuste",
            esperado="um único percentual por reajuste",
            encontrado=" e ".join(sorted(ocorrencias))))

    # C1 — valor citado como patamar/limite que não existe na série calculada.
    # Na peça CASSI a tutela pedia R$ 2.526,89, valor ausente da própria tabela.
    conhecidos = {q(l.competencia.valor_pago) for l in res.linhas}
    conhecidos |= {q(l.valor_devido) for l in res.linhas}
    conhecidos |= {q(v) for v in origem.values()}
    for trecho, valor in _valores_de_patamar(texto):
        if valor not in conhecidos:
            achados.append(Achado(
                "C1", BLOQUEIA, "pedido de tutela",
                "valor pedido como patamar não existe no cálculo",
                esperado="um valor da tabela de reajuste",
                encontrado=f"{_brl(valor)} em “{trecho[:80]}…”"))

    # C5 — valor da causa contra a fórmula que a própria peça declara.
    if valor_da_causa and formula_valor_da_causa:
        achados += _conferir_valor_da_causa(valor_da_causa, formula_valor_da_causa, res)

    return achados


def _percentuais_conflitantes(texto: str) -> dict[str, set[str]]:
    """Agrupa percentuais que diferem por menos de 0,3 ponto — perto demais para serem
    reajustes distintos, longe demais para serem o mesmo número."""
    achados: dict[str, set[str]] = {}
    vistos = sorted({m.group(1) for m in RE_PCT.finditer(texto)},
                    key=lambda s: Decimal(s.replace(".", "").replace(",", ".")))
    for i, a in enumerate(vistos):
        for b in vistos[i + 1:]:
            va, vb = d(a), d(b)
            if va == vb:
                continue
            if abs(vb - va) <= Decimal("0.3"):
                achados.setdefault(a, set()).update({f"{a}%", f"{b}%"})
    return achados


PALAVRAS_PATAMAR = re.compile(
    r"\b(?:patamar|limite|limitar|limitando|limitação|reduzir|reduzindo|fixar)\b",
    re.IGNORECASE)

# Fim de frase é ponto seguido de espaço ou fim do texto. Separar em qualquer ponto
# quebraria "R$ 2.526,89" no separador de milhar e o valor se perderia.
FIM_DE_FRASE = re.compile(r"(?<=\.)\s+|\n+")


def _valores_de_patamar(texto: str) -> list[tuple[str, Decimal]]:
    saida = []
    for frase in FIM_DE_FRASE.split(texto):
        if not PALAVRAS_PATAMAR.search(frase):
            continue
        for m in RE_VALOR.finditer(frase):
            saida.append((frase.strip(), d(m.group(1))))
    return saida


def _conferir_valor_da_causa(escrito: str, formula: str, res: Resultado) -> list[Achado]:
    """Fórmulas aceitas: 'restituicao', 'restituicao+12x_diferenca', '2x_restituicao'."""
    valor = d(escrito)
    rest = res.restituicao()
    calculos = {
        "restituicao": rest,
        "restituicao+12x_diferenca": rest + res.diferenca_mensal * 12,
        "2x_restituicao": rest * 2,
        "12x_diferenca": res.diferenca_mensal * 12,
    }
    if formula not in calculos:
        return [Achado("C5", ALERTA, "valor da causa",
                       f"fórmula “{formula}” não reconhecida — não pude conferir")]
    esperado = calculos[formula]
    if abs(valor - q(esperado)) > TOLERANCIA:
        # É o caso da peça CASSI: valor da causa era o dobro da restituição, mas o texto
        # o justificava como restituição mais doze meses de diferença.
        coincide = [nome for nome, v in calculos.items()
                    if abs(valor - q(v)) <= TOLERANCIA]
        pista = f" (bate com “{coincide[0]}”)" if coincide else ""
        return [Achado("C5", BLOQUEIA, "valor da causa",
                       f"não confere com a fórmula declarada na peça{pista}",
                       esperado=_brl(esperado), encontrado=_brl(valor))]
    return []


# --------------------------------------------------------------------------- #
# Parte 3 — o DOCX cumpre o requisito de edição?
# --------------------------------------------------------------------------- #

FONTE_PADRAO = "Segoe UI"
TAMANHO_IMAGEM_DE_TABELA = 60_000     # bytes; acima disso não é ícone nem timbre


def conferir_editabilidade(caminho_docx: str) -> list[Achado]:
    """O requisito não negociável: a colega precisa conseguir corrigir qualquer valor
    no Word. Tabela em imagem, proteção ou campo travado quebram isso."""
    achados: list[Achado] = []
    with zipfile.ZipFile(caminho_docx) as z:
        nomes = z.namelist()
        doc = z.read("word/document.xml").decode("utf-8", "replace")

        # C9 — proteção de documento com atributos de fato restringe a edição.
        if "word/settings.xml" in nomes:
            cfg = z.read("word/settings.xml").decode("utf-8", "replace")
            m = re.search(r"<w:documentProtection([^>]*)/?>", cfg)
            if m and m.group(1).strip(" /"):
                achados.append(Achado("C9", BLOQUEIA, "settings.xml",
                                      "documento protegido contra edição",
                                      encontrado=m.group(0)))

        # C10 — só o content control TRAVADO impede a edição. Os dois documentos reais
        # do escritório têm w:sdt sem nenhum w:lock: são destravados e editáveis
        # normalmente. Bloquear por w:sdt reprovaria toda peça do escritório.
        travas = [v for v in re.findall(r'<w:lock[^>]*w:val="([^"]+)"', doc)
                  if v != "unlocked"]
        if travas:
            achados.append(Achado(
                "C10", BLOQUEIA, "document.xml",
                "content control travado — o conteúdo não pode ser corrigido no Word",
                esperado="nenhum w:lock", encontrado=", ".join(sorted(set(travas)))))

        # C8 — imagem grande **referenciada pelo corpo** é, quase sempre, tabela
        # renderizada. O timbre é referenciado por cabeçalho e rodapé, não pelo corpo,
        # e por isso não cai aqui nem quando é pesado.
        do_corpo = set(re.findall(r'r:(?:id|embed)="([^"]+)"', doc))
        alvos = set()
        if "word/_rels/document.xml.rels" in nomes:
            rels = z.read("word/_rels/document.xml.rels").decode("utf-8", "replace")
            for bloco in re.findall(r"<Relationship\b[^>]*/>", rels):
                attrs = dict(re.findall(r'(\w+)="([^"]*)"', bloco))
                if attrs.get("Id") in do_corpo and "media/" in attrs.get("Target", ""):
                    alvos.add("word/" + attrs["Target"].lstrip("./").replace("../", ""))
        grandes = [(n, z.getinfo(n).file_size) for n in nomes
                   if n in alvos and z.getinfo(n).file_size > TAMANHO_IMAGEM_DE_TABELA]
        corpo = len(re.findall(r"<w:drawing>", doc))
        for nome, tamanho in grandes:
            achados.append(Achado(
                "C8", BLOQUEIA, nome,
                "imagem grande embutida — se for tabela, os valores não podem ser "
                "corrigidos no Word",
                esperado="tabela nativa (w:tbl)", encontrado=f"{tamanho//1024} KB"))
        if corpo and not re.search(r"<w:tbl[\s>/]", doc):
            achados.append(Achado("C8", ALERTA, "document.xml",
                                  "há imagens no corpo e nenhuma tabela nativa"))

        # C14 — fonte fora do padrão do escritório.
        fontes = set(re.findall(r'w:ascii="([^"]+)"', doc))
        estranhas = {f for f in fontes if not f.startswith("Segoe UI")}
        if estranhas:
            achados.append(Achado("C14", ALERTA, "document.xml",
                                  "fonte fora do padrão do escritório",
                                  esperado=FONTE_PADRAO,
                                  encontrado=", ".join(sorted(estranhas))))
    return achados


# --------------------------------------------------------------------------- #

def conferir(res: Resultado, texto_peca: str = "", caminho_docx: str = "",
             declarados: dict[str, str] | None = None,
             formula_valor_da_causa: str = "", valor_da_causa: str = "") -> Conferencia:
    c = Conferencia()
    c.achados += conferir_calculo(res)
    if texto_peca:
        c.achados += conferir_peca(texto_peca, res, declarados,
                                   formula_valor_da_causa, valor_da_causa)
    if caminho_docx:
        c.achados += conferir_editabilidade(caminho_docx)
    return c
