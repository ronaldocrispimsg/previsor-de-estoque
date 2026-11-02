"""
backend/app/models/__init__.py
Exporta todas as entidades de banco de dados.
"""

from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.models.previsao import Previsao
from backend.app.models.usuario import Usuario

__all__ = ["Produto", "Venda", "Previsao", "Usuario"]

