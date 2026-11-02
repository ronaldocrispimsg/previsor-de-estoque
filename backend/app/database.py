"""
backend/app/database.py
Gerenciamento de conexões e sessões de banco de dados SQLAlchemy.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.config import DATABASE_URL

# Configuração para SQLite (check_same_thread=False)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Gerador de sessão de banco de dados para injeção de dependência nas rotas."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

