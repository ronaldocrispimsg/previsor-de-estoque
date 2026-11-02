# Previsor de Estoque
### Solução de Previsão de Demanda e Apoio à Gestão de Estoque para Supermercados

Sistema web corporativo voltado a pequenos e médios supermercados para substituição da gestão puramente reativa ou baseada em "feeling" por tomadas de decisão orientadas a dados e inteligência preditiva.

> Para a documentação arquitetural, matemática e operacional completa, consulte [docs/DOCUMENTACAO_TECNICA.md](docs/DOCUMENTACAO_TECNICA.md).

---

## 1. Visão Geral e Arquitetura

O sistema opera sobre o fluxo de inteligência preditiva:
$$\text{Histórico de Vendas} \longrightarrow \text{Tratamento e Higienização} \longrightarrow \text{Modelo Preditivo} \longrightarrow \text{Gestão e Alertas} \longrightarrow \text{Decisão de Compra}$$

```text
previsor-de-estoque/
├── backend/
│   └── app/
│       ├── config.py              # Parâmetros de ambiente e banco de dados
│       ├── database.py            # Engine SQLAlchemy e SessionLocal
│       ├── main.py                # Aplicação FastAPI e servidor estático
│       ├── models/                # Entidades relacionais (Produto, Venda, Previsao, Usuario)
│       ├── routes/                # Endpoints REST (auth, produtos, vendas, previsões, sazonalidade, alertas, dashboard)
│       ├── schemas/               # Contratos Pydantic com validação rigorosa
│       └── services/              # Ingestão CSV, decomposição sazonal e cálculo de métricas
├── docs/
│   └── DOCUMENTACAO_TECNICA.md    # Especificação técnica, matemática e arquitetural completa
├── frontend/                      # Interface Web responsiva (SPA corporativa)
│   ├── index.html                 # Painel unificado (Inicio, Estoque, Vendas, Previsão, Analise de Sazonalidade, Alertas)
│   ├── css/style.css              # Custom tokens, badges de status, modais e toasts
│   └── js/                        # Módulos: api, auth, dashboard, produtos, vendas, previsao, sazonalidade, alertas
├── tests/                         # Suíte de testes automatizados com pytest (15 testes)
├── scripts/
│   ├── run.py                     # Inicializador do servidor HTTP com auto-seleção de porta
│   ├── popular_dados.py           # Script para preenchimento de dados de supermercado sob demanda
│   └── backup_chat.py             # Backup contínuo de conversas do agente
└── requirements.txt
```

---

## 2. Modelo de Dados Relacional e Variáveis Analisadas

- **`PRODUTO (1) -> (N) VENDA`**: `id_produto`, `nome`, `categoria`, `preco_base`, `estoque_atual`, `estoque_minimo`, `lead_time_dias`.
- **`PRODUTO (1) -> (N) PREVISÃO`**: `id_previsao`, `id_produto`, `periodo`, `horizonte_dias`, `demanda_prevista`, `confianca`, `sugestao_reposicao`, `status_risco`.
- **`VENDA`**: `id_venda`, `id_produto`, `data`, `quantidade`, `preco`, `promocao`.
- **Variáveis Consideradas no Modelo**:
  - Giro Diário Base do Produto
  - Efeito do Dia da Semana (fatores empíricos para fins de semana)
  - Efeito do Ciclo do Mês (recebimento salarial no início de mês)
  - Padrões Sazonais e Datas Comemorativas (Páscoa, Festa Junina, Verão, Natal)
  - Elasticidade de Preço sob Condição Promocional
  - Ponto de Pedido ($P = \text{Consumo Diário} \times \text{Lead Time} + \text{Segurança}$)

---

## 3. Telas do Protótipo

1. **Login**: Autenticação com credenciais padrão (`admin@admin.com` / `admin`).
2. **Inicio**: Cards de KPIs (Giro 30d, Acurácia média, Alertas de ruptura/excesso, Redução de perdas), gráfico de vendas históricas vs projeção, distribuição por categoria, rankings de Top 5 produtos e resumo de ações imediatas de reposição.
3. **Estoque**: Tabela com filtros, ajuste rápido de estoque (+20), cadastro de produtos, ponto de pedido e lead time.
4. **Vendas**: Histórico de transações, registro manual de vendas com baixa imediata no estoque, download de modelo CSV e upload com higienização automática.
5. **Previsão**: Simulação por produto nos horizontes de 7, 15 e 30 dias, simulação de promoção, curva com intervalo de 95%, métricas científicas (MAE, RMSE, MAPE) e exportação em CSV.
6. **Analise de Sazonalidade**: Curva anual de 12 meses de cada evento (Páscoa, Festa Junina, Verão, Natal), comparativo Reativo vs Preditivo e produtos impactados.
7. **Alertas**: Classificação de risco (Ruptura Iminente, Ponto de Pedido, Excesso), impacto financeiro em R$ e reposição com 1 clique.

---

## 4. Como Executar

### Pré-requisitos
- Python 3.11+
- Virtualenv

### Instalação e Execução
```bash
# Ative o ambiente virtual
source .venv/bin/activate

# Execute o servidor web (inicializa com banco limpo e usuário admin)
python3 scripts/run.py

# Opcional: Para preencher o banco com dados de supermercado demonstrativos
python3 scripts/popular_dados.py
```
Acesse no navegador:
- **Aplicação Web**: [http://localhost:8080](http://localhost:8080) (ou 8000)
- **Documentação Interativa (Swagger)**: [http://localhost:8080/docs](http://localhost:8080/docs)
- **Credenciais**: `admin@admin.com` / `admin`

---

## 5. Testes Automatizados

```bash
pytest -v
```
Todos os 15 testes validam o modelo de dados, o motor de previsão sem vazamento de dados, o pipeline de ingestão CSV e os endpoints REST.
