"""
backend/app/schemas/__init__.py
Exportação centralizada dos schemas Pydantic.
"""

from backend.app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoResponse, ProdutoListResponse
from backend.app.schemas.venda import VendaCreate, VendaResponse, VendaImportBatch
from backend.app.schemas.previsao import PrevisaoRequest, PrevisaoResponse, PrevisaoDetalhadaResponse, PrevisaoPonto, MetricasQualidade
from backend.app.schemas.dashboard import DashboardStatsResponse, AlertaEstoque, GraficoPonto, GraficoCategoria, SazonalidadeEvento
from backend.app.schemas.usuario import LoginRequest, LoginResponse, UsuarioResponse

__all__ = [
    "ProdutoCreate", "ProdutoUpdate", "ProdutoResponse", "ProdutoListResponse",
    "VendaCreate", "VendaResponse", "VendaImportBatch",
    "PrevisaoRequest", "PrevisaoResponse", "PrevisaoDetalhadaResponse", "PrevisaoPonto", "MetricasQualidade",
    "DashboardStatsResponse", "AlertaEstoque", "GraficoPonto", "GraficoCategoria", "SazonalidadeEvento",
    "LoginRequest", "LoginResponse", "UsuarioResponse"
]
