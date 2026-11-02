"""
backend/app/routes/produtos.py
Rotas RESTful para gerenciamento de Produtos e Estoque de Supermercado.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.schemas.produto import (
    ProdutoAjusteEstoque,
    ProdutoCreate,
    ProdutoListResponse,
    ProdutoResponse,
    ProdutoUpdate,
)
from backend.app.services.forecasting import prever_demanda_produto

router = APIRouter(prefix="/produtos", tags=["Produtos"])


def _determinar_status_estoque(p: Produto) -> str:
    if p.estoque_atual <= 0:
        return "RUPTURA"
    if p.estoque_atual < p.estoque_minimo:
        return "ATENCAO"
    if p.estoque_atual > (p.estoque_minimo * 6) and p.estoque_atual > 50:
        return "EXCESSO"
    return "EQUILIBRADO"


@router.get("", response_model=ProdutoListResponse)
def listar_produtos(
    categoria: Optional[str] = Query(None, description="Filtrar por categoria"),
    busca: Optional[str] = Query(None, description="Buscar por nome"),
    status_filtro: Optional[str] = Query(None, description="Filtrar por status de estoque"),
    db: Session = Depends(get_db)
):
    query = db.query(Produto)

    if categoria:
        query = query.filter(Produto.categoria == categoria)

    if busca:
        query = query.filter(Produto.nome.ilike(f"%{busca}%"))

    produtos_db = query.order_by(Produto.nome).all()

    resultado: List[ProdutoResponse] = []
    for p in produtos_db:
        st = _determinar_status_estoque(p)
        if status_filtro and st != status_filtro:
            continue

        # Calcula estimativa rápida de giro diário e ponto de pedido
        vendas = db.query(Venda).filter(Venda.id_produto == p.id_produto).limit(60).all()
        giro_dia = 5.0
        ponto_ped = round(5.0 * p.lead_time_dias + p.estoque_minimo, 1)

        if vendas:
            total_qtd = sum(v.quantidade for v in vendas)
            giro_dia = round(total_qtd / max(1, len(set(v.data for v in vendas))), 1)
            ponto_ped = round(giro_dia * p.lead_time_dias + p.estoque_minimo, 1)

        resp = ProdutoResponse(
            id_produto=p.id_produto,
            nome=p.nome,
            categoria=p.categoria,
            preco_base=p.preco_base,
            estoque_atual=p.estoque_atual,
            estoque_minimo=p.estoque_minimo,
            lead_time_dias=p.lead_time_dias,
            status_estoque=st,
            ponto_de_pedido=ponto_ped,
            giro_diario_estimado=giro_dia
        )
        resultado.append(resp)

    return ProdutoListResponse(total=len(resultado), produtos=resultado)


@router.get("/categorias", response_model=List[str])
def listar_categorias(db: Session = Depends(get_db)):
    categorias = db.query(Produto.categoria).distinct().all()
    return [c[0] for c in categorias if c[0]]


@router.get("/{id_produto}", response_model=ProdutoResponse)
def obter_produto(id_produto: int, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    return ProdutoResponse(
        id_produto=p.id_produto,
        nome=p.nome,
        categoria=p.categoria,
        preco_base=p.preco_base,
        estoque_atual=p.estoque_atual,
        estoque_minimo=p.estoque_minimo,
        lead_time_dias=p.lead_time_dias,
        status_estoque=_determinar_status_estoque(p)
    )


@router.post("", response_model=ProdutoResponse, status_code=status.HTTP_201_CREATED)
def criar_produto(dados: ProdutoCreate, db: Session = Depends(get_db)):
    p = Produto(
        nome=dados.nome,
        categoria=dados.categoria,
        preco_base=dados.preco_base,
        estoque_atual=dados.estoque_atual,
        estoque_minimo=dados.estoque_minimo,
        lead_time_dias=dados.lead_time_dias
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    return ProdutoResponse(
        id_produto=p.id_produto,
        nome=p.nome,
        categoria=p.categoria,
        preco_base=p.preco_base,
        estoque_atual=p.estoque_atual,
        estoque_minimo=p.estoque_minimo,
        lead_time_dias=p.lead_time_dias,
        status_estoque=_determinar_status_estoque(p)
    )


@router.put("/{id_produto}", response_model=ProdutoResponse)
def atualizar_produto(id_produto: int, dados: ProdutoUpdate, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if dados.nome is not None:
        p.nome = dados.nome
    if dados.categoria is not None:
        p.categoria = dados.categoria
    if dados.preco_base is not None:
        p.preco_base = dados.preco_base
    if dados.estoque_atual is not None:
        p.estoque_atual = dados.estoque_atual
    if dados.estoque_minimo is not None:
        p.estoque_minimo = dados.estoque_minimo
    if dados.lead_time_dias is not None:
        p.lead_time_dias = dados.lead_time_dias

    db.commit()
    db.refresh(p)

    return ProdutoResponse(
        id_produto=p.id_produto,
        nome=p.nome,
        categoria=p.categoria,
        preco_base=p.preco_base,
        estoque_atual=p.estoque_atual,
        estoque_minimo=p.estoque_minimo,
        lead_time_dias=p.lead_time_dias,
        status_estoque=_determinar_status_estoque(p)
    )


@router.post("/{id_produto}/ajuste-estoque", response_model=ProdutoResponse)
def ajustar_estoque(id_produto: int, dados: ProdutoAjusteEstoque, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    novo_estoque = max(0, p.estoque_atual + dados.quantidade)
    p.estoque_atual = novo_estoque
    db.commit()
    db.refresh(p)

    return ProdutoResponse(
        id_produto=p.id_produto,
        nome=p.nome,
        categoria=p.categoria,
        preco_base=p.preco_base,
        estoque_atual=p.estoque_atual,
        estoque_minimo=p.estoque_minimo,
        lead_time_dias=p.lead_time_dias,
        status_estoque=_determinar_status_estoque(p)
    )


@router.delete("/{id_produto}", status_code=status.HTTP_204_NO_CONTENT)
def remover_produto(id_produto: int, db: Session = Depends(get_db)):
    p = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not p:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    db.delete(p)
    db.commit()
    return None
