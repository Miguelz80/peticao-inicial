"""Orquestrador — costura os cinco módulos numa sequência com porteiros humanos.

A colega que opera trabalha por chat, respondendo uma coisa de cada vez. Então isto
não é um pipeline que roda do começo ao fim: é uma máquina de estados **retomável**.
Cada chamada avança até o próximo ponto que exige decisão humana, devolve o que
precisa ser respondido, e para. A resposta volta no mesmo `Caso` e a chamada seguinte
continua de onde parou.

As fases, e o que trava cada uma:

    TRIAGEM      → lê os documentos e classifica        trava: gate do Classificador
    CONFIRMACAO  → apresenta o Espelho                  trava: confirmação da tese (G8)
    CALCULO      → monta a tabela de reajuste devido    trava: faixa etária, índice ausente
    REDACAO      → escolhe capítulos e preenche         trava: campo sem valor, capítulo sem texto
    GERACAO      → escreve o DOCX
    CONFERENCIA  → compara com a origem                 trava: qualquer achado que BLOQUEIA
    CONCLUIDO    → entrega

Nenhuma fase pula porteiro. Avançar sem resposta seria transformar as travas que cada
módulo tem em decoração.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from decimal import Decimal

import calcular_reajuste as calc
import classificar as cls
import conferir as conf
import extrair_evidencias as extr
import gerar_peticao as ger
import ler_tabela as tab
import roteiro as rot


TRIAGEM, CONFIRMACAO, CALCULO = "TRIAGEM", "CONFIRMACAO", "CALCULO"
REDACAO, GERACAO, CONFERENCIA, CONCLUIDO = "REDACAO", "GERACAO", "CONFERENCIA", "CONCLUIDO"

PRECISA_CALCULO = {"FATURAMENTO_BRUTO", "DEMONSTRATIVO_OPERADORA"}


@dataclass
class Caso:
    """Tudo que a operadora já forneceu. Cresce a cada resposta; nada se perde entre
    as chamadas, e é ele que torna o fluxo retomável."""
    arquivos: list[str] = field(default_factory=list)
    fatos: dict[str, cls.Fato] = field(default_factory=dict)
    dados: dict[str, str] = field(default_factory=dict)
    mes_aniversario: int | None = None
    faixa_etaria_aceita: dict[tuple[int, int], Decimal] = field(default_factory=dict)
    tese_confirmada: str = ""          # a operadora confirmou o Espelho
    modelo_docx: str = ""
    saida_docx: str = ""
    cliente: str = ""
    competencias: list[calc.Competencia] = field(default_factory=list)
    respostas: dict[str, str] = field(default_factory=dict)
    """Gate respondido, por id da pergunta (G4, G5-ausente, DOC-arquivo.pdf...).

    Sem este canal o fluxo trava: alguns gates do Classificador não se resolvem
    preenchendo um fato — a resposta é a própria operadora dizendo o que fazer.
    """

    def fatos_simples(self) -> dict[str, str]:
        """Os fatos no formato que o Roteiro entende."""
        return {k: v.valor for k, v in self.fatos.items()}


@dataclass
class Etapa:
    fase: str
    perguntas: list[str] = field(default_factory=list)
    avisos: list[str] = field(default_factory=list)
    espelho: str = ""
    dossie: dict | None = None
    resultado: calc.Resultado | None = None
    conferencia: conf.Conferencia | None = None
    docx: str = ""

    @property
    def travado(self) -> bool:
        return bool(self.perguntas) and self.fase != CONCLUIDO

    @property
    def concluido(self) -> bool:
        return self.fase == CONCLUIDO


# --------------------------------------------------------------------------- #
# Fluxo
# --------------------------------------------------------------------------- #

def elaborar(caso: Caso) -> Etapa:
    """Avança até o próximo ponto de decisão humana e para."""

    # ---- TRIAGEM ---------------------------------------------------------- #
    extracao = extr.extrair(caso.arquivos) if caso.arquivos else extr.Extracao()
    documentos = extr.para_documentos(extracao)
    planilhas = [cls.Planilha(**p) for p in extracao.planilhas]

    # Planilha reconhecida vira série automaticamente. Sem isto o orquestrador pedia
    # as competências mês a mês mesmo tendo o arquivo em mãos.
    avisos_da_serie: list[str] = []
    if planilhas and not caso.competencias:
        for pl in planilhas:
            comps, avisos = tab.competencias_de(
                {"linhas": pl.linhas, "texto_solto": pl.texto_solto})
            if comps:
                caso.competencias = comps
                avisos_da_serie = avisos
                break

    # Série informada direto pela operadora vale como base de cálculo: o Eixo A não
    # pode ficar em AUSENTE só porque o dado não veio por arquivo.
    if caso.competencias and not planilhas:
        planilhas = [cls.Planilha(
            arquivo="série informada pela operadora",
            cabecalhos=["Mês/Ano", "Valor Pago"],
            linhas=[[c.rotulo, c.valor_pago] for c in caso.competencias])]

    dossie = cls.classificar(documentos, planilhas, caso.fatos)
    etapa = Etapa(fase=TRIAGEM, dossie=dossie, avisos=list(avisos_da_serie))

    pendentes = [p for p in dossie["perguntas"] if p["id"] not in caso.respostas]
    bloqueantes = [p for p in pendentes if p["bloqueante"]]
    if bloqueantes:
        etapa.perguntas = [_formatar(p) for p in pendentes]
        etapa.espelho = cls.espelho(dossie, caso.cliente)
        return etapa

    # ---- CONFIRMACAO (G8: sempre) ----------------------------------------- #
    tese = dossie["eixo_b"]["tese"]
    if caso.tese_confirmada != tese:
        etapa.fase = CONFIRMACAO
        etapa.espelho = cls.espelho(dossie, caso.cliente)
        etapa.perguntas = [
            f"Confirma a tese {cls.ROTULO_TESE.get(tese, tese)} para eu seguir? "
            f"Responda com a tese confirmada."]
        return etapa

    # ---- CALCULO ---------------------------------------------------------- #
    etapa.fase = CALCULO
    regime = dossie["eixo_a"]["regime"]
    resultado = None

    # Calcula sempre que houver série, inclusive em CALCULO_PRONTO: recontar é a
    # única verificação independente da planilha que o cliente mandou.
    if caso.competencias:
        if caso.mes_aniversario is None:
            etapa.perguntas = ["Em que mês cai o aniversário do contrato? "
                               "É ele que define qual índice ANS se aplica a cada ano."]
            return etapa
        if not caso.competencias:
            etapa.perguntas = ["Preciso das competências e valores pagos mês a mês "
                               "para montar a tabela de reajuste devido."]
            return etapa

        resultado = calc.calcular(caso.competencias, caso.mes_aniversario,
                                  caso.faixa_etaria_aceita)
        etapa.resultado = resultado
        if resultado.bloqueios:
            etapa.perguntas = list(resultado.bloqueios)
            return etapa
        if resultado.pendencias:
            etapa.perguntas = [p.pergunta for p in resultado.pendencias]
            return etapa
        resultado.restituicao()
        if regime == "CALCULO_PRONTO":
            for pl in planilhas:
                etapa.avisos += tab.conferir_importado(
                    {"linhas": pl.linhas, "texto_solto": pl.texto_solto}, resultado)
        caso.dados.setdefault("valor_pago_atual", calc._brl(resultado.valor_pago_atual))
        caso.dados.setdefault("valor_devido_atual",
                              calc._brl(resultado.valor_devido_atual))
        caso.dados.setdefault("diferenca_mensal", calc._brl(resultado.diferenca_mensal))
        caso.dados.setdefault("restituicao", calc._brl(resultado.restituicao()))

    # ---- REDACAO ---------------------------------------------------------- #
    etapa.fase = REDACAO
    try:
        roteiro = rot.montar_peca(tese, caso.fatos_simples(), caso.dados,
                                  resultado_calculo=resultado)
    except rot.CampoAusente as erro:
        etapa.perguntas = [str(erro)]
        return etapa

    etapa.avisos = list(avisos_da_serie) + list(roteiro.revisoes)
    if roteiro.perguntas:
        etapa.perguntas = list(roteiro.perguntas)
        return etapa
    if roteiro.pendencias:
        etapa.perguntas = [f"Capítulo sem texto do escritório — {p}"
                           for p in roteiro.pendencias]
        return etapa

    # ---- GERACAO ---------------------------------------------------------- #
    etapa.fase = GERACAO
    if not caso.modelo_docx or not os.path.exists(caso.modelo_docx):
        etapa.perguntas = ["Preciso do arquivo DOCX do escritório que serve de modelo — "
                           "é dele que saem o timbre, as margens e o rodapé."]
        return etapa

    saida = caso.saida_docx or os.path.join(
        os.path.dirname(caso.modelo_docx) or ".", "peticao-gerada.docx")
    ger.montar(caso.modelo_docx, roteiro.peca, saida)
    etapa.docx = saida

    # ---- CONFERENCIA ------------------------------------------------------ #
    etapa.fase = CONFERENCIA
    texto = _texto_da_peca(roteiro.peca)
    conferencia = conf.conferir(
        resultado or calc.Resultado(), texto_peca=texto, caminho_docx=saida,
        declarados={k: caso.dados[k] for k in
                    ("restituicao", "diferenca_mensal", "valor_pago_atual",
                     "valor_devido_atual") if k in caso.dados})
    etapa.conferencia = conferencia
    etapa.espelho = espelho_completo(dossie, resultado, roteiro, conferencia,
                                     caso.cliente)
    if not conferencia.liberado:
        etapa.perguntas = [str(a) for a in conferencia.bloqueios()]
        return etapa

    etapa.fase = CONCLUIDO
    return etapa


def _formatar(pergunta: dict) -> str:
    linhas = [pergunta["texto"]]
    for ev in pergunta.get("evidencias", []):
        linhas.append(f"    encontrei: {ev}")
    for i, opcao in enumerate(pergunta["opcoes"], 1):
        linhas.append(f"    {i}) {opcao}")
    return "\n".join(linhas)


def _texto_da_peca(peca: ger.Peca) -> str:
    return " ".join(b.texto for b in peca.blocos if hasattr(b, "texto"))


# --------------------------------------------------------------------------- #
# Espelho completo
# --------------------------------------------------------------------------- #

def espelho_completo(dossie: dict, resultado, roteiro, conferencia,
                     cliente: str = "") -> str:
    """O Espelho da spec, agora com os números e a procedência do texto.

    Existia para a operadora conferir a classificação; sem o cálculo e sem o aviso de
    que a tese tem texto ainda não lido por advogado, ela confirmaria no escuro
    justamente o que mais importa.
    """
    L = [cls.espelho(dossie, cliente, pedir_confirmacao=False), ""]

    if resultado is not None and resultado.linhas:
        L.append("Cálculo")
        for chave, valor in calc.resumo(resultado).items():
            L.append(f"  {chave:32s} {valor}")
        L.append(f"  {'Competências apuradas':32s} {len(resultado.linhas)}")
        erros = resultado.conferir()
        L.append(f"  {'Conferência dos totais':32s} "
                 f"{'tudo fecha' if not erros else '; '.join(erros)}")
        L.append("")

    if roteiro is not None:
        L.append("Peça")
        titulos = [f"{b.numeral} {b.texto}" for b in roteiro.peca.blocos
                   if isinstance(b, ger.Titulo)]
        L.append(f"  {len(titulos)} capítulos")
        for titulo in titulos:
            L.append(f"    {titulo}")
        if roteiro.revisoes:
            L.append("")
            L.append("  ATENÇÃO — texto que ainda não foi lido por advogado:")
            for aviso in roteiro.revisoes:
                L.append(f"    · {aviso}")
        L.append("")

    if conferencia is not None:
        L.append(conferencia.relatorio())

    return "\n".join(L)
