"""
backend/app/schemas/venda.py
Contratos de dados Pydantic para Vendas.
"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class VendaBase(BaseModel):
    id_produto: int = Field(..., description="Identificador do produto vendido")
    data: date = Field(..., description="Data da venda")
    quantidade: int = Field(..., gt=0, description="Quantidade vendida")
    preco: float = Field(..., gt=0, description="Preço efetivamente praticado")
    promocao: bool = Field(False, description="Indicação se a venda ocorreu sob promoção")


class VendaCreate(VendaBase):
    pass


class VendaResponse(VendaBase):
    id_venda: int
    nome_produto: Optional[str] = None
    categoria_produto: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class VendaImportItem(VendaBase):
    pass


class VendaImportBatch(BaseModel):
    vendas: List[VendaImportItem]

