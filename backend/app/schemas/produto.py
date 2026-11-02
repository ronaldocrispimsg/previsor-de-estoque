"""
backend/app/schemas/produto.py
Contratos de dados Pydantic para Produto.
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150, description="Nome do produto")
    categoria: str = Field(..., min_length=2, max_length=80, description="Categoria do produto")
    preco_base: float = Field(..., gt=0, description="Preço de referência do produto")
    estoque_atual: int = Field(0, ge=0, description="Quantidade atual em estoque")
    estoque_minimo: int = Field(10, ge=0, description="Estoque de segurança mínimo")
    lead_time_dias: int = Field(3, ge=1, description="Tempo médio de reposição em dias")


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    categoria: Optional[str] = Field(None, min_length=2, max_length=80)
    preco_base: Optional[float] = Field(None, gt=0)
    estoque_atual: Optional[int] = Field(None, ge=0)
    estoque_minimo: Optional[int] = Field(None, ge=0)
    lead_time_dias: Optional[int] = Field(None, ge=1)


class ProdutoAjusteEstoque(BaseModel):
    quantidade: int = Field(..., description="Quantidade a somar (positiva) ou abater (negativa)")
    motivo: str = Field("Entrada de Mercadoria", description="Motivo do ajuste")


class ProdutoResponse(ProdutoBase):
    id_produto: int
    status_estoque: Optional[str] = "EQUILIBRADO"  # "RUPTURA", "ATENCAO", "EXCESSO", "EQUILIBRADO"
    ponto_de_pedido: Optional[float] = None
    giro_diario_estimado: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ProdutoListResponse(BaseModel):
    total: int
    produtos: List[ProdutoResponse]
