"""
backend/app/models/produto.py
Entidade Produto no banco de dados.
"""

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Produto(Base):
    __tablename__ = "produtos"

    id_produto = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nome = Column(String(150), nullable=False, index=True)
    categoria = Column(String(80), nullable=False, index=True)
    preco_base = Column(Float, nullable=False, default=0.0)
    estoque_atual = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=10)
    lead_time_dias = Column(Integer, nullable=False, default=3)

    # Relacionamentos
    vendas = relationship("Venda", back_populates="produto", cascade="all, delete-orphan")
    previsoes = relationship("Previsao", back_populates="produto", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Produto(id={self.id_produto}, nome='{self.nome}', categoria='{self.categoria}')>"

