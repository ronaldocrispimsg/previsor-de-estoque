"""
backend/app/services/alert_service.py
Serviço de Diagnóstico de Estoque e Emissão de Alertas Inteligentes (Predikta).
"""

from typing import List
from sqlalchemy.orm import Session
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.schemas.dashboard import AlertaEstoque
from backend.app.services.forecasting import prever_demanda_produto


def gerar_alertas_estoque(db: Session, horizonte_dias: int = 15) -> List[AlertaEstoque]:
    """
    Analisa todos os produtos cadastrados e emite alertas classificados por risco de estoque.
    """
    produtos = db.query(Produto).all()
    alertas: List[AlertaEstoque] = []

    for p in produtos:
        vendas = db.query(Venda).filter(Venda.id_produto == p.id_produto).all()
        previsao = prever_demanda_produto(p, vendas, horizonte_dias=horizonte_dias)
        demanda_prevista = previsao.resumo.demanda_prevista

        # Demanda diária estimada
        demanda_diaria = max(0.1, demanda_prevista / horizonte_dias)
        dias_cobertura = round(p.estoque_atual / demanda_diaria, 1)

        # Checagem de RUPTURA (Falta de Estoque)
        if p.estoque_atual <= 0:
            alertas.append(
                AlertaEstoque(
                    id_produto=p.id_produto,
                    nome_produto=p.nome,
                    categoria=p.categoria,
                    tipo_alerta="RUPTURA",
                    severidade="critico",
                    estoque_atual=p.estoque_atual,
                    demanda_prevista_periodo=demanda_prevista,
                    dias_cobertura_estoque=0.0,
                    sugestao_acao=f"Ruptura Total! Emitir pedido urgente de reposição de pelo menos {int(demanda_prevista + p.estoque_minimo)} un.",
                    quantidade_sugerida=round(demanda_prevista + p.estoque_minimo, 1),
                )
            )
        elif p.estoque_atual < (demanda_prevista * 0.5):
            alertas.append(
                AlertaEstoque(
                    id_produto=p.id_produto,
                    nome_produto=p.nome,
                    categoria=p.categoria,
                    tipo_alerta="RUPTURA",
                    severidade="critico",
                    estoque_atual=p.estoque_atual,
                    demanda_prevista_periodo=demanda_prevista,
                    dias_cobertura_estoque=dias_cobertura,
                    sugestao_acao=f"Risco de Ruptura! Estoque cobre apenas {dias_cobertura} dias. Comprar {int(demanda_prevista - p.estoque_atual)} un.",
                    quantidade_sugerida=round(demanda_prevista - p.estoque_atual, 1),
                )
            )
        elif p.estoque_atual < p.estoque_minimo:
            alertas.append(
                AlertaEstoque(
                    id_produto=p.id_produto,
                    nome_produto=p.nome,
                    categoria=p.categoria,
                    tipo_alerta="ATENCAO",
                    severidade="medio",
                    estoque_atual=p.estoque_atual,
                    demanda_prevista_periodo=demanda_prevista,
                    dias_cobertura_estoque=dias_cobertura,
                    sugestao_acao=f"Estoque abaixo do ponto de segurança ({p.estoque_minimo} un). Programar pedido preventivo.",
                    quantidade_sugerida=round(p.estoque_minimo * 1.5 - p.estoque_atual, 1),
                )
            )
        # Checagem de EXCESSO de estoque
        elif p.estoque_atual > (demanda_prevista * 2.5) and p.estoque_atual > 30:
            qtd_excedente = round(p.estoque_atual - (demanda_prevista * 1.5), 1)
            alertas.append(
                AlertaEstoque(
                    id_produto=p.id_produto,
                    nome_produto=p.nome,
                    categoria=p.categoria,
                    tipo_alerta="EXCESSO",
                    severidade="medio",
                    estoque_atual=p.estoque_atual,
                    demanda_prevista_periodo=demanda_prevista,
                    dias_cobertura_estoque=dias_cobertura,
                    sugestao_acao=f"Excesso de estoque ({dias_cobertura} dias de giro). Risco de custo de armazenagem/validade. Avaliar promoção.",
                    quantidade_sugerida=qtd_excedente,
                )
            )

    # Ordena: críticos primeiro, depois médios
    severidade_ordem = {"critico": 0, "medio": 1, "baixo": 2}
    alertas.sort(key=lambda a: severidade_ordem.get(a.severidade, 3))
    return alertas
