"""Guarda da própria suíte. Rodar: python3 tests/test_suite.py

Existe por um erro que se repetiu três vezes: ao acrescentar testes no fim do
arquivo, eles caíam **depois** do bloco `if __name__ == "__main__"`, que já tinha
executado — e a suíte reportava sucesso sem tê-los rodado.
"""

import pathlib, re

TESTES = sorted(pathlib.Path(__file__).parent.glob("test_*.py"))
# Ancorado no início da linha: procurar a marca solta encontrava também esta própria
# constante, e o guarda acusava a si mesmo.
RUNNER = re.compile(r'^if __name__ == "__main__":', re.MULTILINE)


def test_o_runner_e_a_ultima_coisa_de_cada_arquivo():
    for arquivo in TESTES:
        texto = arquivo.read_text(encoding="utf-8")
        m = RUNNER.search(texto)
        if not m:
            continue
        assert "\ndef test_" not in texto[m.start():], (
            f"{arquivo.name}: há teste definido depois do runner — ele nunca roda")


def test_todo_arquivo_de_teste_tem_runner():
    for arquivo in TESTES:
        assert RUNNER.search(arquivo.read_text(encoding="utf-8")), arquivo.name


if __name__ == "__main__":
    import traceback
    testes = [(n, o) for n, o in sorted(globals().items())
              if n.startswith("test_") and callable(o)]
    falhas = 0
    for nome, fn in testes:
        try:
            fn(); print(f"  ok    {nome}")
        except Exception:
            falhas += 1; print(f"  FALHA {nome}"); traceback.print_exc()
    print(f"\n{len(testes)-falhas}/{len(testes)} passaram")
    raise SystemExit(1 if falhas else 0)
