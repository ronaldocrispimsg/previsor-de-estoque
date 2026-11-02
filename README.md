# Predikta Data Solutions
### Solução de Previsão de Demanda e Apoio à Gestão de Estoque para Supermercados

Protótipo de sistema web voltado a pequenos e médios supermercados para substituição da gestão reativa por tomadas de decisão orientadas a dados e inteligência preditiva.

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

O sistema opera sobre o fluxo:
$$\text{Histórico de Vendas} \longrightarrow \text{Banco de Dados} \longrightarrow \text{Tratamento} \longrightarrow \text{Modelo Preditivo} \longrightarrow \text{Dashboard} \longrightarrow \text{Decisão}$$

```text
previsor-de-estoque/
├── backend/
│   └── app/
│       ├── config.py              # Parâmetros de ambiente e banco de dados
│       ├── database.py            # Engine SQLAlchemy e SessionLocal
│       ├── main.py                # Aplicação FastAPI e servidor estático
│       ├── models/                # Entidades relacionais (Produto, Venda, Previsao, Usuario)
│       ├── routes/                # Endpoints REST (auth, produtos, vendas, previsões, sazonalidade, alertas)
│       ├── schemas/               # Contratos de dados Pydantic
│       └── services/              # Tratamento de séries temporais, previsão e alertas
├── frontend/                      # Interface Web responsiva (SPA)
│   ├── index.html                 # Painel do gestor (Dashboard, Catálogo, Previsão, Sazonalidade)
│   ├── css/style.css              # Custom tokens, badges de ruptura e estados de estoque
│   └── js/                        # Módulos de API, autenticação, gráficos e diagnósticos
├── tests/                         # Suíte de testes automatizados com pytest (13 testes)
├── scripts/
│   ├── run.py                     # Inicializador do servidor HTTP
│   └── backup_chat.py             # Backup contínuo de conversas do agente
└── requirements.txt
```

---

## 2. Modelo de Dados Relacional

- **`PRODUTO (1) -> (N) VENDA`**: `id_produto`, `nome`, `categoria`, `preco_base`, `estoque_atual`, `estoque_minimo`, `lead_time_dias`.
- **`PRODUTO (1) -> (N) PREVISÃO`**: `id_previsao`, `id_produto`, `periodo`, `horizonte_dias`, `demanda_prevista`, `confianca`, `sugestao_reposicao`, `status_risco`.
- **`VENDA`**: `id_venda`, `id_produto`, `data`, `quantidade`, `preco`, `promocao`.

---

## 3. Telas do Protótipo

1. **Login**: Autenticação com credenciais demonstrativas (`gestor@supermercado.com` / `admin123`).
2. **Dashboard**: Indicadores de giro (30d), acurácia média da IA, alertas ativos de ruptura/excesso, evolução histórica de vendas vs projeção futura e faturamento por categoria.
3. **Catálogo de Produtos**: Tabela com filtros rápidos por categoria, status de risco e modal para cadastro de novas mercadorias.
4. **Previsão de Demanda**: Simulação por produto nos horizontes de 7, 15 e 30 dias, impacto de promoções, gráfico com intervalo de confiança (95%) e métricas de qualidade (MAE, RMSE, MAPE).
5. **Análise de Sazonalidade**: Padrões comemorativos brasileiros (Páscoa nos chocolates, Festa Junina no milho/canjica, Verão em bebidas, Natal em panetones).
6. **Alertas & Gestão de Estoque**: Classificação de risco de ruptura (falta de produto) ou excesso (capital parado), com ação de reposição em 1 clique.

---

## 4. Como Executar

### Pré-requisitos
- Python 3.11+
- Pip / Venv

### Instalação
```bash
# Clone ou acerte o diretório do projeto
cd previsor-de-estoque

# Ative ou crie o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# Instale as dependências
pip install -r requirements.txt
```

### Inicialização do Sistema
```bash
python3 scripts/run.py
```
Acesse no navegador:
- **Aplicação Web & Dashboard**: [http://localhost:8000](http://localhost:8000)
- **Documentação Interativa da API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 5. Execução dos Testes Automatizados

```bash
pytest -v
```
A suíte valida:
- Persistência e relacionamentos relacionais (`Produto`, `Venda`, `Previsao`).
- Motor preditivo e métricas de erro científico sem vazamento de dados (*data leakage*).
- Endpoints REST de autenticação, produtos, previsões, sazonalidade e alertas.
