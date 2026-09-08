"""Extração determinística de evidências dos documentos do caso.

Só lê e descreve o que encontrou — não decide nada. A decisão é do classificar.py.
Toda saída declara a ORIGEM do texto (nativo, ocr, imagem), porque fato lido de
digitalização vale menos e sempre volta como pergunta à operadora.

Dependências são opcionais: faltando uma biblioteca, o arquivo é reportado como
ilegível em vez de derrubar a execução.
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass, field, asdict


MIN_CHARS_PAGINA = 60      # abaixo disso, a página não tem camada de texto útil


@dataclass
class Trecho:
    arquivo: str
    paginas: tuple[int, int] | None
    texto: str
    origem: str                       # texto_nativo | imagem | planilha
    papel: str = "INDEFINIDO"


@dataclass
class Extracao:
    trechos: list[Trecho] = field(default_factory=list)
    planilhas: list[dict] = field(default_factory=list)
    ilegiveis: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Triagem: que documento é este
# --------------------------------------------------------------------------- #

# Marcadores estruturais, não semânticos. Nome de arquivo é dica, nunca prova.
MARCADORES = {
    "CONTRATO_SOCIAL":  ["contrato social", "capital social", "junta comercial"],
    "EXTRATO_BANCARIO": ["saldo disponivel", "extrato", "bloqueio judicial",
                         "agencia", "lancamentos"],
    "CARTEIRINHA":      ["numero do beneficiario", "acomodacao", "abrangencia",
                         "carteira", "registro ans"],
    "BOLETO":           ["nosso numero", "cedente", "linha digitavel", "sacado"],
    "CONTRATO_PLANO":   ["contrato de adesao", "clausula", "regulamento",
                         "participante", "cobertura"],
    "PROCURACAO":       ["procuracao", "outorgante", "outorgado", "poderes"],
    "DOC_PESSOAL":      ["registro geral", "orgao expedidor", "filiacao",
                         "cadastro de pessoas fisicas"],
    "DEMONSTRATIVO_OPERADORA": ["demonstrativo de pagamento", "data baixa",
                                "tipo lancamento", "competencia"],
    "PROPOSTA_ADESAO":  ["proposta de adesao", "declaro que", "corretor"],
}

# Peça processual compartilha vocabulário com o contrato do plano ("cláusula",
# "cobertura"), então é reconhecida por estrutura própria e testada primeiro —
# ler uma inicial como se fosse contrato do cliente seria erro grave.
MARCADORES_PECA = ["excelentissimo", "ao juizo da", "meritissimo",
                   "pede deferimento", "vem, respeitosamente", "oab/",
                   "dos pedidos", "valor da causa"]

RE_TURNO_FALA = re.compile(r"(^|\n)\s*(\[\d{1,2}:\d{2}|[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\w\s]{2,30}:)")


def _normalizar(t: str) -> str:
    import unicodedata
    sem = "".join(c for c in unicodedata.normalize("NFD", t or "")
                  if unicodedata.category(c) != "Mn")
    return " ".join(sem.lower().split())


def identificar_papel(texto: str) -> tuple[str, list[str]]:
    n = _normalizar(texto)
    if len(RE_TURNO_FALA.findall(texto or "")) >= 6:
        return "TRANSCRICAO", ["marcas de turnos de fala"]

    achados_peca = [m for m in MARCADORES_PECA if m in n]
    if len(achados_peca) >= 2:
        return "PECA_PROCESSUAL", [f"estrutura de peça: {', '.join(achados_peca)}"]
    melhor, achados_melhor = "INDEFINIDO", []
    for papel, marcas in MARCADORES.items():
        achados = [m for m in marcas if m in n]
        if len(achados) > len(achados_melhor):
            melhor, achados_melhor = papel, achados
    if len(achados_melhor) >= 2:
        return melhor, [f"marcadores: {', '.join(achados_melhor)}"]
    return "INDEFINIDO", ["nenhum marcador suficiente"]


# --------------------------------------------------------------------------- #
# Leitores por formato
# --------------------------------------------------------------------------- #

def _ler_pdf(caminho: str, ex: Extracao) -> None:
    """Segmenta por página: um arquivo pode conter vários documentos, e páginas
    com e sem camada de texto costumam conviver no mesmo PDF."""
    try:
        from pypdf import PdfReader
    except ImportError:
        ex.ilegiveis.append(f"{caminho}: pypdf não instalado")
        return
    try:
        paginas = [(p.extract_text() or "") for p in PdfReader(caminho).pages]
    except Exception as erro:                      # PDF corrompido, cifrado, etc.
        ex.ilegiveis.append(f"{caminho}: {erro}")
        return

    # Duas passagens. A primeira classifica página a página, que é o que permite
    # separar dois documentos colados no mesmo arquivo (demonstrativo + regulamento).
    # Mas página isolada de um documento longo raramente tem marcadores suficientes,
    # e uma petição de 16 páginas acabaria picotada. Então: se a maioria das páginas
    # ficou INDEFINIDA, o arquivo é tratado como um documento só.
    por_pagina = []
    for txt in paginas:
        origem = "texto_nativo" if len(txt) >= MIN_CHARS_PAGINA else "imagem"
        papel = identificar_papel(txt)[0] if origem == "texto_nativo" else "INDEFINIDO"
        por_pagina.append((papel, origem, txt))

    com_texto = [p for p in por_pagina if p[1] == "texto_nativo"]
    indefinidas = [p for p in com_texto if p[0] == "INDEFINIDO"]
    fragmentado = com_texto and len(indefinidas) / len(com_texto) > 0.5

    if fragmentado:
        inteiro = "\n".join(t for _, _, t in com_texto)
        papel_inteiro = identificar_papel(inteiro)[0]
        if papel_inteiro != "INDEFINIDO":
            por_pagina = [(papel_inteiro if o == "texto_nativo" else "INDEFINIDO", o, t)
                          for _, o, t in por_pagina]

    bloco_ini, bloco_papel, bloco_txt = 0, None, []
    for i, (papel, origem, txt) in enumerate(por_pagina):
        chave = (papel, origem)
        if bloco_papel is None:
            bloco_papel, bloco_ini, bloco_txt = chave, i, [txt]
        elif chave == bloco_papel:
            bloco_txt.append(txt)
        else:
            _fechar(ex, caminho, bloco_ini, i - 1, bloco_papel, bloco_txt)
            bloco_papel, bloco_ini, bloco_txt = chave, i, [txt]
    if bloco_papel is not None:
        _fechar(ex, caminho, bloco_ini, len(por_pagina) - 1, bloco_papel, bloco_txt)


def _fechar(ex, caminho, ini, fim, chave, textos) -> None:
    papel, origem = chave
    texto = "\n".join(textos)
    ex.trechos.append(Trecho(caminho, (ini + 1, fim + 1), texto, origem, papel))
    if papel == "DEMONSTRATIVO_OPERADORA":
        ex.planilhas.append({"arquivo": f"{os.path.basename(caminho)} (pgs {ini+1}-{fim+1})",
                             "cabecalhos": [], "linhas": [], "texto_solto": texto})


def _ler_xlsx(caminho: str, ex: Extracao) -> None:
    try:
        import openpyxl
    except ImportError:
        ex.ilegiveis.append(f"{caminho}: openpyxl não instalado")
        return
    try:
        wb = openpyxl.load_workbook(caminho, data_only=True, read_only=True)
    except Exception as erro:
        ex.ilegiveis.append(f"{caminho}: {erro}")
        return
    for aba in wb.worksheets:
        linhas = [list(r) for r in aba.iter_rows(values_only=True)]
        if not linhas:
            continue
        i = _linha_de_cabecalho(linhas)
        ex.planilhas.append({
            "arquivo": f"{os.path.basename(caminho)}[{aba.title}]",
            "cabecalhos": [str(c) if c is not None else "" for c in linhas[i]],
            "linhas": linhas[i + 1:],
            "texto_solto": "",
        })


def _linha_de_cabecalho(linhas: list[list], limite: int = 10) -> int:
    """A planilha do escritório costuma ter título e linhas soltas antes do
    cabeçalho real. Cabeçalho = primeira linha com mais células de texto não vazio."""
    melhor_i, melhor_n = 0, -1
    for i, linha in enumerate(linhas[:limite]):
        n = sum(1 for c in linha if isinstance(c, str) and c.strip())
        if n > melhor_n:
            melhor_i, melhor_n = i, n
    return melhor_i


def _ler_csv(caminho: str, ex: Extracao) -> None:
    with open(caminho, encoding="utf-8", errors="replace", newline="") as fh:
        amostra = fh.read(4096)
        fh.seek(0)
        try:
            dialeto = csv.Sniffer().sniff(amostra, delimiters=";,\t")
        except csv.Error:
            dialeto = csv.excel
        linhas = [l for l in csv.reader(fh, dialeto)]
    if not linhas:
        return
    i = _linha_de_cabecalho(linhas)
    ex.planilhas.append({"arquivo": os.path.basename(caminho),
                         "cabecalhos": linhas[i], "linhas": linhas[i + 1:],
                         "texto_solto": ""})


def _ler_docx(caminho: str, ex: Extracao) -> None:
    try:
        import docx
    except ImportError:
        ex.ilegiveis.append(f"{caminho}: python-docx não instalado")
        return
    try:
        d = docx.Document(caminho)
    except Exception as erro:
        ex.ilegiveis.append(f"{caminho}: {erro}")
        return
    texto = "\n".join(p.text for p in d.paragraphs)
    ex.trechos.append(Trecho(caminho, None, texto, "texto_nativo",
                             identificar_papel(texto)[0]))


def _ler_txt(caminho: str, ex: Extracao) -> None:
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        texto = fh.read()
    ex.trechos.append(Trecho(caminho, None, texto, "texto_nativo",
                             identificar_papel(texto)[0]))


LEITORES = {".pdf": _ler_pdf, ".xlsx": _ler_xlsx, ".xlsm": _ler_xlsx,
            ".csv": _ler_csv, ".docx": _ler_docx, ".txt": _ler_txt, ".md": _ler_txt}


def extrair(caminhos: list[str]) -> Extracao:
    ex = Extracao()
    for caminho in caminhos:
        leitor = LEITORES.get(os.path.splitext(caminho)[1].lower())
        if leitor is None:
            ex.ilegiveis.append(f"{caminho}: formato não suportado")
            continue
        try:
            leitor(caminho, ex)
        except Exception as erro:                  # nunca derruba o lote inteiro
            ex.ilegiveis.append(f"{caminho}: {erro}")
    return ex


def para_documentos(ex: Extracao) -> list[dict]:
    """Formato que o classificar.py consome na lista `documentos`."""
    docs = []
    for t in ex.trechos:
        nome = os.path.basename(t.arquivo)
        if t.paginas:
            nome += f" (pgs {t.paginas[0]}-{t.paginas[1]})"
        docs.append({"arquivo": nome, "papel": t.papel, "origem": t.origem})
    for ruim in ex.ilegiveis:
        docs.append({"arquivo": ruim.split(":")[0], "papel": "INDEFINIDO",
                     "origem": "ilegivel"})
    return docs


if __name__ == "__main__":
    import json, sys
    ex = extrair(sys.argv[1:])
    print(json.dumps({"documentos": para_documentos(ex),
                      "planilhas": ex.planilhas,
                      "ilegiveis": ex.ilegiveis,
                      "trechos": [asdict(t) for t in ex.trechos]},
                     ensure_ascii=False, indent=2)[:4000])
