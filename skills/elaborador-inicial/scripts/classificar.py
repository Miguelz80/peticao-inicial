"""Classificador do elaborador-inicial — Eixo A (regime de cálculo) e Eixo B (tese).

Trabalha sobre evidências já extraídas (ver extrair_evidencias.py), nunca sobre
arquivos. Isso mantém a decisão testável sem depender de leitura de PDF/XLSX.

Regra que atravessa o módulo inteiro: na dúvida, não decide — devolve pergunta.
Especificação: docs/02-classificador-spec.md
"""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass, field, asdict
from typing import Any


# --------------------------------------------------------------------------- #
# Normalização
# --------------------------------------------------------------------------- #

def normalizar(texto: str) -> str:
    """minúsculas, sem acento, espaços colapsados. Base de toda comparação."""
    if texto is None:
        return ""
    sem_acento = "".join(
        c for c in unicodedata.normalize("NFD", str(texto))
        if unicodedata.category(c) != "Mn"
    )
    return " ".join(sem_acento.lower().split())


# --------------------------------------------------------------------------- #
# Eixo A — regime de cálculo
# --------------------------------------------------------------------------- #

# Comparação é sempre sobre o cabeçalho normalizado INTEIRO, nunca por substring:
# "reajuste aplicado" (o que a operadora cobrou) e "reajuste devido" (o que seria
# legal) diferem por uma palavra, e confundi-los inverte o regime de cálculo.
COLS_DEVIDO = {
    "reajuste devido", "valor devido", "diferenca", "diferenca mensal",
    "valor correto", "valor devido atual",
}
COLS_BASE = {
    "mes/ano", "mes ano", "competencia", "valor pago", "valor",
    "valor total", "referencia", "mensalidade",
}
COLS_RUIDO = {"reajuste aplicado", "tipo de reajuste", "percentual aplicado"}

# Demonstrativo emitido pela operadora: série de competências, sem coluna de devido.
MARCADORES_DEMONSTRATIVO = {
    "demonstrativo de pagamento", "data baixa", "tipo lancamento",
    "demonstrativo de faturas", "vencimento",
}

PREENCHIMENTO_MINIMO = 0.6


@dataclass
class Planilha:
    """Uma tabela já extraída: cabeçalhos e linhas como listas de strings."""
    arquivo: str
    cabecalhos: list[str]
    linhas: list[list[Any]] = field(default_factory=list)
    texto_solto: str = ""          # para demonstrativos sem grade de colunas


def _e_numero(valor: Any) -> bool:
    if valor is None:
        return False
    if isinstance(valor, (int, float)):
        return True
    t = str(valor).strip().replace(".", "").replace(",", ".").replace("R$", "").strip()
    if not t:
        return False
    try:
        float(t)
        return True
    except ValueError:
        return False


def classificar_planilha(p: Planilha) -> dict:
    """Decide o regime de uma única planilha. Nunca levanta exceção por cabeçalho
    desconhecido — cabeçalho que não casa vira AMBIGUO, que vira pergunta."""
    normalizados = [normalizar(c) for c in p.cabecalhos]
    devido = [c for c in normalizados if c in COLS_DEVIDO]
    base = [c for c in normalizados if c in COLS_BASE]
    ruido = [c for c in normalizados if c in COLS_RUIDO]

    evidencias: list[str] = []
    if devido:
        evidencias.append(f"colunas de valor devido: {', '.join(sorted(devido))}")
    if base:
        evidencias.append(f"colunas de base: {', '.join(sorted(base))}")
    if ruido:
        evidencias.append(
            f"colunas de reajuste aplicado (não é valor devido): {', '.join(sorted(ruido))}"
        )

    preenchimento = _preenchimento_devido(p, normalizados)

    if len(devido) >= 2 and preenchimento >= PREENCHIMENTO_MINIMO:
        evidencias.append(f"colunas de devido preenchidas em {preenchimento:.0%} das linhas")
        return _regime("CALCULO_PRONTO", 0.9, evidencias, p.arquivo)

    if not devido and len(base) >= 2:
        return _regime("FATURAMENTO_BRUTO", 0.85, evidencias, p.arquivo)

    if devido and preenchimento < PREENCHIMENTO_MINIMO:
        evidencias.append(
            f"colunas de devido presentes mas preenchidas em apenas {preenchimento:.0%} das linhas"
        )
        return _regime("AMBIGUO", 0.4, evidencias, p.arquivo)

    if len(devido) == 1:
        evidencias.append("apenas uma coluna de valor devido — cálculo possivelmente parcial")
        return _regime("AMBIGUO", 0.4, evidencias, p.arquivo)

    texto = normalizar(p.texto_solto + " " + " ".join(p.cabecalhos))
    achados = [m for m in MARCADORES_DEMONSTRATIVO if m in texto]
    if achados:
        evidencias.append(f"marcadores de demonstrativo de operadora: {', '.join(sorted(achados))}")
        return _regime("DEMONSTRATIVO_OPERADORA", 0.75, evidencias, p.arquivo)

    evidencias.append(f"cabeçalhos não reconhecidos: {', '.join(p.cabecalhos) or '(nenhum)'}")
    return _regime("AMBIGUO", 0.2, evidencias, p.arquivo)


def _preenchimento_devido(p: Planilha, normalizados: list[str]) -> float:
    indices = [i for i, c in enumerate(normalizados) if c in COLS_DEVIDO]
    if not indices or not p.linhas:
        return 0.0
    cheias = 0
    for linha in p.linhas:
        if any(i < len(linha) and _e_numero(linha[i]) for i in indices):
            cheias += 1
    return cheias / len(p.linhas)


def _regime(regime: str, confianca: float, evidencias: list[str], arquivo: str) -> dict:
    return {
        "regime": regime,
        "confianca": confianca,
        "evidencias": evidencias,
        "planilha_base": arquivo,
    }


def decidir_eixo_a(planilhas: list[Planilha]) -> dict:
    """Consolida o regime quando há mais de uma planilha.

    Vereditos divergentes NÃO são resolvidos por heurística (a maior, a mais
    recente): viram pergunta. Escolher a base de cálculo errada corrompe tudo
    que vem depois.
    """
    if not planilhas:
        return _regime("AUSENTE", 0.0, ["nenhuma planilha ou demonstrativo recebido"], "")

    vereditos = [classificar_planilha(p) for p in planilhas]
    uteis = [v for v in vereditos if v["regime"] not in ("AMBIGUO", "AUSENTE")]
    regimes = {v["regime"] for v in uteis}

    if len(regimes) > 1:
        detalhe = "; ".join(f"{v['planilha_base']} → {v['regime']}" for v in uteis)
        return _regime("AMBIGUO", 0.3,
                       [f"planilhas com vereditos divergentes: {detalhe}"], "")

    if len(uteis) == 1:
        return uteis[0]

    if len(uteis) > 1:
        vencedor = max(uteis, key=lambda v: v["confianca"])
        vencedor = dict(vencedor)
        vencedor["evidencias"] = list(vencedor["evidencias"]) + [
            f"{len(uteis)} planilhas concordam no regime {vencedor['regime']}"
        ]
        return vencedor

    pior = max(vereditos, key=lambda v: v["confianca"])
    return pior


# --------------------------------------------------------------------------- #
# Eixo B — tese
# --------------------------------------------------------------------------- #

SIM, NAO, DESCONHECIDO = "SIM", "NAO", "DESCONHECIDO"


@dataclass
class Fato:
    """Ausência de sinal é DESCONHECIDO, jamais NAO. Silêncio não prova nada."""
    valor: str = DESCONHECIDO
    fonte: str = ""
    citacao: str = ""
    confianca: float = 0.0
    origem: str = "texto_nativo"   # texto_nativo | ocr | imagem | informado
    conflitos: list[str] = field(default_factory=list)   # citações que contradizem

    def confiavel(self, minimo: float = 0.7) -> bool:
        return self.valor != DESCONHECIDO and self.confianca >= minimo


def _f(fatos: dict[str, Fato], chave: str) -> Fato:
    return fatos.get(chave) or Fato()


def decidir_eixo_b(fatos: dict[str, Fato]) -> dict:
    """Árvore de discriminantes duros. A narrativa alimenta fatos; nunca sobrepõe."""
    descartadas: list[dict] = []
    evid: list[str] = []

    f1 = _f(fatos, "F1")   # natureza da operadora
    f2 = _f(fatos, "F2")   # quem contratou
    f3 = _f(fatos, "F3")   # PJ tem atividade econômica real
    f4 = _f(fatos, "F4")   # beneficiários são o núcleo familiar
    f5 = _f(fatos, "F5")   # há vínculo empregatício

    if f1.valor == "AUTOGESTAO":
        evid.append(f"operadora de autogestão ({f1.fonte})")
        descartadas.append({
            "tese": "EMPRESARIAL_FAMILIAR",
            "porque": "operadora é autogestão — Súmula 608/STJ afasta o CDC e não há "
                      "coletivo empresarial interposto",
        })
        return _tese("CASSI_AUTOGESTAO", 0.95, evid, descartadas)

    if f1.valor == DESCONHECIDO:
        return _tese("INDEFINIDA", 0.0,
                     ["natureza da operadora não identificada"], descartadas,
                     bloqueio="G4")

    if f2.valor == "PJ":
        evid.append(f"contratante é pessoa jurídica ({f2.fonte})")
        if f3.valor == SIM:
            evid.append("a PJ tem atividade econômica real")
            return _tese("FORA_DO_PADRAO", 0.8, evid, descartadas, bloqueio="G6")
        if f3.valor == NAO and f4.valor == SIM and f5.valor == NAO:
            for rotulo, fato in (("sem atividade econômica real", f3),
                                 ("beneficiários são o núcleo familiar", f4),
                                 ("sem vínculo empregatício", f5)):
                evid.append(f"{rotulo}: “{fato.citacao}” ({fato.fonte})"
                            if fato.citacao else f"{rotulo} ({fato.fonte})")
            descartadas.append({"tese": "COLETIVO_POR_ADESAO",
                                "porque": "contratante é PJ, não PF via associação"})
            return _tese("EMPRESARIAL_FAMILIAR", 0.9, evid, descartadas)
        faltando = [n for n, f in (("F3", f3), ("F4", f4), ("F5", f5))
                    if f.valor == DESCONHECIDO]
        return _tese("INDEFINIDA", 0.3, evid, descartadas, bloqueio="G1",
                     faltando=faltando)

    if f2.valor == "PF_VIA_ASSOCIACAO":
        evid.append(f"pessoa física aderiu via associação/sindicato ({f2.fonte})")
        descartadas.append({"tese": "EMPRESARIAL_FAMILIAR",
                            "porque": "não há PJ contratante"})
        return _tese("COLETIVO_POR_ADESAO", 0.9, evid, descartadas)

    if f2.valor == "PF_DIRETO":
        evid.append(f"pessoa física contratou direto com a operadora ({f2.fonte})")
        return _tese("INDIVIDUAL_COMUM", 0.9, evid, descartadas)

    return _tese("INDEFINIDA", 0.0, ["não foi possível determinar quem contratou"],
                 descartadas, bloqueio="G3", faltando=["F2"])


def _tese(tese, confianca, evidencias, descartadas, bloqueio=None, faltando=None) -> dict:
    return {
        "tese": tese,
        "confianca": confianca,
        "evidencias": evidencias,
        "descartadas": descartadas,
        "bloqueio": bloqueio,
        "faltando": faltando or [],
    }


MODELOS = {
    "EMPRESARIAL_FAMILIAR": "PETIÇÃO INICIAL-MODELO APENAS RESTITUIÇÃO.docx",
    "COLETIVO_POR_ADESAO": "MODELO PETIÇÃO INICIAL COLETIVO POR ADESÃO.docx",
    "CASSI_AUTOGESTAO": "modelo-autogestao.docx",
    "INDIVIDUAL_COMUM": None,          # pendente — pergunta B2
}


# --------------------------------------------------------------------------- #
# Gate de segurança
# --------------------------------------------------------------------------- #

# Toda pergunta bloqueante oferece "Não sei / vou verificar". Se "não sei" tiver
# atrito, a operadora chuta para destravar — e o chute vira tese na peça.
NAO_SEI = "Não sei / vou verificar — pare aqui e não gere nada"

ROTULO_FATO = {
    "F2": "Quem assinou o contrato do plano?",
    "F3": "A empresa tem atividade econômica real hoje?",
    "F4": "Os beneficiários são só pessoas da mesma família?",
    "F5": "Algum beneficiário é empregado registrado da empresa?",
}
OPCOES_FATO = {
    "F2": ["Uma empresa (CNPJ)", "A própria pessoa, por uma associação ou sindicato",
           "A própria pessoa, direto com a operadora"],
    "F3": ["Sim, funciona normalmente", "Não, está parada ou sem movimento"],
    "F4": ["Sim, só familiares", "Não, há pessoas de fora da família"],
    "F5": ["Sim, há vínculo de emprego", "Não, ninguém é empregado da empresa"],
}


def _pergunta(id_, texto, opcoes, evidencias=None, bloqueante=True) -> dict:
    return {
        "id": id_,
        "texto": texto,
        "opcoes": list(opcoes) + [NAO_SEI],
        "evidencias": evidencias or [],
        "bloqueante": bloqueante,
    }


def aplicar_gates(eixo_a: dict, eixo_b: dict, fatos: dict[str, Fato],
                  documentos: list[dict], tipo_peca: str = "PETICAO_INICIAL") -> list[dict]:
    perguntas: list[dict] = []

    # G7 — escopo. Esta fase cobre apenas petições iniciais.
    if tipo_peca != "PETICAO_INICIAL":
        perguntas.append(_pergunta(
            "G7", f"Este pedido é de {tipo_peca}, que está fora do escopo desta skill "
                  "(só petições iniciais). Existem skills separadas do escritório para "
                  "os demais tipos de peça.", ["Entendi, vou usar a skill correta"]))
        return perguntas

    # G4 — sem natureza da operadora não há tese confiável.
    if eixo_b.get("bloqueio") == "G4":
        perguntas.append(_pergunta(
            "G4", "Não consegui identificar a operadora nos documentos, ou ela não está "
                  "no cadastro. Ela é de autogestão (tipo CASSI, ASSEFAZ, GEAP) ou "
                  "comercial (tipo Unimed, Amil, Bradesco)?",
            ["É de autogestão", "É comercial"]))

    # G6 — PJ com atividade real: caso legítimo, mas fora desta skill.
    if eixo_b.get("tese") == "FORA_DO_PADRAO":
        perguntas.append(_pergunta(
            "G6", "A empresa contratante parece ter atividade econômica real. Nesse caso "
                  "a tese de falso coletivo empresarial não se aplica e o caso precisa "
                  "de análise da advogada antes de seguir.",
            ["Confirmo, a empresa funciona mesmo", "Não, a empresa está parada"],
            evidencias=eixo_b.get("evidencias")))

    # G1 — fato de que a tese depende está desconhecido.
    for chave in eixo_b.get("faltando", []):
        perguntas.append(_pergunta(
            f"G1-{chave}", ROTULO_FATO.get(chave, f"Preciso confirmar o fato {chave}."),
            OPCOES_FATO.get(chave, ["Sim", "Não"])))

    # G2 — sinais conflitantes: mostra os dois lados, não escolhe.
    for chave, fato in sorted(fatos.items()):
        for conflito in fato.conflitos:
            perguntas.append(_pergunta(
                f"G2-{chave}", f"Encontrei informações que se contradizem sobre "
                               f"{ROTULO_FATO.get(chave, chave).lower()} Qual vale?",
                [f"Vale: {fato.citacao}", f"Vale: {conflito}"],
                evidencias=[fato.citacao, conflito]))

    # G3 — árvore ambígua fora dos casos acima.
    if eixo_b.get("bloqueio") == "G3":
        perguntas.append(_pergunta(
            "G3", ROTULO_FATO["F2"], OPCOES_FATO["F2"]))

    # G5 — base de cálculo indefinida.
    if eixo_a.get("regime") == "AMBIGUO":
        perguntas.append(_pergunta(
            "G5", "Não consegui decidir se a planilha já traz o cálculo pronto ou se "
                  "preciso calcular do zero.",
            ["O cálculo já está pronto, é só formatar",
             "Precisa calcular o reajuste devido do zero"],
            evidencias=eixo_a.get("evidencias")))
    elif eixo_a.get("regime") == "AUSENTE":
        perguntas.append(_pergunta(
            "G5-ausente", "Não recebi planilha de cálculo nem demonstrativo da operadora. "
                          "Sem isso não dá para apurar valores.",
            ["Vou enviar o arquivo", "Não existe cálculo neste caso"]))

    # Documento não reconhecido nunca é descartado em silêncio.
    for doc in documentos:
        if doc.get("papel") == "INDEFINIDO":
            perguntas.append(_pergunta(
                f"DOC-{doc['arquivo']}", f"Não identifiquei o que é o arquivo "
                                         f"“{doc['arquivo']}”. O que ele é?",
                ["Cálculo/planilha", "Demonstrativo da operadora", "Transcrição de reunião",
                 "Contrato do plano", "Extrato bancário", "Documento pessoal",
                 "Não precisa entrar no caso"],
                bloqueante=False))

    # Fato vindo de imagem/OCR sempre confirma — leitura de digitalização erra.
    for chave, fato in sorted(fatos.items()):
        if fato.valor != DESCONHECIDO and fato.origem in ("ocr", "imagem"):
            perguntas.append(_pergunta(
                f"OCR-{chave}", "Li isto de um documento digitalizado, então pode ter "
                                f"erro de leitura. Confere?",
                [f"Confere: {fato.citacao or fato.valor}", "Está errado, vou corrigir"],
                evidencias=[f"{fato.fonte}: {fato.citacao or fato.valor}"]))

    return perguntas


# --------------------------------------------------------------------------- #
# Dossiê
# --------------------------------------------------------------------------- #

def classificar(documentos: list[dict], planilhas: list[Planilha],
                fatos: dict[str, Fato], tipo_peca: str = "PETICAO_INICIAL") -> dict:
    eixo_a = decidir_eixo_a(planilhas)
    eixo_b = decidir_eixo_b(fatos)
    perguntas = aplicar_gates(eixo_a, eixo_b, fatos, documentos, tipo_peca)

    bloqueantes = [p for p in perguntas if p["bloqueante"]]
    if bloqueantes:
        status = "BLOQUEADO"
    else:
        # G8: o Eixo B nunca é gerado sem confirmação explícita do Espelho,
        # por mais alta que seja a confiança. Erro de tese é irreversível.
        status = "PRECISA_CONFIRMACAO"

    return {
        "status": status,
        "documentos": documentos,
        "eixo_a": eixo_a,
        "eixo_b": {**eixo_b, "modelo_docx": MODELOS.get(eixo_b["tese"])},
        "fatos": {k: asdict(v) for k, v in sorted(fatos.items())},
        "subdecisoes": _subdecisoes(eixo_b, fatos),
        "perguntas": perguntas,
    }


def _subdecisoes(eixo_b: dict, fatos: dict[str, Fato]) -> dict:
    """Decisões que a skill propõe mas nunca fecha sozinha."""
    f6 = _f(fatos, "F6")   # plano ativo ou cancelado
    f9 = _f(fatos, "F9")   # idade do autor
    tese = eixo_b.get("tese")

    if tese == "CASSI_AUTOGESTAO":
        restituicao = ("simples — sem incidência do CDC, a dobra do art. 42 perde base "
                       "direta (arts. 876 e 884 do CC)")
    else:
        restituicao = "decisão humana: simples ou em dobro (art. 42, § único, CDC)"

    if f6.valor == "CANCELADO":
        caminho = "rescisão indireta (plano já cancelado pela parte autora)"
    elif f6.valor == "ATIVO":
        caminho = "tutela de urgência para readequação da mensalidade vincenda"
    else:
        caminho = "indefinido — precisa saber se o plano está ativo ou já foi cancelado"

    idade = None
    try:
        idade = int(str(f9.valor))
    except (TypeError, ValueError):
        pass

    return {
        "restituicao": restituicao,
        "caminho_processual": caminho,
        "prioridade_idoso": ("sim — art. 71 do Estatuto da Pessoa Idosa c/c art. 1.048, I, "
                             "do CPC" if idade and idade >= 60 else "não aplicável"),
        "faixa_etaria": ("cada competência com reajuste de faixa etária é confirmada uma a "
                         "uma antes de entrar no valor devido — legitimidade é decisão "
                         "jurídica (Temas 952 e 1016 do STJ), não cálculo"),
        "valor_da_causa": "decisão humana — fórmula ainda não fechada (pergunta A6)",
    }


# --------------------------------------------------------------------------- #
# Espelho de Classificação
# --------------------------------------------------------------------------- #

ROTULO_REGIME = {
    "CALCULO_PRONTO": "CÁLCULO JÁ PRONTO — é só formatar, não recalculo",
    "FATURAMENTO_BRUTO": "PRECISA SER CALCULADO — a planilha não traz reajuste devido",
    "DEMONSTRATIVO_OPERADORA": "PRECISA SER CALCULADO — veio demonstrativo da operadora",
    "AMBIGUO": "INDEFINIDO — preciso perguntar",
    "AUSENTE": "SEM BASE DE CÁLCULO",
}
ROTULO_TESE = {
    "EMPRESARIAL_FAMILIAR": "FALSO COLETIVO EMPRESARIAL",
    "COLETIVO_POR_ADESAO": "FALSO COLETIVO POR ADESÃO",
    "CASSI_AUTOGESTAO": "AUTOGESTÃO",
    "INDIVIDUAL_COMUM": "REVISIONAL INDIVIDUAL",
    "FORA_DO_PADRAO": "FORA DO PADRÃO — precisa da advogada",
    "INDEFINIDA": "NÃO DEFINIDA",
}


def espelho(dossie: dict, cliente: str = "") -> str:
    """Texto apresentado à operadora ANTES de gerar qualquer coisa.

    Guardado junto com o .docx: se uma peça sair com tese errada, dá para auditar
    qual evidência levou até lá e corrigir a regra, não só o documento.
    """
    L: list[str] = [f"ESPELHO DE CLASSIFICAÇÃO — {cliente or 'caso sem nome'}", ""]

    L.append("Documentos reconhecidos")
    for doc in dossie["documentos"]:
        marca = "  ?" if doc.get("papel") == "INDEFINIDO" else "   "
        origem = doc.get("origem", "")
        sufixo = "  [digitalizado]" if origem in ("ocr", "imagem") else ""
        L.append(f"{marca} {doc['arquivo']} → {doc.get('papel','?')}{sufixo}")
    L.append("")

    a = dossie["eixo_a"]
    L.append(f"Cálculo:  {ROTULO_REGIME.get(a['regime'], a['regime'])}")
    for e in a.get("evidencias", []):
        L.append(f"          · {e}")
    L.append("")

    b = dossie["eixo_b"]
    L.append(f"Tese:     {ROTULO_TESE.get(b['tese'], b['tese'])}")
    for e in b.get("evidencias", []):
        L.append(f"  porque  {e}")
    for d in b.get("descartadas", []):
        L.append(f"  descartei  {ROTULO_TESE.get(d['tese'], d['tese'])} — {d['porque']}")
    if b.get("modelo_docx"):
        L.append(f"  modelo  {b['modelo_docx']}")
    L.append("")

    L.append("A decidir com você")
    for chave, valor in dossie["subdecisoes"].items():
        L.append(f"  • {chave.replace('_', ' ')}: {valor}")
    L.append("")

    perguntas = dossie.get("perguntas", [])
    if perguntas:
        L.append("Preciso que você responda antes de eu gerar")
        for p in perguntas:
            marca = "!" if p["bloqueante"] else "-"
            L.append(f"  {marca} [{p['id']}] {p['texto']}")
            for ev in p.get("evidencias", []):
                L.append(f"        encontrei: {ev}")
            for i, op in enumerate(p["opcoes"], 1):
                L.append(f"        {i}) {op}")
        L.append("")

    if dossie["status"] == "BLOQUEADO":
        L.append("NÃO vou gerar a peça enquanto os itens marcados com ! não forem respondidos.")
    else:
        L.append("Confirma a tese acima para eu gerar a peça? (sim / corrigir)")
    return "\n".join(L)


def main(caminho_json: str) -> int:
    """Entrada de linha de comando: recebe evidências em JSON, imprime o espelho."""
    with open(caminho_json, encoding="utf-8") as fh:
        entrada = json.load(fh)

    planilhas = [Planilha(**p) for p in entrada.get("planilhas", [])]
    fatos = {k: Fato(**v) for k, v in entrada.get("fatos", {}).items()}
    dossie = classificar(entrada.get("documentos", []), planilhas, fatos,
                         entrada.get("tipo_peca", "PETICAO_INICIAL"))

    print(espelho(dossie, entrada.get("cliente", "")))
    print()
    print("--- dossiê ---")
    print(json.dumps(dossie, ensure_ascii=False, indent=2))
    return 0 if dossie["status"] != "BLOQUEADO" else 2


if __name__ == "__main__":
    import sys
    raise SystemExit(main(sys.argv[1]))
