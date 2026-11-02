"""
backend/app/services/seeder.py
Gerador de dados realistas de supermercado para demonstração e testes do Predikta Data Solutions.
"""

import hashlib
import random
from datetime import date, datetime, timedelta, timezone
from sqlalchemy.orm import Session
from backend.app.models.produto import Produto
from backend.app.models.usuario import Usuario
from backend.app.models.venda import Venda


def hash_senha(senha: str) -> str:
    return hashlib.sha256(senha.encode("utf-8")).hexdigest()


PRODUTOS_SEMENTES = [
    # Doces e Chocolates (Pico na Páscoa)
    {"nome": "Ovo de Páscoa Crocante 250g", "categoria": "Doces e Chocolates", "preco_base": 42.90, "estoque_atual": 18, "estoque_minimo": 20, "lead_time_dias": 5, "base_diaria": 4, "fator_pascoa": 6.5},
    {"nome": "Caixa de Bombons Sortidos 250g", "categoria": "Doces e Chocolates", "preco_base": 14.50, "estoque_atual": 65, "estoque_minimo": 30, "lead_time_dias": 3, "base_diaria": 12, "fator_pascoa": 3.8},
    {"nome": "Barra de Chocolate ao Leite 90g", "categoria": "Doces e Chocolates", "preco_base": 7.99, "estoque_atual": 140, "estoque_minimo": 40, "lead_time_dias": 2, "base_diaria": 25, "fator_pascoa": 2.5},

    # Padaria e Natalinos (Pico no Natal)
    {"nome": "Panetone Tradicional de Frutas 500g", "categoria": "Padaria e Natalinos", "preco_base": 24.90, "estoque_atual": 12, "estoque_minimo": 25, "lead_time_dias": 4, "base_diaria": 3, "fator_natal": 6.0},
    {"nome": "Chocotone Gotas de Chocolate 500g", "categoria": "Padaria e Natalinos", "preco_base": 26.50, "estoque_atual": 85, "estoque_minimo": 25, "lead_time_dias": 4, "base_diaria": 4, "fator_natal": 5.5},

    # Festa Junina (Pico em Junho/Julho)
    {"nome": "Milho de Pipoca Especial 500g", "categoria": "Festa Junina", "preco_base": 5.80, "estoque_atual": 110, "estoque_minimo": 30, "lead_time_dias": 3, "base_diaria": 10, "fator_junina": 4.2},
    {"nome": "Canjica Amarela Selecionada 500g", "categoria": "Festa Junina", "preco_base": 6.20, "estoque_atual": 15, "estoque_minimo": 25, "lead_time_dias": 3, "base_diaria": 5, "fator_junina": 5.0},
    {"nome": "Amendoim Torrado com Pele 500g", "categoria": "Festa Junina", "preco_base": 9.90, "estoque_atual": 70, "estoque_minimo": 20, "lead_time_dias": 3, "base_diaria": 8, "fator_junina": 3.5},

    # Bebidas (Pico no Verão e fins de semana)
    {"nome": "Cerveja Pilsen Lata 350ml", "categoria": "Bebidas", "preco_base": 3.99, "estoque_atual": 450, "estoque_minimo": 150, "lead_time_dias": 2, "base_diaria": 60, "fator_verao": 2.2},
    {"nome": "Refrigerante Guaraná 2L", "categoria": "Bebidas", "preco_base": 8.50, "estoque_atual": 80, "estoque_minimo": 50, "lead_time_dias": 2, "base_diaria": 22, "fator_verao": 1.7},
    {"nome": "Água Mineral sem Gás 500ml", "categoria": "Bebidas", "preco_base": 2.50, "estoque_atual": 320, "estoque_minimo": 100, "lead_time_dias": 1, "base_diaria": 45, "fator_verao": 2.0},

    # Mercearia e Básicos (Giro regular)
    {"nome": "Arroz Branco Tipo 1 5kg", "categoria": "Mercearia", "preco_base": 29.90, "estoque_atual": 90, "estoque_minimo": 40, "lead_time_dias": 4, "base_diaria": 18, "fator_geral": 1.0},
    {"nome": "Feijão Carioca Tipo 1 1kg", "categoria": "Mercearia", "preco_base": 7.90, "estoque_atual": 120, "estoque_minimo": 40, "lead_time_dias": 3, "base_diaria": 20, "fator_geral": 1.0},
    {"nome": "Café Torrado e Moído Tradicional 500g", "categoria": "Mercearia", "preco_base": 18.90, "estoque_atual": 15, "estoque_minimo": 35, "lead_time_dias": 3, "base_diaria": 16, "fator_geral": 1.0},
    {"nome": "Leite Integral UHT 1L", "categoria": "Laticínios", "preco_base": 5.49, "estoque_atual": 240, "estoque_minimo": 80, "lead_time_dias": 2, "base_diaria": 50, "fator_geral": 1.0},
]


def popular_dados_iniciais(db: Session, force: bool = False):
    """
    Popula o banco com catálogo de produtos, usuário gestor e histórico de vendas.
    """
    total_produtos = db.query(Produto).count()
    if total_produtos > 0 and not force:
        return {"mensagem": "Banco de dados já contém registros.", "total_produtos": total_produtos}

    # Se force=True, limpa as tabelas existentes
    if force:
        db.query(Venda).delete()
        db.query(Produto).delete()
        db.query(Usuario).delete()
        db.commit()

    # Cria Usuário Gestor padrão
    gestor = Usuario(
        nome="Gestor Supermercado",
        email="gestor@supermercado.com",
        senha_hash=hash_senha("admin123"),
        cargo="Gerente de Suprimentos & Estoque",
        criado_em=datetime.now(timezone.utc)
    )
    db.add(gestor)
    db.flush()

    # Cria Produtos
    produtos_persistidos = []
    for item in PRODUTOS_SEMENTES:
        p = Produto(
            nome=item["nome"],
            categoria=item["categoria"],
            preco_base=item["preco_base"],
            estoque_atual=item["estoque_atual"],
            estoque_minimo=item["estoque_minimo"],
            lead_time_dias=item["lead_time_dias"]
        )
        db.add(p)
        produtos_persistidos.append((p, item))

    db.flush()

    # Gera histórico de vendas dos últimos 180 dias
    random.seed(42)
    hoje = date.today()
    total_vendas_geradas = 0

    for p, meta in produtos_persistidos:
        base_diaria = meta.get("base_diaria", 10)
        fator_pascoa = meta.get("fator_pascoa", 1.0)
        fator_natal = meta.get("fator_natal", 1.0)
        fator_junina = meta.get("fator_junina", 1.0)
        fator_verao = meta.get("fator_verao", 1.0)

        for dias_atras in range(180, 0, -1):
            data_venda = hoje - timedelta(days=dias_atras)
            mes = data_venda.month
            dia_semana = data_venda.weekday()  # 5=Sábado, 6=Domingo

            # Variação natural do fim de semana (+30% a +60%)
            multiplicador_dia = 1.4 if dia_semana in [4, 5, 6] else 1.0

            # Aplicação de fatores sazonais
            multiplicador_mes = 1.0
            if mes in [3, 4] and fator_pascoa > 1.0:
                multiplicador_mes = fator_pascoa
            elif mes in [6, 7] and fator_junina > 1.0:
                multiplicador_mes = fator_junina
            elif mes in [11, 12] and fator_natal > 1.0:
                multiplicador_mes = fator_natal
            elif mes in [12, 1, 2] and fator_verao > 1.0:
                multiplicador_mes = fator_verao

            # Probabilidade de promoção (~10% dos dias)
            em_promocao = random.random() < 0.10
            mult_promo = 1.5 if em_promocao else 1.0

            ruido = random.uniform(0.75, 1.25)
            qtd_venda = int(round(base_diaria * multiplicador_dia * multiplicador_mes * mult_promo * ruido))
            qtd_venda = max(1, qtd_venda)

            preco_venda = round(p.preco_base * (0.85 if em_promocao else 1.0), 2)

            venda = Venda(
                id_produto=p.id_produto,
                data=data_venda,
                quantidade=qtd_venda,
                preco=preco_venda,
                promocao=em_promocao
            )
            db.add(venda)
            total_vendas_geradas += 1

    db.commit()

    return {
        "status": "sucesso",
        "total_produtos": len(produtos_persistidos),
        "total_vendas": total_vendas_geradas,
        "usuario_criado": gestor.email
    }
