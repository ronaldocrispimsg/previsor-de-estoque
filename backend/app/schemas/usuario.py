"""
backend/app/schemas/usuario.py
Contratos de dados Pydantic para Autenticação e Usuário.
"""

from typing import Optional
from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    senha: str


class LoginResponse(BaseModel):
    token: str
    nome: str
    email: str
    cargo: str


class UsuarioResponse(BaseModel):
    id_usuario: int
    nome: str
    email: str
    cargo: str
