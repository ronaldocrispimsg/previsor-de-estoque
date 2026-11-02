"""
backend/app/main.py
Ponto de entrada principal da aplicação Predikta Data Solutions.
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.config import PROJECT_DESCRIPTION, PROJECT_NAME
from backend.app.database import Base, SessionLocal, engine
from backend.app.models import *  # Carrega todas as tabelas
from backend.app.routes import alertas, auth, dashboard, previsoes, produtos, sazonalidade, seed, vendas
from backend.app.services.seeder import popular_dados_iniciais

BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria todas as tabelas no banco de dados se não existirem
    Base.metadata.create_all(bind=engine)

    # Popula dados iniciais de demonstração se o banco estiver vazio
    db = SessionLocal()
    try:
        popular_dados_iniciais(db, force=False)
    finally:
        db.close()

    yield


app = FastAPI(
    title=PROJECT_NAME,
    description=PROJECT_DESCRIPTION,
    version="1.0.0",
    lifespan=lifespan
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro dos Roteadores REST API
app.include_router(auth.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(produtos.router, prefix="/api")
app.include_router(vendas.router, prefix="/api")
app.include_router(previsoes.router, prefix="/api")
app.include_router(sazonalidade.router, prefix="/api")
app.include_router(alertas.router, prefix="/api")
app.include_router(seed.router, prefix="/api")

# Montagem dos arquivos estáticos do frontend
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    def index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/healthz")
def healthcheck():
    return {"status": "ok", "app": PROJECT_NAME, "version": "1.0.0"}
