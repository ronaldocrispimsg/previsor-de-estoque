"""
backend/app/routes/vendas.py
Rotas RESTful para gerenciamento de Histórico e Registro de Vendas.
Inclui importação/ingestão de arquivos CSV com higienização de inconsistências.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.produto import Produto
from backend.app.models.venda import Venda
from backend.app.schemas.venda import VendaCreate, VendaImportBatch, VendaResponse
from backend.app.services.data_cleaner import gerar_template_csv, processar_csv_vendas

router = APIRouter(prefix="/vendas", tags=["Vendas"])


@router.get("", response_model=List[VendaResponse])
def listar_vendas(
    id_produto: Optional[int] = Query(None, description="Filtrar por ID do produto"),
    data_inicio: Optional[date] = Query(None, description="Data inicial"),
    data_fim: Optional[date] = Query(None, description="Data final"),
    promocao: Optional[bool] = Query(None, description="Filtrar por vendas em promoção"),
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
    if promocao is not None:
        query = query.filter(Venda.promocao == promocao)

    registros = query.order_by(Venda.data.desc(), Venda.id_venda.desc()).limit(limite).all()

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

    # Baixa no estoque
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


@router.post("/upload-csv")
async def upload_csv_vendas(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Recebe arquivo CSV com histórico de vendas, aplica higienização de dados
    e insere em lote os registros válidos no banco de dados.
    """
    try:
        conteudo_bytes = await arquivo.read()
        conteudo_str = conteudo_bytes.decode("utf-8", errors="replace")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao ler arquivo: {str(e)}")

    resultado_processamento = processar_csv_vendas(conteudo_str)
    linhas_validas = resultado_processamento["validas"]

    produtos_existentes = {p.id_produto for p in db.query(Produto.id_produto).all()}
    vendas_inseridas = 0

    for item in linhas_validas:
        if item["id_produto"] in produtos_existentes:
            v = Venda(
                id_produto=item["id_produto"],
                data=item["data"],
                quantidade=item["quantidade"],
                preco=item["preco"],
                promocao=item["promocao"]
            )
            db.add(v)
            vendas_inseridas += 1

    db.commit()

    return {
        "status": "sucesso",
        "total_linhas_processadas": resultado_processamento["total_linhas_processadas"],
        "linhas_inseridas": vendas_inseridas,
        "linhas_descartadas": resultado_processamento["total_invalidas"],
        "amostra_motivos_descarte": resultado_processamento["amostra_motivos"]
    }


@router.get("/template-csv")
def baixar_template_csv():
    """
    Retorna o modelo de arquivo CSV para download.
    """
    csv_data = gerar_template_csv()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=modelo_vendas_predikta.csv"}
    )


@router.delete("/{id_venda}", status_code=status.HTTP_204_NO_CONTENT)
def remover_venda(id_venda: int, db: Session = Depends(get_db)):
    v = db.query(Venda).filter(Venda.id_venda == id_venda).first()
    if not v:
        raise HTTPException(status_code=404, detail="Registro de venda não encontrado")

    db.delete(v)
    db.commit()
    return None
