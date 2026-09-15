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
import sys
import zipfile
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
            # O aviso vale mesmo sem competência: é ele que diz POR QUE a leitura
            # falhou (coluna de valor ilegível, digitalização torta). Descartá-lo
            # deixava a operadora sem saber o que houve com o arquivo que mandou.
            avisos_da_serie += [f"{pl.arquivo}: {a}" for a in avisos]
            if comps:
                caso.competencias = comps
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
    # Regime que exige cálculo sem série legível trava aqui. Antes caía na redação e
    # a operadora acabava digitando restituição e diferença à mão — justamente os
    # números que esta skill existe para calcular e conferir.
    if regime in PRECISA_CALCULO and not caso.competencias:
        etapa.perguntas = [
            "Não consegui ler competência e valor pago do demonstrativo — sem a "
            "série não monto a tabela de reajuste devido nem a restituição. "
            "Informe os meses e valores no campo “competencias” do arquivo do caso "
            '(ex.: [{"competencia": "2024-01", "valor": "2.238,77"}]) ou mande o '
            "demonstrativo em versão legível (planilha ou PDF com texto)."]
        return etapa

    if caso.competencias:
        if caso.mes_aniversario is None:
            etapa.perguntas = ["Em que mês cai o aniversário do contrato? "
                               "É ele que define qual índice ANS se aplica a cada ano."]
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
        etapa.avisos += resultado.avisos   # série truncada por índice ANS ausente
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
    except rot.TeseSemCatalogo as erro:
        etapa.perguntas = [f"Problema no catálogo de teses: {erro}"]
        return etapa

    etapa.avisos += list(roteiro.revisoes)   # += : as divergências da planilha já
                                             # estavam aqui e eram sobrescritas
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
    try:
        ger.montar(caso.modelo_docx, roteiro.peca, saida)
    except (ger.ModeloInvalido, zipfile.BadZipFile, OSError) as erro:
        # Quem opera é a colega do processual, por chat. Traceback não é resposta.
        etapa.perguntas = [f"Não consegui usar o modelo {os.path.basename(caso.modelo_docx)}: "
                           f"{erro}"]
        return etapa
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


# --------------------------------------------------------------------------- #
# Interface por arquivo JSON
# --------------------------------------------------------------------------- #
#
# Quem dirige a skill no chat não constrói objeto Python: escreve um JSON de tipos
# simples e roda um comando. Tudo aqui é string — fato, decisão de faixa etária,
# resposta de gate — porque é o que atravessa uma conversa sem se perder.

import json  # noqa: E402

# Campo em branco é campo por preencher. O menu de opções vive em "_ajuda", que a
# skill ignora — antes as opções ficavam no próprio valor e a primeira delas era lida
# como resposta.
EXEMPLO = {
    "cliente": "",
    "arquivos": [],
    "modelo_docx": "",
    "saida_docx": "",
    "mes_aniversario": None,
    "tese_confirmada": "",
    "fatos": {"F1": "", "F2": "", "F6": "", "F7": "", "F9": "", "F10": ""},
    "dados": {"plano": "", "inicio_contrato": "", "comarca": "", "idade": "",
              "competencia_atual": "", "maior_reajuste": "", "valor_da_causa": "",
              "narrativa_hipossuficiencia": ""},
    "faixa_etaria_aceita": {},
    "respostas": {},
    "_ajuda": {
        "arquivos": "caminhos dos documentos do caso",
        "modelo_docx": "DOCX do escritório de onde vêm timbre, margens e rodapé",
        "mes_aniversario": "número do mês, 1 a 12 — define o índice ANS de cada ano",
        "F1": "AUTOGESTAO ou COMERCIAL",
        "F2": "PJ, PF_VIA_ASSOCIACAO ou PF_DIRETO",
        "F6": "ATIVO ou CANCELADO",
        "F7": "SIM ou NAO — houve reajuste por faixa etária",
        "F9": "idade da parte autora, em anos",
        "F10": "SIM ou NAO — houve ação anterior desistida",
        "faixa_etaria_aceita": "ANO-MÊS para o PERCENTUAL que entra no devido, "
                               "ex.: {\"2021-01\": \"10,50\"} = 10,5%. Use \"0\" "
                               "para o reajuste que NÃO entra (é o que se impugna)",
        "respostas": "gate respondido, pelo id da pergunta",
    },
}

CAMPOS_CONHECIDOS = set(EXEMPLO) | {"competencias"}


class CasoInvalido(Exception):
    pass


def caso_de_json(bruto: dict) -> Caso:
    bruto = {k: v for k, v in bruto.items() if k != "_ajuda"}
    desconhecidos = set(bruto) - CAMPOS_CONHECIDOS
    if desconhecidos:
        raise CasoInvalido(
            f"campos que não reconheço no arquivo: {', '.join(sorted(desconhecidos))}. "
            f"Os aceitos são: {', '.join(sorted(CAMPOS_CONHECIDOS))}")

    caso = Caso(
        cliente=bruto.get("cliente", ""),
        arquivos=list(bruto.get("arquivos") or []),
        modelo_docx=bruto.get("modelo_docx", ""),
        saida_docx=bruto.get("saida_docx", ""),
        mes_aniversario=bruto.get("mes_aniversario"),
        tese_confirmada=bruto.get("tese_confirmada", ""),
        dados={k: str(v) for k, v in (bruto.get("dados") or {}).items() if v != ""},
        respostas={k: str(v) for k, v in (bruto.get("respostas") or {}).items()},
    )

    for chave, valor in (bruto.get("fatos") or {}).items():
        if valor in (None, ""):
            continue
        if isinstance(valor, dict):
            caso.fatos[chave] = cls.Fato(**valor)
        else:
            # informado pela operadora: alta confiança, origem declarada
            caso.fatos[chave] = cls.Fato(valor=str(valor), fonte="informado pela operadora",
                                         confianca=0.95, origem="informado")

    for item in (bruto.get("competencias") or []):
        # série informada à mão, quando não há arquivo. O campo era aceito na
        # validação e nunca lido: não havia como fornecer as competências sem arquivo.
        try:
            ano, mes = (int(x) for x in str(item["competencia"]).split("-"))
        except (KeyError, ValueError):
            raise CasoInvalido(
                'cada competência precisa de "competencia" no formato ANO-MÊS e '
                '"valor", ex.: {"competencia": "2024-01", "valor": "1.234,56"}')
        caso.competencias.append(calc.Competencia(
            ano=ano, mes=mes, valor_pago=calc.d(item.get("valor", "0")),
            tipo_reajuste=item.get("tipo", "")))

    for chave, valor in (bruto.get("faixa_etaria_aceita") or {}).items():
        try:
            ano, mes = (int(x) for x in str(chave).split("-"))
        except ValueError:
            raise CasoInvalido(
                f"chave de faixa etária inválida: “{chave}”. Use ANO-MÊS, como 2021-01.")
        # O arquivo fala em percentual ("10,50"); o cálculo trabalha em fração.
        # Sem esta conversão, 10,5% entrava como 1050% e multiplicava a mensalidade
        # por onze.
        caso.faixa_etaria_aceita[(ano, mes)] = calc.d(valor) / 100

    return caso


def json_do_caso(caso: Caso) -> dict:
    return {
        "cliente": caso.cliente,
        "arquivos": caso.arquivos,
        "modelo_docx": caso.modelo_docx,
        "saida_docx": caso.saida_docx,
        "mes_aniversario": caso.mes_aniversario,
        "tese_confirmada": caso.tese_confirmada,
        "fatos": {k: v.valor for k, v in sorted(caso.fatos.items())},
        "dados": dict(sorted(caso.dados.items())),
        "faixa_etaria_aceita": {f"{a}-{m:02d}": _pct_texto(v) for (a, m), v
                                in sorted(caso.faixa_etaria_aceita.items())},
        "respostas": dict(sorted(caso.respostas.items())),
    }


def _pct_texto(fracao) -> str:
    """De volta a percentual, como entrou."""
    return f"{fracao * 100:.2f}".replace(".", ",")


def relatorio(etapa: Etapa) -> str:
    L = [f"FASE: {etapa.fase}", ""]
    if etapa.espelho:
        L += [etapa.espelho, ""]
    if etapa.avisos:
        L.append("AVISOS — não travam, mas precisam de olhar humano:")
        L += [f"  · {a}" for a in etapa.avisos]
        L.append("")
    if etapa.perguntas:
        L.append("PRECISO QUE VOCÊ RESPONDA:")
        for p in etapa.perguntas:
            L.append("  " + p.replace("\n", "\n  "))
        L.append("")
        L.append("Responda editando o arquivo do caso e rode de novo.")
    if etapa.concluido:
        L.append(f"PETIÇÃO GERADA: {etapa.docx}")
        L.append("Revise antes de protocolar — a skill erra, e o documento é editável.")
    return "\n".join(L)


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[1] in ("-h", "--ajuda"):
        print("uso: python3 elaborar.py <caso.json>\n"
              "     python3 elaborar.py --exemplo > caso.json")
        return 0
    if argv[1] == "--exemplo":
        print(json.dumps(EXEMPLO, ensure_ascii=False, indent=2))
        return 0

    caminho = argv[1]
    if not os.path.exists(caminho):
        print(f"não achei {caminho}. Comece com: "
              f"python3 elaborar.py --exemplo > {caminho}")
        return 2
    with open(caminho, encoding="utf-8") as fh:
        bruto = json.load(fh)

    try:
        caso = caso_de_json(bruto)
    except CasoInvalido as erro:
        print(f"ERRO no arquivo do caso: {erro}")
        return 2

    etapa = elaborar(caso)
    print(relatorio(etapa))

    # devolve o caso enriquecido, preservando o que o arquivo já trazia: a ajuda e os
    # campos em branco são o formulário que a operadora usa para responder, e antes
    # sumiam na primeira rodada.
    atualizado = dict(bruto)
    atualizado.update(json_do_caso(caso))
    for chave in ("fatos", "dados"):
        combinado = dict(bruto.get(chave) or {})
        combinado.update(atualizado.get(chave) or {})
        atualizado[chave] = combinado
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump(atualizado, fh, ensure_ascii=False, indent=2)
    return 0 if etapa.concluido else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
