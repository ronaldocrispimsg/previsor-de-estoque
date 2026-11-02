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
    mae: float = Field(..., description="Mean Absolute Error (Erro Médio Absoluto)")
    rmse: float = Field(..., description="Root Mean Squared Error (Raiz do Erro Quadrático Médio)")
    mape: float = Field(..., description="Mean Absolute Percentage Error (Erro Percentual Absoluto Médio)")
    acuracia_estimada: float = Field(..., description="Acurácia percentual (100 - MAPE)")


class DecomposicaoFatores(BaseModel):
    demanda_base_diaria: float = Field(..., description="Giro médio diário base do produto")
    fator_dia_semana_medio: float = Field(..., description="Multiplicador médio por dias de maior fluxo (fins de semana)")
    fator_ciclo_mes: float = Field(..., description="Multiplicador do ciclo quinzenal / quinto dia útil")
    fator_sazonal_festivo: float = Field(..., description="Impacto multiplicativo da data festiva ativa")
    fator_promocional: float = Field(..., description="Impacto de elasticidade em preço promocional")
    ponto_de_pedido: float = Field(..., description="Nível de estoque que dispara ordem de compra")
    lead_time_dias: int = Field(..., description="Prazo de entrega do fornecedor em dias")
    estoque_seguranca: int = Field(..., description="Margem de segurança para evitar ruptura")


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
    decomposicao: DecomposicaoFatores
    serie_temporal: List[PrevisaoPonto]
