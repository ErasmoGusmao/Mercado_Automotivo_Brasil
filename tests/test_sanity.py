"""Smoke test do projeto.

Garante que:
1. O pacote `src` é importável.
2. A versão declarada bate com a versão do MVP.
3. Python mínimo (3.10+) está em uso.
"""
import sys


def test_pacote_src_importavel():
    import src
    assert hasattr(src, "__version__")


def test_versao_pacote():
    import src
    assert src.__version__ == "0.1.0"


def test_python_minimo():
    assert sys.version_info >= (3, 10), (
        f"Python 3.10+ requerido; encontrado {sys.version_info.major}.{sys.version_info.minor}"
    )
