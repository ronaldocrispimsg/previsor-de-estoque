"""
backend/app/config.py
Configurações da aplicação Previsor de Estoque.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR}/previsor_estoque.db")
SECRET_KEY = os.getenv("SECRET_KEY", "previsor-estoque-secret-key-2026")
PROJECT_NAME = "Previsor de Estoque"
PROJECT_DESCRIPTION = "Solução de Previsão de Demanda e Apoio à Gestão de Estoque para Supermercados"
API_V1_STR = "/api"
