"""
tests/conftest.py
Fixtures de teste para a suíte automatizada do Predikta Data Solutions.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.app.database import Base, get_db
from backend.app.models import Produto, Venda, Previsao, Usuario
from backend.app.main import app
from backend.app.services.seeder import popular_dados_iniciais


@pytest.fixture(scope="function")
def db_session():
    # StaticPool garante que todas as conexões acessem a mesma instância do banco em memória
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()

    popular_dados_iniciais(session, force=True)

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
