"""
backend/app/models/previsao.py
Entidade Previsão no banco de dados.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Previsao(Base):
    __tablename__ = "previsoes"

    id_previsao = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_produto = Column(Integer, ForeignKey("produtos.id_produto", ondelete="CASCADE"), nullable=False, index=True)
    periodo = Column(String(80), nullable=False)
    horizonte_dias = Column(Integer, nullable=False, default=15)
    demanda_prevista = Column(Float, nullable=False)
    data_geracao = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    metodo = Column(String(80), nullable=False, default="Decomposição Sazonal Ponderada")
    confianca = Column(Float, nullable=False, default=90.0)
    sugestao_reposicao = Column(Float, nullable=False, default=0.0)
    status_risco = Column(String(30), nullable=False, default="EQUILIBRADO")

    # Relacionamento inverso
    produto = relationship("Produto", back_populates="previsoes")

    def __repr__(self):
        return f"<Previsao(id={self.id_previsao}, prod_id={self.id_produto}, demanda={self.demanda_prevista})>"
