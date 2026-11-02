"""
tests/test_api.py
Validação dos endpoints da API RESTful do Predikta Data Solutions.
"""


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


def test_dashboard_stats(client):
    res = client.get("/api/dashboard/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_produtos"] > 0
    assert stats["reducao_estimada_perdas_pct"] == 18.0
    assert stats["acuracia_media_modelo"] > 50.0


def test_eventos_sazonalidade(client):
    res = client.get("/api/sazonalidade")
    assert res.status_code == 200
    eventos = res.json()
    assert len(eventos) >= 4
    chaves = [e["id_evento"] for e in eventos]
    assert "pascoa" in chaves
    assert "natal" in chaves
    assert "festa_junina" in chaves


def test_alertas_estoque(client):
    res = client.get("/api/alertas")
    assert res.status_code == 200
    alertas = res.json()
    assert isinstance(alertas, list)


def test_gerar_previsao_api(client):
    # Pega um produto qualquer
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
    assert "serie_temporal" in prev
