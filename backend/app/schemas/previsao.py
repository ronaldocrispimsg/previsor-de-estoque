"""
backend/app/schemas/previsao.py
Contratos de dados Pydantic para Previsão de Demanda.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PrevisaoRequest(BaseModel):
    id_produto: int = Field(..., description="ID do produto a ser previsto")
    horizonte_dias: int = Field(15, ge=7, le=90, description="Horizonte de previsão em dias (7, 15, 30, etc.)")
    considerar_promocao: bool = Field(False, description="Simular impacto de promoção no período")


class PrevisaoPonto(BaseModel):
    data: str
    quantidade_historica: Optional[float] = None
    demanda_prevista: Optional[float] = None
    limite_inferior: Optional[float] = None
    limite_superior: Optional[float] = None


class MetricasQualidade(BaseModel):
    mae: float = Field(..., description="Mean Absolute Error")
    rmse: float = Field(..., description="Root Mean Squared Error")
    mape: float = Field(..., description="Mean Absolute Percentage Error (%)")
    acuracia_estimada: float = Field(..., description="Acurácia percentual (100 - MAPE)")


class PrevisaoResponse(BaseModel):
    id_previsao: Optional[int] = None
    id_produto: int
    nome_produto: str
    categoria: str
    periodo: str
    horizonte_dias: int
    demanda_prevista: float
    estoque_atual: int
    sugestao_reposicao: float
    status_risco: str  # "RUPTURA", "EXCESSO", "EQUILIBRADO"
    metodo: str
    confianca: float
    data_geracao: datetime
    impacto_sazonal_identificado: Optional[str] = None
    multiplicador_sazonal: float = 1.0

    model_config = ConfigDict(from_attributes=True)


class PrevisaoDetalhadaResponse(BaseModel):
    resumo: PrevisaoResponse
    metricas: MetricasQualidade
    serie_temporal: List[PrevisaoPonto]
