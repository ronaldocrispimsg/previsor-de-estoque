"""
backend/app/schemas/dashboard.py
Contratos de dados Pydantic para o Dashboard e Telas de Sazonalidade/Alertas.
"""

from typing import List, Optional
from pydantic import BaseModel


class AlertaEstoque(BaseModel):
    id_produto: int
    nome_produto: str
    categoria: str
    tipo_alerta: str  # "RUPTURA", "ATENCAO", "EXCESSO"
    severidade: str   # "critico", "medio", "baixo"
    estoque_atual: int
    demanda_prevista_periodo: float
    dias_cobertura_estoque: float
    sugestao_acao: str
    quantidade_sugerida: float


class DashboardStatsResponse(BaseModel):
    total_produtos: int
    total_vendas_30d: int
    receita_estimada_30d: float
    acuracia_media_modelo: float
    alertas_ruptura: int
    alertas_excesso: int
    reducao_estimada_perdas_pct: float = 18.0  # Métrica validada na apresentação Predikta


class GraficoPonto(BaseModel):
    label: str
    valor_real: Optional[float] = None
    valor_previsto: Optional[float] = None


class GraficoCategoria(BaseModel):
    categoria: str
    total_vendas: int
    faturamento: float
    participacao_pct: float


class SazonalidadeEvento(BaseModel):
    id_evento: str
    nome: str
    periodo: str
    meses_afetados: List[int]
    descricao: str
    exemplo_produtos: List[str]
    multiplicador_medio: float
    produtos_impactados: List[dict]
