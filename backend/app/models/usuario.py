"""
backend/app/models/usuario.py
Entidade Usuário/Gestor do sistema.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from backend.app.database import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    senha_hash = Column(String(200), nullable=False)
    cargo = Column(String(60), nullable=False, default="Gestor de Estoque")
    criado_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Usuario(id={self.id_usuario}, email='{self.email}')>"
