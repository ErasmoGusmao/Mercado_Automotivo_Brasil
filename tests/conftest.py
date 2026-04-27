"""Configuração compartilhada do pytest.

Adiciona a raiz do projeto ao `sys.path` para que `import src` funcione sem
instalar o pacote (pip install -e). Mantém o setup de testes simples para
um projeto de notebook + módulo local.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
