"""
tests/test_models.py
Validação das entidades e relacionamentos relacionais do Predikta.
"""

from datetime import date
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.models.previsao import Previsao


def test_criacao_produto_e_relacionamento_vendas(db_session):
    prod = Produto(
        nome="Produto Teste Unidade",
        categoria="Mercearia",
        preco_base=12.50,
        estoque_atual=50,
        estoque_minimo=15,
        lead_time_dias=3
    )
    db_session.add(prod)
    db_session.commit()
    db_session.refresh(prod)

    assert prod.id_produto is not None
    assert prod.nome == "Produto Teste Unidade"

    # Adiciona vendas relacionadas (1 -> N)
    venda1 = Venda(id_produto=prod.id_produto, data=date(2026, 4, 1), quantidade=5, preco=12.50, promocao=False)
    venda2 = Venda(id_produto=prod.id_produto, data=date(2026, 4, 2), quantidade=10, preco=10.00, promocao=True)
    db_session.add_all([venda1, venda2])
    db_session.commit()

    db_session.refresh(prod)
    assert len(prod.vendas) == 2
    assert prod.vendas[0].quantidade in [5, 10]


def test_relacionamento_previsao(db_session):
    prod = db_session.query(Produto).first()
    assert prod is not None

    prev = Previsao(
        id_produto=prod.id_produto,
        periodo="2026-W15",
        horizonte_dias=15,
        demanda_prevista=45.0,
        metodo="Sazonal Teste",
        confianca=92.5,
        sugestao_reposicao=10.0,
        status_risco="EQUILIBRADO"
    )
    db_session.add(prev)
    db_session.commit()
    db_session.refresh(prev)

    assert prev.id_previsao is not None
    assert prev.produto.id_produto == prod.id_produto
