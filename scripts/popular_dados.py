#!/usr/bin/env python3
"""
scripts/popular_dados.py
Script para realizar o preenchimento automático (seeding) da base de dados sob demanda.
Preenche produtos de supermercado e histórico de vendas de 180 dias com sazonalidades.
"""

import argparse
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.app.database import Base, SessionLocal, engine
from backend.app.services.seeder import popular_dados_iniciais, garantir_usuario_admin


def main():
    parser = argparse.ArgumentParser(description="Preenchimento automático do banco de dados (Previsor de Estoque)")
    parser.add_argument("--force", action="store_true", help="Sobrescreve e recria os dados mesmo se já existirem")
    args = parser.parse_args()

    print("\n" + "=" * 62)
    print("PREVISOR DE ESTOQUE - PREENCHIMENTO AUTOMATICO DE DADOS")
    print("=" * 62)

    # Cria tabelas caso ainda não existam
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        garantir_usuario_admin(db)
        print("-> Usuario 'admin' (admin@admin.com) garantido com sucesso.")

        print("-> Populando catalogo de produtos e historico de 180 dias de vendas...")
        resultado = popular_dados_iniciais(db, force=args.force)

        if "mensagem" in resultado:
            print(f"-> {resultado['mensagem']} (Total de produtos: {resultado['total_produtos']})")
            print("   Dica: execute com a flag '--force' para recriar do zero: python3 scripts/popular_dados.py --force")
        else:
            print(f"-> Sucesso! {resultado['total_produtos']} produtos e {resultado['total_vendas']} vendas registradas.")
            print(f"-> Acesso liberado: {resultado['usuario_criado']} / senha: admin")

    except Exception as e:
        print(f"-> Erro ao popular dados: {e}")
        sys.exit(1)
    finally:
        db.close()

    print("=" * 62 + "\n")


if __name__ == "__main__":
    main()

