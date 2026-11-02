"""
tests/test_api.py
Validação dos endpoints da API RESTful do Predikta Data Solutions.
"""

import io


def test_healthcheck(client):
    res = client.get("/healthz")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_login_demo(client):
    res = client.post("/api/auth/login", json={
        "email": "gestor@supermercado.com",
        "senha": "admin123"
    })
    assert res.status_code == 200
    dados = res.json()
    assert "token" in dados
    assert dados["email"] == "gestor@supermercado.com"


def test_listar_produtos(client):
    res = client.get("/api/produtos")
    assert res.status_code == 200
    dados = res.json()
    assert "total" in dados
    assert dados["total"] > 0
    assert len(dados["produtos"]) > 0
    primeiro = dados["produtos"][0]
    assert "ponto_de_pedido" in primeiro
    assert "giro_diario_estimado" in primeiro


def test_criar_e_consultar_produto(client):
    novo_prod = {
        "nome": "Produto Teste API 1kg",
        "categoria": "Mercearia",
        "preco_base": 15.99,
        "estoque_atual": 30,
        "estoque_minimo": 10,
        "lead_time_dias": 3
    }
    res = client.post("/api/produtos", json=novo_prod)
    assert res.status_code == 201
    criado = res.json()
    assert criado["id_produto"] is not None
    assert criado["nome"] == novo_prod["nome"]

    # Consulta por ID
    res_get = client.get(f"/api/produtos/{criado['id_produto']}")
    assert res_get.status_code == 200
    assert res_get.json()["nome"] == novo_prod["nome"]


def test_ajuste_rapido_estoque(client):
    prods = client.get("/api/produtos").json()["produtos"]
    prod = prods[0]
    est_anterior = prod["estoque_atual"]

    res = client.post(f"/api/produtos/{prod['id_produto']}/ajuste-estoque", json={
        "quantidade": 25,
        "motivo": "Entrada Fornecedor"
    })
    assert res.status_code == 200
    assert res.json()["estoque_atual"] == est_anterior + 25


def test_dashboard_stats(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_produtos"] > 0
    assert stats["reducao_estimada_perdas_pct"] == 18.0
    assert stats["acuracia_media_modelo"] > 50.0
    assert "produtos_em_alta" in stats
    assert "alertas_urgentes" in stats


def test_eventos_sazonalidade(client):
    res = client.get("/api/sazonalidade")
    assert res.status_code == 200
    eventos = res.json()
    assert len(eventos) >= 4
    chaves = [e["id_evento"] for e in eventos]
    assert "pascoa" in chaves
    assert "natal" in chaves
    assert "festa_junina" in chaves
    assert len(eventos[0]["curva_anual_indices"]) == 12


def test_alertas_estoque(client):
    res = client.get("/api/alertas")
    assert res.status_code == 200
    alertas = res.json()
    assert isinstance(alertas, list)
    if alertas:
        assert "impacto_financeiro_estimado" in alertas[0]


def test_gerar_previsao_api(client):
    prods = client.get("/api/produtos").json()["produtos"]
    id_alvo = prods[0]["id_produto"]

    res = client.post("/api/previsoes/gerar", json={
        "id_produto": id_alvo,
        "horizonte_dias": 15,
        "considerar_promocao": False
    })
    assert res.status_code == 200
    prev = res.json()
    assert prev["resumo"]["id_produto"] == id_alvo
    assert prev["resumo"]["demanda_prevista"] > 0
    assert "metricas" in prev
    assert "decomposicao" in prev
    assert prev["decomposicao"]["ponto_de_pedido"] > 0
    assert "serie_temporal" in prev


def test_upload_csv_vendas_e_template(client):
    # Teste de download de template
    res_tpl = client.get("/api/vendas/template-csv")
    assert res_tpl.status_code == 200
    assert "id_produto;data;quantidade;preco;promocao" in res_tpl.text

    # Teste de upload de CSV higienizado
    prods = client.get("/api/produtos").json()["produtos"]
    id_prod = prods[0]["id_produto"]

    csv_conteudo = f"id_produto;data;quantidade;preco;promocao\n{id_prod};2026-04-10;50;10.50;1\n{id_prod};data_invalida;-5;0;0\n"
    csv_file = io.BytesIO(csv_conteudo.encode("utf-8"))

    res_upload = client.post(
        "/api/vendas/upload-csv",
        files={"arquivo": ("vendas_teste.csv", csv_file, "text/csv")}
    )
    assert res_upload.status_code == 200
    resp_dados = res_upload.json()
    assert resp_dados["linhas_inseridas"] == 1
    assert resp_dados["linhas_descartadas"] == 1
