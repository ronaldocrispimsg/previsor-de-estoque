#!/usr/bin/env python3
"""
scripts/run.py
Inicia o servidor web da Predikta Data Solutions (FastAPI + Interface Web).
"""

import os
import sys
from pathlib import Path

# Adiciona a raiz do projeto ao sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import uvicorn

if __name__ == "__main__":
    porta = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    print("\n" + "=" * 60)
    print("🚀 PREDIKTA DATA SOLUTIONS - SISTEMA WEB DE PREVISÃO DE DEMANDA")
    print("=" * 60)
    print(f"👉 Interface Web & Dashboard: http://localhost:{porta}")
    print(f"👉 Documentação Interativa (Swagger): http://localhost:{porta}/docs")
    print(f"👉 Documentação ReDoc: http://localhost:{porta}/redoc")
    print(f"👉 Credenciais Demo: gestor@supermercado.com / admin123")
    print("=" * 60 + "\n")

    uvicorn.run("backend.app.main:app", host=host, port=porta, reload=False)
