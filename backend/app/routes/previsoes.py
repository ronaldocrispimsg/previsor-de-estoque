"""
backend/app/routes/previsoes.py
Rotas RESTful para geração e consulta de Previsões de Demanda.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.previsao import Previsao
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.schemas.previsao import PrevisaoDetalhadaResponse, PrevisaoRequest, PrevisaoResponse
from backend.app.services.forecasting import prever_demanda_produto

router = APIRouter(prefix="/previsoes", tags=["Previsões de Demanda"])


@router.post("/gerar", response_model=PrevisaoDetalhadaResponse)
def gerar_previsao(dados: PrevisaoRequest, db: Session = Depends(get_db)):
    """
    Gera uma previsão de demanda sob demanda para o produto e horizonte especificados,
    salvando o registro no banco de dados.
    """
    produto = db.query(Produto).filter(Produto.id_produto == dados.id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    vendas = db.query(Venda).filter(Venda.id_produto == dados.id_produto).all()

    resultado = prever_demanda_produto(
        produto=produto,
        vendas_raw=vendas,
        horizonte_dias=dados.horizonte_dias,
        considerar_promocao=dados.considerar_promocao
    )

    # Persiste a previsão gerada na entidade PREVISAO
    nova_prev = Previsao(
        id_produto=produto.id_produto,
        periodo=resultado.resumo.periodo,
        horizonte_dias=dados.horizonte_dias,
        demanda_prevista=resultado.resumo.demanda_prevista,
        metodo=resultado.resumo.metodo,
        confianca=resultado.resumo.confianca,
        sugestao_reposicao=resultado.resumo.sugestao_reposicao,
        status_risco=resultado.resumo.status_risco
    )
    db.add(nova_prev)
    db.commit()
    db.refresh(nova_prev)

    resultado.resumo.id_previsao = nova_prev.id_previsao
    return resultado


@router.get("/historico", response_model=List[PrevisaoResponse])
def listar_historico_previsoes(
    id_produto: Optional[int] = Query(None),
    limite: int = Query(50, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Previsao, Produto.nome, Produto.categoria, Produto.estoque_atual).join(
        Produto, Previsao.id_produto == Produto.id_produto
    )

    if id_produto:
        query = query.filter(Previsao.id_produto == id_produto)

    registros = query.order_by(Previsao.data_geracao.desc()).limit(limite).all()

    resultado: List[PrevisaoResponse] = []
    for prev, nome_prod, cat_prod, est_atual in registros:
        resultado.append(
            PrevisaoResponse(
                id_previsao=prev.id_previsao,
                id_produto=prev.id_produto,
                nome_produto=nome_prod,
                categoria=cat_prod,
                periodo=prev.periodo,
                horizonte_dias=prev.horizonte_dias,
                demanda_prevista=prev.demanda_prevista,
                estoque_atual=est_atual,
                sugestao_reposicao=prev.sugestao_reposicao,
                status_risco=prev.status_risco,
                metodo=prev.metodo,
                confianca=prev.confianca,
                data_geracao=prev.data_geracao
            )
        )

    return resultado


@router.get("/{id_produto}", response_model=PrevisaoDetalhadaResponse)
def obter_previsao_produto(
    id_produto: int,
    horizonte_dias: int = Query(15, ge=7, le=90),
    considerar_promocao: bool = Query(False),
    db: Session = Depends(get_db)
):
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    vendas = db.query(Venda).filter(Venda.id_produto == id_produto).all()

    return prever_demanda_produto(
        produto=produto,
        vendas_raw=vendas,
        horizonte_dias=horizonte_dias,
        considerar_promocao=considerar_promocao
    )

