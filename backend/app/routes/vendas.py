"""
backend/app/routes/vendas.py
Rotas RESTful para gerenciamento de Histórico e Registro de Vendas.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.schemas.venda import VendaCreate, VendaImportBatch, VendaResponse

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.get("", response_model=List[VendaResponse])
def listar_vendas(
    id_produto: Optional[int] = Query(None, description="Filtrar por ID do produto"),
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final"),
    limite: int = Query(100, le=500, description="Limite de registros"),
    db: Session = Depends(get_db)
):
    query = db.query(Venda, Produto.nome, Produto.categoria).join(Produto, Venda.id_produto == Produto.id_produto)

    if id_produto:
        query = query.filter(Venda.id_produto == id_produto)
    if data_inicio:
        query = query.filter(Venda.data >= data_inicio)
    if data_fim:
        query = query.filter(Venda.data <= data_fim)

    registros = query.order_by(Venda.data.desc()).limit(limite).all()

    resultado: List[VendaResponse] = []
    for venda, nome_prod, cat_prod in registros:
        resultado.append(
            VendaResponse(
                id_venda=venda.id_venda,
                id_produto=venda.id_produto,
                nome_produto=nome_prod,
                categoria_produto=cat_prod,
                data=venda.data,
                quantidade=venda.quantidade,
                preco=venda.preco,
                promocao=venda.promocao
            )
        )

    return resultado


@router.post("", response_model=VendaResponse, status_code=status.HTTP_201_CREATED)
def registrar_venda(dados: VendaCreate, db: Session = Depends(get_db)):
    produto = db.query(Produto).filter(Produto.id_produto == dados.id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Atualiza o estoque do produto decrementando a quantidade vendida
    produto.estoque_atual = max(0, produto.estoque_atual - dados.quantidade)

    venda = Venda(
        id_produto=dados.id_produto,
        data=dados.data,
        quantidade=dados.quantidade,
        preco=dados.preco,
        promocao=dados.promocao
    )
    db.add(venda)
    db.commit()
    db.refresh(venda)

    return VendaResponse(
        id_venda=venda.id_venda,
        id_produto=venda.id_produto,
        nome_produto=produto.nome,
        categoria_produto=produto.categoria,
        data=venda.data,
        quantidade=venda.quantidade,
        preco=venda.preco,
        promocao=venda.promocao
    )


@router.post("/importar-lote")
def importar_vendas_lote(lote: VendaImportBatch, db: Session = Depends(get_db)):
    """
    Importa um lote de registros históricos de vendas (ingestão de dados).
    """
    produtos_ids = {p.id_produto for p in db.query(Produto.id_produto).all()}
    vendas_inseridas = 0

    for item in lote.vendas:
        if item.id_produto in produtos_ids:
            v = Venda(
                id_produto=item.id_produto,
                data=item.data,
                quantidade=item.quantidade,
                preco=item.preco,
                promocao=item.promocao
            )
            db.add(v)
            vendas_inseridas += 1

    db.commit()
    return {"status": "sucesso", "total_importado": vendas_inseridas}
