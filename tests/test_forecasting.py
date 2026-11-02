"""
tests/test_forecasting.py
Validação do motor preditivo e métricas de qualidade científica.
"""

from datetime import date
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.services.forecasting import calcular_fator_sazonal, prever_demanda_produto


def test_fator_sazonal_pascoa_chocolates():
    data_pascoa = date(2026, 4, 5)  # Abril
    mult, evento = calcular_fator_sazonal("Doces e Chocolates", data_pascoa)
    assert mult > 1.5
    assert evento == "Páscoa"


def test_fator_sazonal_neutro():
    data_comum = date(2026, 9, 15)  # Setembro
    mult, evento = calcular_fator_sazonal("Doces e Chocolates", data_comum)
    assert mult == 1.0
    assert evento is None


def test_previsao_demanda_e_metricas(db_session):
    # Seleciona um produto com histórico populado
    produto = db_session.query(Produto).filter(Produto.nome.ilike("%Chocolate%")).first()
    assert produto is not None

    vendas = db_session.query(Venda).filter(Venda.id_produto == produto.id_produto).all()
    assert len(vendas) > 0

    horizonte = 15
    resp = prever_demanda_produto(produto, vendas, horizonte_dias=horizonte)

    # Validações
    assert resp.resumo.id_produto == produto.id_produto
    assert resp.resumo.demanda_prevista > 0
    assert resp.resumo.confianca >= 50.0
    assert resp.metricas.mae >= 0.0
    assert resp.metricas.rmse >= 0.0
    assert resp.metricas.mape >= 0.0
    assert len(resp.serie_temporal) > horizonte

