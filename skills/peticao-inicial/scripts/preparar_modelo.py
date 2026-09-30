"""Prepara o DOCX-modelo do escritório a partir de uma peça já protocolada.

Existe porque o gerador **parte do DOCX real do escritório** — é o `sectPr` dele que
carrega as referências de cabeçalho e rodapé onde vive o timbre. Montar do zero perde o
timbre.

O que este script faz: esvazia o corpo, mantém `sectPr`, estilos, numeração,
cabeçalhos e rodapés, e **remove as imagens referenciadas pelo corpo** (as tabelas em
imagem da peça antiga) e os metadados de autoria. O que sai é papel timbrado em branco.

O que ele NÃO faz: garantir que não sobrou dado de cliente. Cabeçalho e rodapé são
copiados como estão — se o timbre do escritório tiver algo do caso, continua lá. Por
isso o script confere e avisa, e o arquivo de saída **não vai para o repositório**:
`assets/modelos/` é local da máquina de quem usa.

    python3 preparar_modelo.py peca-protocolada.docx modelo-timbre.docx
"""

from __future__ import annotations

import re
import sys
import zipfile


# Campos de metadado que carregam nome de quem redigiu, do cliente ou do caso. São
# ESVAZIADOS, não removidos: apagar a parte inteira quebra o pacote, porque o
# `_rels/.rels` continua apontando para ela e o Word recusa o arquivo.
CAMPOS_METADADOS = ("dc:creator", "cp:lastModifiedBy", "dc:title", "dc:subject",
                    "dc:description", "cp:keywords", "cp:category", "Company",
                    "Manager")

# Sinais de que sobrou dado pessoal no que foi mantido. Não é validação — é alerta.
RE_CPF = re.compile(r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b")
RE_CNPJ = re.compile(r"\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b")


def _esvaziar_metadados(bruto: bytes) -> bytes:
    texto = bruto.decode("utf-8", "replace")
    for campo in CAMPOS_METADADOS:
        texto = re.sub(rf"<{campo}(\s[^>]*)?>.*?</{campo}>", f"<{campo}></{campo}>",
                       texto, flags=re.S)
    return texto.encode("utf-8")


def preparar(origem: str, destino: str) -> list[str]:
    """Devolve a lista de alertas. Lista vazia não é certificado de limpeza."""
    alertas: list[str] = []
    with zipfile.ZipFile(origem) as zin:
        doc = zin.read("word/document.xml").decode("utf-8")

        m = re.search(r"<w:sectPr\b.*?</w:sectPr>", doc, re.S)
        if not m:
            raise SystemExit(
                f"{origem}: não achei o <w:sectPr> — sem ele o timbre se perde. "
                f"Este arquivo serve como modelo?")
        sectPr = m.group()
        cabeca = doc[:doc.index("<w:body>")]
        corpo_vazio = f"{cabeca}<w:body><w:p/>{sectPr}</w:body></w:document>"

        rels = zin.read("word/_rels/document.xml.rels").decode("utf-8")
        media_do_corpo = {f"word/{alvo}" for alvo in
                          re.findall(r'Target="(media/[^"]+)"', rels)}
        rels_sem_media = re.sub(
            r"<Relationship[^>]*Target=\"media/[^\"]+\"[^>]*/>", "", rels)

        with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                nome = item.filename
                if nome == "word/document.xml":
                    zout.writestr(item, corpo_vazio)
                elif nome == "word/_rels/document.xml.rels":
                    zout.writestr(item, rels_sem_media)
                elif nome in media_do_corpo:
                    continue
                else:
                    bruto = zin.read(nome)
                    if nome.startswith("docProps/"):
                        bruto = _esvaziar_metadados(bruto)
                    if nome.startswith(("word/header", "word/footer")):
                        texto = bruto.decode("utf-8", "replace")
                        if RE_CPF.search(texto) or RE_CNPJ.search(texto):
                            alertas.append(
                                f"{nome} tem algo com cara de CPF/CNPJ — abra o modelo "
                                f"no Word e confira o cabeçalho e o rodapé antes de usar")
                    zout.writestr(item, bruto)

    if media_do_corpo:
        alertas.append(f"{len(media_do_corpo)} imagem(ns) do corpo removida(s) — se "
                       f"alguma era o timbre, ele está no cabeçalho, não no corpo")
    return alertas


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    alertas = preparar(argv[1], argv[2])
    print(f"Modelo gravado em {argv[2]}")
    for a in alertas:
        print(f"  AVISO: {a}")
    print("\nAbra no Word e confira: o timbre tem que aparecer e o corpo tem que estar "
          "vazio. Guarde o arquivo na sua máquina — modelo com dado de caso não vai "
          "para o repositório.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
