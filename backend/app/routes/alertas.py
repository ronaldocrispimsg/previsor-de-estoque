"""
backend/app/routes/alertas.py
Rotas RESTful para consulta e resolução de alertas de estoque.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.produto import Produto
from backend.app.schemas.dashboard import AlertaEstoque
from backend.app.services.alert_service import gerar_alertas_estoque

router = APIRouter(prefix="/alertas", tags=["Alertas de Estoque"])


class ReposicaoRequest(BaseModel):
    quantidade: int


@router.get("", response_model=List[AlertaEstoque])
def obter_alertas(
    horizonte_dias: int = Query(15, ge=7, le=60),
    db: Session = Depends(get_db)
):
    return gerar_alertas_estoque(db, horizonte_dias=horizonte_dias)


@router.post("/repor-estoque/{id_produto}")
def repor_estoque(id_produto: int, dados: ReposicaoRequest, db: Session = Depends(get_db)):
    """
    Simula a execução de um pedido de compras/reposição para um produto com alerta.
    """
    produto = db.query(Produto).filter(Produto.id_produto == id_produto).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    produto.estoque_atual += dados.quantidade
    db.commit()
    db.refresh(produto)

    return {
        "status": "sucesso",
        "mensagem": f"Estoque do produto '{produto.nome}' atualizado com sucesso.",
        "novo_estoque": produto.estoque_atual
    }

