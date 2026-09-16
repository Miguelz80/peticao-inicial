#!/usr/bin/env bash
# Gera o .zip da skill para instalar no Claude Desktop.
#
#     ./empacotar.sh            → elaborador-inicial.zip na raiz do repositório
#
# O zip leva SKILL.md, scripts/ e references/. NÃO leva assets/modelos/: o modelo
# timbrado fica na máquina de quem usa, porque sai de peça real do escritório.
set -euo pipefail

cd "$(dirname "$0")"
DESTINO="elaborador-inicial.zip"
rm -f "$DESTINO"

for f in tests/test_*.py; do
    python3 "$f" > /dev/null || { echo "ABORTADO: $f falhou"; exit 1; }
done
echo "testes: ok"

# Carimbo de versão: sem ele não há como saber, olhando um relatório, se quem rodou
# usou a cópia instalada ou a do repositório — e cópias dessincronizadas fazem testar
# uma coisa e corrigir outra.
printf '%s (commit %s)\n' "$(date +%d/%m/%Y)" "$(git rev-parse --short HEAD)" \
    > skills/elaborador-inicial/VERSAO
trap 'rm -f skills/elaborador-inicial/VERSAO' EXIT

cd skills
zip -qr "../$DESTINO" elaborador-inicial \
    -x '*/__pycache__/*' '*.pyc' '*/assets/modelos/*' '*/assets/timbre/*' '*/.gitkeep'
cd ..

python3 - "$DESTINO" <<'PY'
import sys, zipfile
z = zipfile.ZipFile(sys.argv[1])
nomes = z.namelist()
assert "elaborador-inicial/SKILL.md" in nomes, "SKILL.md tem que estar na raiz da pasta"
vazou = [n for n in nomes if n.endswith((".pdf", ".docx", ".xlsx"))]
assert not vazou, f"documento de caso no pacote: {vazou}"
print(f"{sys.argv[1]}: {len(nomes)} arquivos, {sum(i.file_size for i in z.infolist())//1024} KB")
PY
