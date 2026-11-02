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
    Autenticação do gestor de estoque.
    Usuário padrão: admin (admin@admin.com / admin)
    """
    hash_informado = hash_senha(dados.senha)
    usuario = db.query(Usuario).filter(Usuario.email == dados.email).first()

    # Fallback caso o banco tenha sido recriado em tempo de execução
    if not usuario and dados.email == "admin@admin.com" and dados.senha == "admin":
        return LoginResponse(
            token="sessao-token-admin",
            nome="admin",
            email="admin@admin.com",
            cargo="Administrador de Estoque"
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
