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
from backend.app.schemas.dashboard import MesIndiceSazonal, SazonalidadeEvento
from backend.app.services.forecasting import EVENTOS_SAZONAIS, prever_demanda_produto

router = APIRouter(prefix="/sazonalidade", tags=["Sazonalidade"])

NOMES_MESES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]


@router.get("", response_model=List[SazonalidadeEvento])
def listar_eventos_sazonais(db: Session = Depends(get_db)):
    """
    Retorna os eventos sazonais com a curva comparativa de 12 meses e
    produtos impactados no supermercado.
    """
    produtos = db.query(Produto).all()
    resultado: List[SazonalidadeEvento] = []

    for chave, evento in EVENTOS_SAZONAIS.items():
        produtos_impactados = []
        impacto_financeiro_acumulado = 0.0

        for p in produtos:
            eh_impactado = any(
                cat.lower() in p.categoria.lower() or p.categoria.lower() in cat.lower()
                for cat in evento["categorias"]
            )
            if eh_impactado:
                vendas = db.query(Venda).filter(Venda.id_produto == p.id_produto).all()
                previsao = prever_demanda_produto(p, vendas, horizonte_dias=30)

                demanda_normal = round(previsao.resumo.demanda_prevista / evento["multiplicador"], 1)
                demanda_sazonal = round(previsao.resumo.demanda_prevista, 1)

                falta_potencial = max(0, int(demanda_sazonal - p.estoque_atual))
                perda_financeira = round(falta_potencial * p.preco_base, 2)
                impacto_financeiro_acumulado += perda_financeira

                produtos_impactados.append({
                    "id_produto": p.id_produto,
                    "nome": p.nome,
                    "categoria": p.categoria,
                    "preco_base": p.preco_base,
                    "estoque_atual": p.estoque_atual,
                    "demanda_normal_30d": demanda_normal,
                    "demanda_pico_sazonal_30d": demanda_sazonal,
                    "salto_demanda_pct": round((evento["multiplicador"] - 1.0) * 100, 0),
                    "risco_sem_previsao": "Ruptura Severa" if p.estoque_atual < demanda_sazonal else "Estoque Adequado",
                    "compra_recomendada": falta_potencial,
                    "impacto_financeiro": perda_financeira
                })

        # Constrói a curva anual de 12 meses para o gráfico comparativo
        curva_meses = []
        indices_brutos = evento.get("curva_anual", [1.0] * 12)
        for i, idx_val in enumerate(indices_brutos):
            mes_num = i + 1
            curva_meses.append(
                MesIndiceSazonal(
                    mes_nome=NOMES_MESES[i],
                    indice=round(idx_val, 2),
                    destaque=(mes_num in evento["meses"])
                )
            )

        resultado.append(
            SazonalidadeEvento(
                id_evento=chave,
                nome=evento["nome"],
                periodo=f"Meses {', '.join(NOMES_MESES[m - 1] for m in evento['meses'])}",
                meses_afetados=evento["meses"],
                descricao=evento["descricao"],
                exemplo_produtos=evento["categorias"],
                multiplicador_medio=evento["multiplicador"],
                impacto_financeiro_potencial=round(impacto_financeiro_acumulado, 2),
                curva_anual_indices=curva_meses,
                produtos_impactados=produtos_impactados
            )
        )

    return resultado
