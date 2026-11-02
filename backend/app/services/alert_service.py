"""
backend/app/services/alert_service.py
Serviço de Diagnóstico de Estoque e Emissão de Alertas Inteligentes (Predikta).
Calcula indicadores de cobertura em dias e impacto financeiro (R$) estimado.
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
            qtd_falta = round(demanda_prevista + p.estoque_minimo, 1)
            perda_faturamento = round(qtd_falta * p.preco_base, 2)
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
                    sugestao_acao=f"Ruptura Total! Emitir pedido urgente de reposição de pelo menos {int(qtd_falta)} un.",
                    quantidade_sugerida=qtd_falta,
                    impacto_financeiro_estimado=perda_faturamento
                )
            )
        elif p.estoque_atual < (demanda_prevista * 0.4):
            qtd_comprar = round(demanda_prevista - p.estoque_atual, 1)
            perda_faturamento = round(qtd_comprar * p.preco_base, 2)
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
                    sugestao_acao=f"Risco Severo de Ruptura! Estoque cobre apenas {dias_cobertura} dias. Comprar {int(qtd_comprar)} un.",
                    quantidade_sugerida=qtd_comprar,
                    impacto_financeiro_estimado=perda_faturamento
                )
            )
        elif p.estoque_atual < previsao.decomposicao.ponto_de_pedido:
            qtd_repor = round(previsao.decomposicao.ponto_de_pedido - p.estoque_atual, 1)
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
                    sugestao_acao=f"Abaixo do ponto de pedido ({previsao.decomposicao.ponto_de_pedido} un). Programar compra preventiva.",
                    quantidade_sugerida=qtd_repor,
                    impacto_financeiro_estimado=round(qtd_repor * p.preco_base, 2)
                )
            )
        # Checagem de EXCESSO de estoque
        elif p.estoque_atual > (demanda_prevista * 2.2) and p.estoque_atual > 30:
            qtd_excedente = round(p.estoque_atual - (demanda_prevista * 1.3), 1)
            capital_imobilizado = round(qtd_excedente * p.preco_base, 2)
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
                    sugestao_acao=f"Excesso de estoque ({dias_cobertura} dias de cobertura). Risco de custo de estocagem/validade.",
                    quantidade_sugerida=qtd_excedente,
                    impacto_financeiro_estimado=capital_imobilizado
                )
            )

    # Ordena: críticos primeiro, depois médios
    severidade_ordem = {"critico": 0, "medio": 1, "baixo": 2}
    alertas.sort(key=lambda a: severidade_ordem.get(a.severidade, 3))
    return alertas
