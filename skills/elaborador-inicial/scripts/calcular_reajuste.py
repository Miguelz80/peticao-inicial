"""Calculador atuarial — monta a tabela de reajuste devido.

Fórmula confirmada contra planilha real do escritório (cadeia de 9 anos, 9 passos
exatos, ver docs/05-achados-caso-sulamerica.md):

    devido[n] = devido[n-1] × (1 + índice ANS do período do aniversário)
                            × (1 + faixa etária legítima, quando houver)

Duas regras que vêm de erro observado, não de preferência:

1. **Não arredondar entre os anos.** Precisão cheia por dentro, arredondamento só na
   exibição. Arredondando ano a ano a cadeia erra centavos que se acumulam ao longo
   de uma década.
2. **Ano sem índice bloqueia o caso.** Nunca pular o ano, nunca estimar. Índice errado
   contamina toda a cadeia e é invisível na revisão da peça.

O que este módulo NÃO faz: decidir se um reajuste por faixa etária é legítimo. Isso é
juízo jurídico (Temas 952 e 1016 do STJ) — ele identifica e devolve para decisão humana.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP


# --------------------------------------------------------------------------- #
# Índices ANS — espelham references/indices-ans.md
# --------------------------------------------------------------------------- #

# Chave = ano de início do período (maio/ANO a abril/ANO+1).
INDICES_ANS: dict[int, Decimal] = {
    2015: Decimal("0.1355"),
    2016: Decimal("0.1357"),
    2017: Decimal("0.1355"),
    2018: Decimal("0.1000"),
    2019: Decimal("0.0735"),
    2020: Decimal("0.0814"),
    2021: Decimal("-0.0819"),   # único negativo da série
    2022: Decimal("0.1550"),
    2023: Decimal("0.0963"),
    2024: Decimal("0.0691"),
    2025: Decimal("0.0606"),
    2026: Decimal("0.0511"),
}

ANUAL, FAIXA_ETARIA, INDEFINIDO = "ANUAL", "FAIXA_ETARIA", ""
MESES_RESTITUICAO = 36          # Tema 610/STJ — prescrição trienal


def periodo_ans(ano: int, mes: int) -> int:
    """O período ANS vai de maio a abril. Aniversário em maio/dezembro usa o índice do
    próprio ano; em janeiro/abril, o do ano anterior."""
    return ano if mes >= 5 else ano - 1


def indice_do_aniversario(ano: int, mes: int) -> Decimal:
    p = periodo_ans(ano, mes)
    if p not in INDICES_ANS:
        raise IndiceAusente(p)
    return INDICES_ANS[p]


class IndiceAusente(Exception):
    def __init__(self, periodo: int):
        self.periodo = periodo
        super().__init__(
            f"Sem índice ANS para o período maio/{periodo}–abril/{periodo+1}. "
            f"Preencha references/indices-ans.md a partir da fonte oficial da ANS "
            f"antes de calcular — não estimar."
        )


# --------------------------------------------------------------------------- #
# Modelo
# --------------------------------------------------------------------------- #

def d(valor) -> Decimal:
    """Aceita '1.234,56', '1234.56', float ou Decimal."""
    if isinstance(valor, Decimal):
        return valor
    if isinstance(valor, (int, float)):
        return Decimal(str(valor))
    t = str(valor).strip().replace("R$", "").strip()
    if "," in t:
        t = t.replace(".", "").replace(",", ".")
    return Decimal(t or "0")


def q(valor: Decimal) -> Decimal:
    """Arredonda para exibição. Só aqui — nunca no meio da cadeia."""
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _brl(v: Decimal) -> str:
    s = f"{q(v):,.2f}".replace(",", "·").replace(".", ",").replace("·", ".")
    return f"R$ {s}"


def _pct(v: Decimal) -> str:
    return f"{v*100:.2f}%".replace(".", ",")


@dataclass
class Competencia:
    ano: int
    mes: int
    valor_pago: Decimal
    tipo_reajuste: str = INDEFINIDO      # ANUAL | FAIXA_ETARIA | "" (não declarado)

    @property
    def rotulo(self) -> str:
        nomes = ["", "janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho",
                 "agosto", "setembro", "outubro", "novembro", "dezembro"]
        return f"{nomes[self.mes]}/{self.ano}"

    @property
    def chave(self) -> tuple[int, int]:
        return (self.ano, self.mes)


@dataclass
class Linha:
    competencia: Competencia
    reajuste_aplicado: Decimal          # o que a operadora cobrou nesta competência
    reajuste_devido: Decimal            # o que se aplicou ao devido nesta competência
    valor_devido: Decimal               # precisão cheia
    diferenca: Decimal                  # precisão cheia


@dataclass
class Pendencia:
    """Reajuste fora do mês de aniversário, sem tipo declarado. Pode ser faixa etária
    legítima (entra no devido) ou aumento sem previsão (é o que se impugna)."""
    competencia: str
    percentual: Decimal
    pergunta: str


@dataclass
class Resultado:
    linhas: list[Linha] = field(default_factory=list)
    pendencias: list[Pendencia] = field(default_factory=list)
    bloqueios: list[str] = field(default_factory=list)
    mes_aniversario: int = 0
    janela_restituicao: tuple[str, str] | None = None

    # ---- resumo ----
    @property
    def valor_pago_atual(self) -> Decimal:
        return self.linhas[-1].competencia.valor_pago if self.linhas else Decimal(0)

    @property
    def valor_devido_atual(self) -> Decimal:
        return self.linhas[-1].valor_devido if self.linhas else Decimal(0)

    @property
    def diferenca_mensal(self) -> Decimal:
        return self.valor_pago_atual - self.valor_devido_atual

    @property
    def total_pago(self) -> Decimal:
        return sum((l.competencia.valor_pago for l in self.linhas), Decimal(0))

    @property
    def total_devido(self) -> Decimal:
        return sum((l.valor_devido for l in self.linhas), Decimal(0))

    @property
    def total_diferenca(self) -> Decimal:
        return sum((l.diferenca for l in self.linhas), Decimal(0))

    def restituicao(self, meses: int = MESES_RESTITUICAO,
                    ate: tuple[int, int] | None = None) -> Decimal:
        """Prescrição trienal (Tema 610/STJ).

        Dois parâmetros porque a resposta muda de valor conforme a convenção, e a
        convenção do escritório ainda não está fechada (pergunta A7):

        - `ate` é o marco final (ano, mês). Sem ele, a última competência da série.
          Numa planilha real do escritório o marco estava **dois meses atrás** da
          última competência — provavelmente congelado na data em que se calculou —
          e a peça saiu com a restituição desatualizada.
        - `meses` é o tamanho da janela. 36 é a leitura direta de "últimos 3 anos";
          contar do mesmo mês três anos antes **incluindo as duas pontas** dá 37
          competências, e é o que aquela planilha fazia. A diferença entre as duas
          convenções, no caso real, passou de mil reais no pedido.
        """
        janela = self._janela(meses, ate)
        if janela:
            self.janela_restituicao = (janela[0].competencia.rotulo,
                                       janela[-1].competencia.rotulo)
        return sum((l.diferenca for l in janela), Decimal(0))

    def _janela(self, meses: int, ate: tuple[int, int] | None) -> list["Linha"]:
        linhas = self.linhas
        if ate is not None:
            linhas = [l for l in linhas if l.competencia.chave <= ate]
        return linhas[-meses:]

    def conferir(self) -> list[str]:
        """Autoconferência dos totais. Existe porque a planilha real do escritório
        reprova aqui: pago − devido não fecha com o total da coluna diferença."""
        erros = []
        if q(self.total_pago - self.total_devido) != q(self.total_diferenca):
            erros.append(
                f"total pago − total devido = {q(self.total_pago - self.total_devido)} "
                f"≠ total da coluna diferença = {q(self.total_diferenca)}")
        # não recalcula a restituição: conferir() não pode sobrescrever a janela que
        # o chamador escolheu — era assim que o alerta de marco congelado se perdia.
        padrao = sum((l.diferenca for l in self._janela(MESES_RESTITUICAO, None)),
                     Decimal(0))
        if padrao > self.total_diferenca:
            erros.append("restituição de 3 anos maior que a diferença total da série")
        ultima = self.linhas[-1].competencia.rotulo if self.linhas else ""
        if self.janela_restituicao and self.janela_restituicao[1] != ultima:
            erros.append(
                f"a janela da restituição termina em {self.janela_restituicao[1]} mas a "
                f"série vai até {ultima} — marco congelado? (pergunta A7)")
        return erros

    @property
    def bloqueado(self) -> bool:
        return bool(self.bloqueios or self.pendencias)


# --------------------------------------------------------------------------- #
# Cálculo
# --------------------------------------------------------------------------- #

def calcular(competencias: list[Competencia], mes_aniversario: int,
             faixa_etaria_aceita: dict[tuple[int, int], Decimal] | None = None,
             ) -> Resultado:
    """Monta a tabela de reajuste devido.

    `faixa_etaria_aceita` traz as decisões humanas: chave (ano, mês), valor = percentual
    a incorporar ao devido. Competência ausente do dicionário e com reajuste fora do
    aniversário vira pendência — o cálculo não segue sozinho.
    """
    aceitas = faixa_etaria_aceita or {}
    res = Resultado(mes_aniversario=mes_aniversario)

    ordenadas = sorted(competencias, key=lambda c: (c.ano, c.mes))
    reais = [c for c in ordenadas if c.valor_pago > Decimal("0.01")]
    if not reais:
        res.bloqueios.append("nenhuma competência com valor real — nada a calcular")
        return res

    devido = reais[0].valor_pago          # base: primeira competência com valor real
    pago_anterior: Decimal | None = None

    for c in reais:
        aplicado = Decimal(0)
        if pago_anterior and pago_anterior > 0:
            aplicado = (c.valor_pago / pago_anterior) - 1

        devido_pct = Decimal(0)
        primeira = c is reais[0]
        aniversario = (c.mes == mes_aniversario) and not primeira

        if aniversario:
            try:
                devido_pct = indice_do_aniversario(c.ano, c.mes)
            except IndiceAusente as erro:
                res.bloqueios.append(str(erro))
                return res
            devido = devido * (1 + devido_pct)

        elif not primeira and aplicado > Decimal("0.005"):
            # Reajuste fora do aniversário: faixa etária legítima entra no devido,
            # aumento sem previsão não entra — e essa distinção é jurídica.
            if c.chave in aceitas:
                extra = aceitas[c.chave]
                devido = devido * (1 + extra)
                devido_pct = extra
            elif c.tipo_reajuste != FAIXA_ETARIA:
                res.pendencias.append(Pendencia(
                    competencia=c.rotulo,
                    percentual=aplicado,
                    pergunta=(f"Em {c.rotulo} a mensalidade subiu {_pct(aplicado)} "
                              f"fora do mês de aniversário. É reajuste por faixa etária "
                              f"previsto em contrato (entra no valor devido) ou aumento "
                              f"sem previsão (fica de fora e é o que se impugna)?"),
                ))

        res.linhas.append(Linha(
            competencia=c,
            reajuste_aplicado=aplicado,
            reajuste_devido=devido_pct,
            valor_devido=devido,
            diferenca=c.valor_pago - devido,
        ))
        pago_anterior = c.valor_pago

    return res


# --------------------------------------------------------------------------- #
# Saída
# --------------------------------------------------------------------------- #

CABECALHOS = ["Mês/Ano", "Valor Pago", "Reajuste Aplicado", "Tipo de Reajuste",
              "Reajuste Devido", "Valor Devido", "Diferença"]


def tabela(res: Resultado) -> list[list[str]]:
    """Linhas prontas para virar `w:tbl` no gerador — nunca imagem."""
    linhas = [CABECALHOS]
    for l in res.linhas:
        tipo = l.competencia.tipo_reajuste
        if not tipo and l.reajuste_devido != 0:
            tipo = ANUAL
        linhas.append([
            l.competencia.rotulo,
            _brl(l.competencia.valor_pago),
            _pct(l.reajuste_aplicado),
            "Anual" if tipo == ANUAL else ("Faixa etária" if tipo == FAIXA_ETARIA else ""),
            _pct(l.reajuste_devido),
            _brl(l.valor_devido),
            _brl(l.diferenca),
        ])
    linhas.append(["Total", _brl(res.total_pago), "", "", "",
                   _brl(res.total_devido), _brl(res.total_diferenca)])
    return linhas


def resumo(res: Resultado) -> dict[str, str]:
    restituicao = res.restituicao()
    janela = res.janela_restituicao
    return {
        "Valor Pago (Atual)": _brl(res.valor_pago_atual),
        "Valor Devido": _brl(res.valor_devido_atual),
        "Diferença (Mensal)": _brl(res.diferenca_mensal),
        "Restituição (últimos 3 anos)": _brl(restituicao),
        "Janela da restituição": f"{janela[0]} a {janela[1]}" if janela else "—",
    }
