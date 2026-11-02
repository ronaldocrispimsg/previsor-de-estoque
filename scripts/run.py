#!/usr/bin/env python3
"""
scripts/run.py
Inicia o servidor web do Previsor de Estoque (FastAPI + Interface Web).
Seleciona automaticamente uma porta livre caso a padrão esteja ocupada.
"""

import os
import socket
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import uvicorn


def porta_em_uso(porta: int, host: str = "0.0.0.0") -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, porta))
            return False
        except OSError:
            return True


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    porta_desejada = int(os.getenv("PORT", 8000))

    if porta_em_uso(porta_desejada, host):
        for p in [8080, 8001, 8081, 5000]:
            if not porta_em_uso(p, host):
                porta_desejada = p
                break

    print("\n" + "=" * 62)
    print("PREVISOR DE ESTOQUE - SISTEMA DE PREVISAO DE DEMANDA")
    print("=" * 62)
    print(f"Interface Web & Dashboard: http://localhost:{porta_desejada}")
    print(f"Documentacao Interativa (Swagger): http://localhost:{porta_desejada}/docs")
    print(f"Documentacao ReDoc: http://localhost:{porta_desejada}/redoc")
    print(f"Credenciais Padrao: admin@admin.com / admin")
    print(f"Preenchimento Automatico: python3 scripts/popular_dados.py")
    print("=" * 62 + "\n")

    uvicorn.run("backend.app.main:app", host=host, port=porta_desejada, reload=False)
