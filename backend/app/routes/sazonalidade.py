"""
backend/app/routes/sazonalidade.py
Rotas RESTful para análise de padrões sazonais e datas comemorativas do varejo alimentar.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.schemas.dashboard import SazonalidadeEvento
from backend.app.services.forecasting import EVENTOS_SAZONAIS, prever_demanda_produto

router = APIRouter(prefix="/sazonalidade", tags=["Sazonalidade"])


@router.get("", response_model=List[SazonalidadeEvento])
def listar_eventos_sazonais(db: Session = Depends(get_db)):
    """
    Retorna os eventos sazonais mapeados no sistema e os produtos do supermercado
    impactados por cada período festivo.
    """
    produtos = db.query(Produto).all()
    resultado: List[SazonalidadeEvento] = []

    for chave, evento in EVENTOS_SAZONAIS.items():
        produtos_impactados = []

        for p in produtos:
            # Verifica se o produto pertence a alguma das categorias impactadas
            eh_impactado = any(
                cat.lower() in p.categoria.lower() or p.categoria.lower() in cat.lower()
                for cat in evento["categorias"]
            )
            if eh_impactado:
                vendas = db.query(Venda).filter(Venda.id_produto == p.id_produto).all()
                previsao = prever_demanda_produto(p, vendas, horizonte_dias=30)

                demanda_normal = round(previsao.resumo.demanda_prevista / evento["multiplicador"], 1)
                demanda_sazonal = round(previsao.resumo.demanda_prevista, 1)

                produtos_impactados.append({
                    "id_produto": p.id_produto,
                    "nome": p.nome,
                    "categoria": p.categoria,
                    "estoque_atual": p.estoque_atual,
                    "demanda_normal_30d": demanda_normal,
                    "demanda_pico_sazonal_30d": demanda_sazonal,
                    "salto_demanda_pct": round((evento["multiplicador"] - 1.0) * 100, 0),
                    "risco_sem_previsao": "Ruptura Severa" if p.estoque_atual < demanda_sazonal else "Estoque Adequado",
                    "compra_recomendada": max(0, int(demanda_sazonal - p.estoque_atual))
                })

        resultado.append(
            SazonalidadeEvento(
                id_evento=chave,
                nome=evento["nome"],
                periodo=f"Meses {', '.join(str(m) for m in evento['meses'])}",
                meses_afetados=evento["meses"],
                descricao=evento["descricao"],
                exemplo_produtos=evento["categorias"],
                multiplicador_medio=evento["multiplicador"],
                produtos_impactados=produtos_impactados
            )
        )

    return resultado
