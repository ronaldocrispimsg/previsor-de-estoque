"""
backend/app/config.py
Configurações da aplicação Predikta Data Solutions.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DB_DIR = BASE_DIR / "data"
DB_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_DIR}/predikta.db")
SECRET_KEY = os.getenv("SECRET_KEY", "predikta-secret-supermarket-key-2026")
PROJECT_NAME = "Predikta Data Solutions"
PROJECT_DESCRIPTION = "Solução de Previsão de Demanda e Apoio à Gestão de Estoque para Supermercados"
API_V1_STR = "/api"

