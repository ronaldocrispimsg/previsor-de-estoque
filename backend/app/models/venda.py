"""
backend/app/models/venda.py
Entidade Venda no banco de dados.
"""

from sqlalchemy import Column, Integer, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Venda(Base):
    __tablename__ = "vendas"

    id_venda = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_produto = Column(Integer, ForeignKey("produtos.id_produto", ondelete="CASCADE"), nullable=False, index=True)
    data = Column(Date, nullable=False, index=True)
    quantidade = Column(Integer, nullable=False, default=1)
    preco = Column(Float, nullable=False)
    promocao = Column(Boolean, nullable=False, default=False)

    # Relacionamento inverso
    produto = relationship("Produto", back_populates="vendas")

    def __repr__(self):
        return f"<Venda(id={self.id_venda}, prod_id={self.id_produto}, data={self.data}, qtd={self.quantidade})>"
