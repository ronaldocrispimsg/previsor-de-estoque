"""
backend/app/services/data_cleaner.py
Módulo de tratamento, higienização, validação e agregação de dados de vendas de supermercado.
"""

import csv
import io
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple


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


def parse_data_flexivel(data_str: str) -> Optional[date]:
    """
    Trata múltiplos formatos comuns de data em supermercados:
    YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY.
    """
    data_str = data_str.strip()
    formatos = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]

    for fmt in formatos:
        try:
            return datetime.strptime(data_str, fmt).date()
        except ValueError:
            continue
    return None


def processar_csv_vendas(conteudo_csv: str) -> Dict[str, any]:
    """
    Valida e converte CSV de histórico de vendas eliminando dados inconsistentes.
    Retorna linhas válidas e contagem de erros descartados.
    """
    f = io.StringIO(conteudo_csv)
    # Detecta se é separado por vírgula ou ponto-e-vírgula
    primeira_linha = f.readline()
    f.seek(0)
    delimitador = ';' if ';' in primeira_linha else ','

    reader = csv.DictReader(f, delimiter=delimitador)

    linhas_validas = []
    linhas_invalidas = 0
    motivos_descarte = []

    for idx, row in enumerate(reader, start=2):
        # Mapeamento flexível de nomes de colunas
        id_prod = row.get("id_produto") or row.get("produto_id") or row.get("id")
        dt_str = row.get("data") or row.get("data_venda") or row.get("dt")
        qtd_str = row.get("quantidade") or row.get("qtd")
        preco_str = row.get("preco") or row.get("preco_unitario") or row.get("valor")
        promo_str = row.get("promocao") or row.get("promo") or "0"

        if not id_prod or not dt_str or not qtd_str or not preco_str:
            linhas_invalidas += 1
            motivos_descarte.append(f"Linha {idx}: campos obrigatórios ausentes")
            continue

        try:
            id_produto = int(id_prod.strip())
            dt = parse_data_flexivel(dt_str)
            if not dt:
                linhas_invalidas += 1
                motivos_descarte.append(f"Linha {idx}: formato de data inválido ({dt_str})")
                continue

            qtd = int(float(qtd_str.strip()))
            if qtd <= 0:
                linhas_invalidas += 1
                motivos_descarte.append(f"Linha {idx}: quantidade negativa ou zero ({qtd})")
                continue

            preco = float(preco_str.strip().replace("R$", "").replace(",", "."))
            if preco <= 0:
                linhas_invalidas += 1
                motivos_descarte.append(f"Linha {idx}: preço zero ou negativo")
                continue

            promo = str(promo_str).strip().lower() in ["1", "true", "sim", "s", "verdadeiro"]

            linhas_validas.append({
                "id_produto": id_produto,
                "data": dt,
                "quantidade": qtd,
                "preco": preco,
                "promocao": promo
            })
        except Exception as e:
            linhas_invalidas += 1
            motivos_descarte.append(f"Linha {idx}: erro de conversão ({str(e)})")

    return {
        "validas": linhas_validas,
        "total_linhas_processadas": len(linhas_validas) + linhas_invalidas,
        "total_validas": len(linhas_validas),
        "total_invalidas": linhas_invalidas,
        "amostra_motivos": motivos_descarte[:5]
    }


def gerar_template_csv() -> str:
    """
    Gera conteúdo CSV modelo para importação de vendas de supermercado.
    """
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow(["id_produto", "data", "quantidade", "preco", "promocao"])
    writer.writerow([1, "2026-03-25", 15, "42.90", "0"])
    writer.writerow([1, "2026-03-26", 28, "38.90", "1"])
    writer.writerow([2, "2026-03-25", 35, "14.50", "0"])
    writer.writerow([3, "2026-03-25", 40, "7.99", "0"])
    return output.getvalue()
