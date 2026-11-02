"""
backend/app/routes/seed.py
Rotas para carregar ou resetar a base de dados de demonstração.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.previsao import Previsao
from backend.app.models.produto import Produto
from backend.app.models.usuario import Usuario
from backend.app.models.venda import Venda
from backend.app.services.seeder import popular_dados_iniciais

router = APIRouter(prefix="/seed", tags=["Seed / Demonstração"])


@router.post("/popular")
def executar_seed(
    force: bool = Query(False, description="Sobrescrever dados existentes"),
    db: Session = Depends(get_db)
):
    resultado = popular_dados_iniciais(db, force=force)
    return resultado


@router.get("/status")
def status_banco(db: Session = Depends(get_db)):
    return {
        "total_produtos": db.query(Produto).count(),
        "total_vendas": db.query(Venda).count(),
        "total_previsoes": db.query(Previsao).count(),
        "total_usuarios": db.query(Usuario).count(),
    }
