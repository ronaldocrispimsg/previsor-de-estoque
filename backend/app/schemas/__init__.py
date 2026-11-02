"""
backend/app/schemas/__init__.py
Exportação centralizada dos schemas Pydantic.
"""

from backend.app.schemas.produto import ProdutoCreate, ProdutoUpdate, ProdutoResponse, ProdutoListResponse, ProdutoAjusteEstoque
from backend.app.schemas.venda import VendaCreate, VendaResponse, VendaImportBatch, VendaImportItem
from backend.app.schemas.previsao import (
    PrevisaoRequest, PrevisaoResponse, PrevisaoDetalhadaResponse,
    PrevisaoPonto, MetricasQualidade, DecomposicaoFatores
)
from backend.app.schemas.dashboard import (
    DashboardStatsResponse, AlertaEstoque, GraficoPonto,
    GraficoCategoria, SazonalidadeEvento, ProdutoDestaque, MesIndiceSazonal
)
from backend.app.schemas.usuario import LoginRequest, LoginResponse, UsuarioResponse

__all__ = [
    "ProdutoCreate", "ProdutoUpdate", "ProdutoResponse", "ProdutoListResponse", "ProdutoAjusteEstoque",
    "VendaCreate", "VendaResponse", "VendaImportBatch", "VendaImportItem",
    "PrevisaoRequest", "PrevisaoResponse", "PrevisaoDetalhadaResponse", "PrevisaoPonto",
    "MetricasQualidade", "DecomposicaoFatores",
    "DashboardStatsResponse", "AlertaEstoque", "GraficoPonto", "GraficoCategoria",
    "SazonalidadeEvento", "ProdutoDestaque", "MesIndiceSazonal",
    "LoginRequest", "LoginResponse", "UsuarioResponse"
]
