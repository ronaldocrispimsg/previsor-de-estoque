# Predikta Data Solutions
### Solução de Previsão de Demanda e Apoio à Gestão de Estoque para Supermercados

Protótipo de sistema web voltado a pequenos e médios supermercados para substituição da gestão puramente reativa ou baseada em "feeling" por tomadas de decisão orientadas a dados e inteligência preditiva.

> **Contexto Institucional**: Instituto Federal do Norte de Minas Gerais (IFNMG) - Campus Januária  
> **Curso**: Bacharelado em Sistemas de Informação  
> **Disciplina**: Gerência de Projetos (Prof. João Pedro)  
> **Equipe**:
> - **João Pedro**: Líder de Projeto e Negócios
> - **Victor Daniel**: Engenheiro de Dados e Desenvolvedor Back-end
> - **Rafael**: Desenvolvedor Front-end & UX / Cientista de Dados
> - **Ronaldo Crispim**: Desenvolvedor e Integrador Técnico

---

## 1. Visão Geral e Arquitetura

O sistema opera sobre o pipeline do fluxo de inteligência preditiva:
$$\text{Histórico de Vendas} \longrightarrow \text{Banco de Dados} \longrightarrow \text{Tratamento} \longrightarrow \text{Modelo Preditivo} \longrightarrow \text{Dashboard} \longrightarrow \text{Decisão}$$

```text
previsor-de-estoque/
├── backend/
│   └── app/
│       ├── config.py              # Parâmetros de ambiente e banco de dados
│       ├── database.py            # Engine SQLAlchemy e SessionLocal
│       ├── main.py                # Aplicação FastAPI e servidor estático
│       ├── models/                # Entidades relacionais (Produto, Venda, Previsao, Usuario)
│       ├── routes/                # Endpoints REST (auth, produtos, vendas, previsões, sazonalidade, alertas, dashboard)
│       ├── schemas/               # Contratos Pydantic com inteligência explicável (XAI)
│       └── services/              # Ingestão CSV, decomposição sazonal e cálculo de métricas
├── frontend/                      # Interface Web responsiva (SPA)
│   ├── index.html                 # Painel do gestor (Dashboard, Catálogo, Vendas/CSV, Previsão, Sazonalidade)
│   ├── css/style.css              # Custom tokens, badges de ruptura, estados de estoque e toasts
│   └── js/                        # Módulos: api, auth, dashboard, produtos, vendas, previsao, sazonalidade, alertas
├── tests/                         # Suíte de testes automatizados com pytest (15 testes)
├── scripts/
│   ├── run.py                     # Inicializador do servidor HTTP com auto-seleção de porta
│   └── backup_chat.py             # Backup contínuo de conversas do agente
└── requirements.txt
```

---

## 2. Modelo de Dados Relacional e Variáveis Analisadas (Seção 13 e 16)

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

## 3. Telas do Protótipo (Seção 15 do Relatório)

1. **Login**: Autenticação com credenciais demonstrativas (`gestor@supermercado.com` / `admin123`).
2. **Dashboard do Gestor**: Cards de KPIs (Giro 30d, Acurácia média, Alertas de ruptura/excesso, Redução estimada de perdas de 18%), gráfico de vendas históricas vs projeção, rosca por categoria, rankings de Top 5 produtos e diagrama do fluxo.
3. **Catálogo de Produtos & Estoque**: Tabela com filtros, ajuste rápido de estoque (+20), modal de edição, ponto de pedido e lead time.
4. **Vendas & Ingestão CSV**: Histórico de transações, registro manual de vendas com baixa imediata no estoque, download de modelo CSV e upload com higienização automática.
5. **Previsão de Demanda**: Simulação por produto nos horizontes de 7, 15 e 30 dias, simulação de promoção, curva com intervalo de 95%, métricas científicas (MAE, RMSE, MAPE) e exportação em CSV.
6. **Análise de Sazonalidade**: Curva anual de 12 meses de cada evento (Páscoa, Festa Junina, Verão, Natal), comparativo Reativo vs Preditivo e produtos impactados.
7. **Alertas & Gestão de Estoque**: Classificação de risco (Ruptura Iminente, Ponto de Pedido, Excesso), impacto financeiro em R$ e reposição com 1 clique.

---

## 4. Como Executar

### Pré-requisitos
- Python 3.11+
- Virtualenv

### Instalação e Execução
```bash
# Ative o ambiente virtual
source .venv/bin/activate

# Execute o servidor web
python3 scripts/run.py
```
Acesse no navegador:
- **Aplicação Web**: [http://localhost:8080](http://localhost:8080) (ou 8000)
- **Documentação Interativa (Swagger)**: [http://localhost:8080/docs](http://localhost:8080/docs)

---

## 5. Testes Automatizados

```bash
pytest -v
```
Todos os 15 testes validam o modelo de dados, o motor de previsão sem vazamento de dados, o pipeline de ingestão CSV e os endpoints REST.
