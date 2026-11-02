"""
backend/app/services/data_cleaner.py
Módulo de tratamento, higienização e agregação de dados de vendas de supermercado.
"""

from datetime import date, timedelta
from typing import Dict, List, Tuple


def tratar_e_agregar_vendas_diarias(vendas_raw: List) -> Dict[date, int]:
    """
    Higieniza e agrega as vendas diárias de um produto.
    - Remove registros com quantidades <= 0 ou datas nulas.
    - Agrega múltiplas vendas do mesmo dia na soma total diária.
    """
    vendas_por_dia: Dict[date, int] = {}

    for v in vendas_raw:
        if v.quantidade <= 0 or v.data is None:
            continue
        vendas_por_dia[v.data] = vendas_por_dia.get(v.data, 0) + v.quantidade

    return vendas_por_dia


def preencher_dias_ausentes(
    vendas_por_dia: Dict[date, int],
    data_inicio: date,
    data_fim: date
) -> List[Tuple[date, int]]:
    """
    Imputa zero para dias sem registro de venda no intervalo cronológico,
    evitando que séries temporais fiquem com buracos de amostragem.
    """
    serie_completa: List[Tuple[date, int]] = []
    dia_atual = data_inicio

    while dia_atual <= data_fim:
        qtd = vendas_por_dia.get(dia_atual, 0)
        serie_completa.append((dia_atual, qtd))
        dia_atual += timedelta(days=1)

    return serie_completa
