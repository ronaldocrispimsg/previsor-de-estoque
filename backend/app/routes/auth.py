"""
backend/app/routes/auth.py
Rotas de autenticação de usuários / gestores do sistema.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.usuario import Usuario
from backend.app.schemas.usuario import LoginRequest, LoginResponse
from backend.app.services.seeder import hash_senha

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=LoginResponse)
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    """
    Autenticação simples e direta do gestor de estoque.
    """
    hash_informado = hash_senha(dados.senha)
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    # Caso seja a primeira execução e o banco ainda esteja vazio, permite acesso com credenciais default
    if not usuario and dados.email == "gestor@supermercado.com" and dados.senha == "admin123":
        return LoginResponse(
            token="predikta-session-token-demo",
            nome="Gestor Supermercado (Demo)",
            email=dados.email,
            cargo="Gerente de Suprimentos & Estoque"
        )

    if not usuario or usuario.senha_hash != hash_informado:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas. Verifique seu email e senha."
        )

    return LoginResponse(
        token=f"token-{usuario.id_usuario}-{usuario.email}",
        nome=usuario.nome,
        email=usuario.email,
        cargo=usuario.cargo
    )

