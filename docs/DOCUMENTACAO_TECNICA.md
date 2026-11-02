# DOCUMENTAÇÃO TÉCNICA DO SISTEMA - PREVISOR DE ESTOQUE

---

## 1. Visão Geral e Contexto de Negócio

O **Previsor de Estoque** é uma plataforma web corporativa desenvolvida para pequenos e médios supermercados com o objetivo de transformar a tomada de decisão: da gestão reativa — baseada em intuição ou em compras emergenciais de última hora — para uma **gestão orientada a dados e inteligência preditiva**.

### 1.1 O Problema no Varejo Supermercadista
No varejo alimentar brasileiro, os gestores enfrentam dois extremos dispendiosos:
1. **Ruptura de Estoque (Falta de Produto)**: Quando produtos de alto giro ou de demanda sazonal esgotam na gôndola. Isso acarreta perda imediata de faturamento (estimada em até 18% em datas comemorativas) e insatisfação do cliente.
2. **Excesso de Estoque (Sobrecarga e Perdas)**: Superabastecimento que gera custo financeiro de capital parado, saturação do espaço de depósito e risco crítico de descarte por vencimento de itens perecíveis.

### 1.2 Objetivo e Escopo
O sistema fornece diagnósticos automatizados de reposição, estimativas de demanda futura e detecção antecipada de picos sazonais.

- **Dentro do Escopo**:
  - Ingestão e higienização de dados históricos de vendas (registro avulso ou planilha CSV em lote).
  - Catálogo de produtos com parâmetros logísticos de estoque (Estoque Mínimo, *Lead Time*, Ponto de Pedido).
  - Motor de previsão de séries temporais com horizontes de 7, 15 e 30 dias e intervalos de confiança estatísticos (95%).
  - Decomposição analítica de fatores de influência (tendência diária, dia da semana, ciclo do mês, sazonalidades festivas e impacto de promoções).
  - Análise contínua de sazonalidades críticas do varejo alimentar (Páscoa, Festa Junina, Verão, Natal).
  - Painel de monitoramento de risco e alertas operacionais com cálculo de impacto financeiro em R$.
- **Fora do Escopo Inicial**:
  - Ponto de Venda (PDV) / Frente de Caixa.
  - Emissão e autorização de notas fiscais eletrônicas (NF-e/NFC-e).
  - Gestão contábil e conciliação bancária completa.
  - Emissão automática de pedidos de compra integrados a sistemas EDI de fornecedores.

---

## 2. Arquitetura do Sistema e Stack Tecnológica

O sistema foi concebido seguindo uma arquitetura moderna, desacoplada, stateless e escalável:

```
+-----------------------------------------------------------------------------------+
|                           CAMADA DE APRESENTAÇÃO (FRONTEND)                       |
|   SPA (Single Page Application) Modular em HTML5 + Tailwind CSS + Chart.js        |
|   Abas: [Inicio]  [Estoque]  [Vendas]  [Previsão]  [Analise de Sazonalidade]  [Alertas] |
+-----------------------------------------------------------------------------------+
                                        | (Requisições HTTP / JSON REST)
                                        v
+-----------------------------------------------------------------------------------+
|                             CAMADA DE API REST (BACKEND)                          |
|                       FastAPI (Python 3.11+) + Uvicorn ASGI                       |
|   Rotas: /api/auth | /api/produtos | /api/vendas | /api/previsoes | /api/sazonalidade | /api/alertas |
+-----------------------------------------------------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+---------------------------------+           +---------------------------------+
|     SERVIÇOS DE NEGÓCIO E ML    |           |    CAMADA DE DADOS E PERSISTÊNCIA|
|  - forecasting.py (Séries Temp) |           |  - SQLAlchemy 2.0 (ORM)         |
|  - data_cleaner.py (Sanitização)|           |  - Pydantic v2 (Validações)     |
|  - alert_service.py (Diagnóstico)|          |  - SQLite (data/previsor_estoque.db)|
|  - seeder.py (Carga sob Demanda)|           |  - StaticPool Memory (Testes)   |
+---------------------------------+           +---------------------------------+
```

### 2.1 Tecnologias Adotadas
- **Back-end**: **Python 3.11+**, **FastAPI** (framework assíncrono de alta performance), **Uvicorn** (servidor ASGI), **Pydantic v2** (validação de contratos de entrada e saída) e **SQLAlchemy 2.0** (ORM relacional).
- **Banco de Dados**: **SQLite 3** em disco para operação (`data/previsor_estoque.db`) e **SQLite `:memory:` com `StaticPool`** para isolamento total nos testes automatizados.
- **Front-end**: **HTML5 semântico**, **Tailwind CSS** (design corporativo responsivo), **Chart.js** (gráficos interativos de linhas, barras e rosca) e **JavaScript ES6+ Vanilla Modular** organizado por domínios.
- **Testes Automatizados**: **Pytest** e **HTTPX/TestClient** com suíte de 15 testes de regressão contínua.

---

## 3. Modelo de Dados e Dicionário de Entidades

O banco de dados relacional é estruturado em 4 entidades centrais com integridade referencial:

```
  +------------------+         1:N          +------------------+
  |     PRODUTO      |--------------------->|      VENDA       |
  +------------------+                      +------------------+
  | id_produto (PK)  |                      | id_venda (PK)    |
  | nome             |                      | id_produto (FK)  |
  | categoria        |                      | data             |
  | preco_base       |                      | quantidade       |
  | estoque_atual    |                      | preco            |
  | estoque_minimo   |                      | promocao         |
  | lead_time_dias   |                      +------------------+
  +------------------+
           |
           | 1:N
           v
  +------------------+                      +------------------+
  |     PREVISAO     |                      |     USUARIO      |
  +------------------+                      +------------------+
  | id_previsao (PK) |                      | id_usuario (PK)  |
  | id_produto (FK)  |                      | nome             |
  | periodo          |                      | email (Unique)   |
  | horizonte_dias   |                      | senha_hash       |
  | demanda_prevista |                      | cargo            |
  | status_risco     |                      +------------------+
  | confianca        |
  +------------------+
```

### 3.1 Dicionário de Campos

#### Tabela `produtos`
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id_produto` | Integer (PK) | Identificador único do produto no catálogo. |
| `nome` | String(120) | Nome descritivo da mercadoria (ex: *Arroz Branco Tipo 1 5kg*). |
| `categoria` | String(80) | Categoria mercadológica (ex: *Doces e Chocolates*, *Bebidas*). |
| `preco_base` | Float | Preço unitário regular de venda praticado no supermercado. |
| `estoque_atual` | Integer | Saldo físico disponível em estoque/gôndola no momento. |
| `estoque_minimo`| Integer | Margem de segurança de estoque contra oscilações de demanda. |
| `lead_time_dias`| Integer | Prazo em dias corridos que o fornecedor leva entre o pedido e a entrega. |
| `criado_em` | DateTime | Carimbo de data/hora do cadastro. |
| `atualizado_em`| DateTime | Carimbo de data/hora da última alteração de cadastro ou saldo. |

#### Tabela `vendas`
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id_venda` | Integer (PK) | Identificador único da transação de saída. |
| `id_produto` | Integer (FK) | Chave estrangeira referenciando o produto comercializado (`produtos.id_produto`). |
| `data` | Date | Data da realização da venda (YYYY-MM-DD). |
| `quantidade` | Integer | Unidades comercializadas na transação ($> 0$). |
| `preco` | Float | Preço unitário efetivamente praticado na transação ($> 0$). |
| `promocao` | Integer | Indicador booleano (0 = Preço Normal, 1 = Preço Promocional). |
| `criado_em` | DateTime | Carimbo de data/hora de inserção do registro. |

#### Tabela `previsoes`
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id_previsao` | Integer (PK) | Identificador único da previsão gerada. |
| `id_produto` | Integer (FK) | Chave estrangeira do produto analisado. |
| `periodo` | String(60) | Descrição do intervalo coberto pela previsão. |
| `horizonte_dias`| Integer | Quantidade de dias futuros simulados (7, 15 ou 30). |
| `demanda_prevista` | Float | Quantidade total de unidades estimadas para o período. |
| `estoque_atual` | Integer | Saldo do produto no momento do cálculo da previsão. |
| `sugestao_reposicao` | Float | Unidades sugeridas para compra imediata. |
| `status_risco` | String(20) | Diagnóstico: `RUPTURA`, `ATENCAO`, `EXCESSO`, `EQUILIBRADO`. |
| `confianca` | Float | Percentual de acurácia estimada do modelo ($50{,}0\%$ a $98{,}5\%$). |
| `multiplicador_sazonal` | Float | Fator de pico sazonal detectado no período. |
| `data_geracao`| Date | Data em que a simulação preditiva foi gerada e gravada. |

#### Tabela `usuarios`
| Campo | Tipo | Descrição |
| :--- | :--- | :--- |
| `id_usuario` | Integer (PK) | Identificador único do operador do sistema. |
| `nome` | String(100) | Nome do usuário (ex: *admin*). |
| `email` | String(120) | E-mail corporativo único utilizado no login (ex: *admin@admin.com*). |
| `senha_hash` | String(64) | Hash criptográfico SHA-256 da senha. |
| `cargo` | String(80) | Função exercida pelo operador. |
| `criado_em` | DateTime | Data/hora de criação do acesso. |

---

## 4. Ingestão e Tratamento de Dados (*Data Cleaner*)

A confiabilidade dos modelos de previsão depende criticamente da higienização dos dados de entrada. O módulo `backend/app/services/data_cleaner.py` implementa um pipeline de sanitização rigoroso:

### 4.1 Regras de Validação e Descarte de Inconsistências
1. **Quantidade Inválida**: Registros com quantidade menor ou igual a zero ($q \le 0$) são sumariamente descartados.
2. **Preço Inválido**: Registros com preço unitário nulo, negativo ou zerado ($p \le 0$) são descartados.
3. **Produto Inexistente**: Registros cujo `id_produto` não pertença à base de produtos cadastrada são rejeitados para evitar orfandade referencial.
4. **Data Inválida**: Datas futuras ou formatos incorretos são higienizados e rejeitados.
5. **Preenchimento de Dias Ausentes**: Em séries temporais diárias, dias em que o supermercado esteve fechado ou não houve venda para determinado item são preenchidos com quantidade zero ($0$), garantindo a continuidade cronológica necessária aos algoritmos matemáticos.

### 4.2 Ingestão em Lote via Arquivo CSV
O sistema disponibiliza um endpoint de upload de arquivos CSV delimitados por ponto e vírgula (`;` ou `,`), acompanhado do endpoint para download do modelo padronizado:
```csv
id_produto;data;quantidade;preco;promocao
1;2026-10-15;14;42.90;0
1;2026-10-16;18;42.90;0
2;2026-10-15;30;14.50;1
```

---

## 5. Motor de Predição de Demanda (Aprofundamento Detalhado)

O núcleo preditivo do sistema (`backend/app/services/forecasting.py`) utiliza uma **modelagem de decomposição multiplicativa de séries temporais com suavização adaptativa**, combinando a tendência empírica com fatores determinísticos de calendário do varejo.

### 5.1 Equação Fundamental da Demanda Projetada
Para cada dia futuro $t$ pertencente ao horizonte solicitado ($t \in [1, H]$, onde $H \in \{7, 15, 30\}$), a demanda esperada $\hat{y}_t$ é calculada por:

$$\hat{y}_t = \max\Big(0{,}2\,;\; L_T \times S(t) \times D(\text{weekday}_t) \times C(\text{day}_t) \times P(\text{promo}_t)\Big)$$

Onde:
- **$L_T$**: Nível base da demanda diária do produto no final da série histórica.
- **$S(t)$**: Multiplicador sazonal da categoria do produto para o mês/período da data-alvo.
- **$D(\text{weekday}_t)$**: Fator de ajuste para o dia da semana da data-alvo.
- **$C(\text{day}_t)$**: Fator do ciclo de pagamento do mês brasileiro.
- **$P(\text{promo}_t)$**: Fator de elasticidade sob simulação de campanha promocional.

---

### 5.2 Detalhamento Matemático dos Fatores

#### 1. Nível Base ($L_T$) via Suavização Exponencial Adaptativa (EMA)
O histórico de vendas diárias $[y_1, y_2, \dots, y_T]$ é processado recursivamente através de uma média móvel exponencial com coeficiente de suavização $\alpha = 0{,}25$:

$$L_0 = y_1$$
$$L_t = \alpha \cdot y_t + (1 - \alpha) \cdot L_{t-1} \quad \text{para } t = 1, \dots, T$$

- O valor $\alpha = 0{,}25$ foi selecionado por conferir 75% do peso à inércia do histórico recente e 25% à nova observação diária, tornando o modelo estável diante de variações esporádicas de caixa sem perder a agilidade para captar mudanças de tendência.

#### 2. Fator do Dia da Semana ($D$) — Efeito Fim de Semana
Supermercados possuem um padrão acentuado de concentração de compras nos fins de semana. O vetor de índices empíricos $D$ é parametrizado de segunda a domingo:

| Dia da Semana | Índice ($D$) | Interpretação Operacional |
| :--- | :---: | :--- |
| Segunda-feira | **$0{,}85$** | Menor fluxo (-15% sobre a média); dia de reposição pós-fim de semana. |
| Terça-feira | **$0{,}90$** | Giro estável (-10%). |
| Quarta-feira | **$0{,}95$** | Tradicional dia de feira/hortifruti no varejo alimentar. |
| Quinta-feira | **$0{,}95$** | Manutenção do padrão regular de meio de semana. |
| Sexta-feira | **$1{,}25$** | Abastecimento pré-fim de semana (+25% de volume). |
| Sábado | **$1{,}45$** | Pico absoluto semanal de compras de grande porte (+45%). |
| Domingo | **$1{,}15$** | Compras rápidas de conveniência, carnes e bebidas (+15%). |

#### 3. Fator do Ciclo do Mês ($C$) — Quinto Dia Útil e Liquidez
O poder de compra no varejo brasileiro varia conforme o calendário salarial:

$$C(\text{dia}) = \begin{cases} 
1{,}15 & \text{se } 1 \le \text{dia} \le 10 \quad \text{(quinto dia útil e liquidez máxima)} \\
1{,}00 & \text{se } 11 \le \text{dia} \le 20 \quad \text{(fluxo regular de compras)} \\
0{,}90 & \text{se } 21 \le \text{dia} \le 31 \quad \text{(desaceleração por restrição orçamentária)}
\end{cases}$$

#### 4. Fator Promocional ($P$) — Elasticidade de Preço
Quando o operador ativa a opção de "Simular Promoção (-15% no preço)", o algoritmo aplica o princípio da elasticidade-preço da demanda no segmento alimentar:

$$P(\text{promo}) = \begin{cases} 
1{,}45 & \text{se promoção ativa (estímulo de +45% no volume)} \\
1{,}00 & \text{se preço regular praticado}
\end{cases}$$

---

### 5.3 Intervalo de Confiança Estatístico (95%)
Para apoiar a tomada de decisão com gestão de incerteza, o sistema calcula os limites superior e inferior da projeção com base na distribuição normal do erro residual ($Z_{0{,}975} = 1{,}96$):

$$\text{Limite Inferior}_t = \max\Big(0\,;\; \hat{y}_t - 1{,}96 \cdot \text{RMSE} \cdot 0{,}7\Big)$$
$$\text{Limite Superior}_t = \hat{y}_t + 1{,}96 \cdot \text{RMSE} \cdot 0{,}7$$

O fator atenuador $0{,}7$ reflete a estabilidade da agregação do consumo no horizonte analisado.

---

### 5.4 Validação Temporal Estrita sem Vazamento de Dados (*Data Leakage*)
Um dos maiores erros em sistemas de previsão é a contaminação do passado com dados futuros (*lookahead bias*). O sistema implementa uma partição temporal rígida (*Holdout / Backtesting Temporal*):

```
Série Histórica Completa: [------------------- HISTÓRICO TOTAL (N dias) -------------------]
Partição Temporal:        [------- TREINO (N - S dias) -------] [---- TESTE / HOLDOUT (S) ----]
                                                                        ^
                                                      Cálculo Cego das Métricas (MAE, RMSE, MAPE)
```

1. **Janela de Treino**: O nível da série é calibrado estritamente até a data de corte ($N - S$).
2. **Janela de Teste (*Holdout*)**: Os últimos $S$ dias ($7 \le S \le 30$) são mantidos ocultos durante o cálculo do nível e servem exclusivamente para mensuração cega do desvio entre o que foi previsto e o que ocorreu de fato:

- **Erro Médio Absoluto (MAE)**:
  $$\text{MAE} = \frac{1}{S} \sum_{k=1}^{S} |y_k - \hat{y}_k|$$
- **Raiz do Erro Quadrático Médio (RMSE)**:
  $$\text{RMSE} = \sqrt{\frac{1}{S} \sum_{k=1}^{S} (y_k - \hat{y}_k)^2}$$
- **Erro Percentual Absoluto Médio (MAPE)**:
  $$\text{MAPE} = \frac{100\%}{S} \sum_{k=1}^{S} \frac{|y_k - \hat{y}_k|}{\max(1\,;\, y_k)}$$
- **Acurácia Estimada do Modelo**:
  $$\text{Acurácia} = \max\Big(50{,}0\%\,;\; \min(98{,}5\%\,;\; 100\% - \text{MAPE})\Big)$$

---

### 5.5 Dimensionamento Logístico de Estoque e Ponto de Pedido

A partir da demanda total prevista para o período ($\hat{Y} = \sum_{t=1}^{H} \hat{y}_t$), o sistema calcula a demanda média diária esperada $\bar{d} = \frac{\hat{Y}}{H}$.

#### Equação do Ponto de Pedido ($P$):
$$P = (\bar{d} \times L) + S_{\text{seg}}$$

Onde:
- **$L$**: *Lead Time* cadastrado para o produto (dias úteis para o fornecedor entregar o lote).
- **$S_{\text{seg}}$**: Estoque mínimo de segurança configurado para o item.

#### Sugestão de Compra:
$$\text{Sugestão} = \max\Big(0\,;\; \hat{Y} - \text{Estoque Atual}\Big)$$

#### Matriz de Classificação de Riscos de Estoque:
```
           +-----------------------------------------------------------+
           | Condição do Estoque Físico                                | Classificação |
           +-----------------------------------------------------------+---------------+
           | Estoque Atual <= 0 OU Estoque Atual < (Demanda x 0.40)    | RUPTURA       |
           | Estoque Atual < Ponto de Pedido (P)                       | ATENÇÃO       |
           | Estoque Atual > (Demanda x 2.20) E Estoque Atual > 30 un  | EXCESSO       |
           | Em qualquer outro cenário                                 | EQUILIBRADO   |
           +-----------------------------------------------------------+---------------+
```

---

## 6. Análise de Sazonalidade (Aprofundamento Detalhado)

O módulo de sazonalidade (`backend/app/routes/sazonalidade.py`) foi desenvolvido com base no comportamento de consumo alimentar brasileiro, mapeando 4 ciclos de alto impacto no faturamento:

### 6.1 Catálogo de Eventos Sazonais e Curvas de 12 Meses

```
Índice
 4.0 |                  [Páscoa: 3.8x]
     |                     /\                                [Natal: 3.2x]
 3.0 |                    /  \               [Junina: 2.6x]      /\
     |                   /    \                 /\              /  \
 2.0 | [Verão: 1.9x]    /      \               /  \            /    \
     |    /\           /        \             /    \          /      \
 1.0 |--/----\--------/----------\-----------/------\--------/--------\-- (Base 1.0)
     +-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+-----+
      Jan   Fev   Mar   Abr   Mai   Jun   Jul   Ago   Set   Out   Nov   Dez
```

| Evento Sazonal | Meses Críticos | Categorias Alimentares Impactadas | Multiplicador de Pico | Curva Mensal de Índices (Jan -> Dez) |
| :--- | :---: | :--- | :---: | :--- |
| **Páscoa** | Março, Abril | *Doces e Chocolates*, *Pescados* | **$3{,}8\times$** (+280%) | `[1.0, 1.0, 2.5, 3.8, 1.1, 1.0, 1.0, 1.0, 1.0, 1.1, 1.2, 1.4]` |
| **Festa Junina** | Junho, Julho | *Festa Junina*, *Mercearia*, *Bebidas Quentes* | **$2{,}6\times$** (+160%) | `[1.0, 1.0, 1.0, 1.0, 1.2, 2.6, 2.1, 1.0, 1.0, 1.0, 1.1, 1.3]` |
| **Verão / Calor** | Dezembro a Fevereiro | *Bebidas*, *Sorvetes*, *Gelo* | **$1{,}9\times$** (+90%) | `[1.9, 1.8, 1.3, 1.0, 1.0, 0.9, 0.9, 1.0, 1.1, 1.2, 1.4, 1.9]` |
| **Natal e Fim de Ano** | Novembro, Dezembro | *Padaria e Natalinos*, *Carnes Especiais* | **$3{,}2\times$** (+220%) | `[1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.4, 2.4, 3.2]` |

---

### 6.2 Quantificação do Impacto Financeiro da Sazonalidade
O gestor supermercadista muitas vezes não tem clareza de quanto dinheiro está deixando na mesa ao não planejar estoques sazonais. O sistema calcula a **Receita em Risco (R$)** para cada produto impactado:

1. **Demanda Regular de 30 Dias**:
   $$\text{Demanda Normal} = \frac{\text{Demanda Prevista no Período}}{\text{Multiplicador Sazonal}}$$
2. **Demanda de Pico Sazonal (30 Dias)**:
   $$\text{Demanda no Pico} = \text{Demanda Normal} \times \text{Multiplicador Sazonal}$$
3. **Falta Potencial em Unidades**:
   $$\text{Falta Potencial} = \max\Big(0\,;\; \text{Demanda no Pico} - \text{Estoque Físico Atual}\Big)$$
4. **Receita em Risco (R$)**:
   $$\text{Receita em Risco} = \text{Falta Potencial} \times \text{Preço Base}$$

Esse cálculo permite ao supermercado antecipar a negociação com distribuidores e indústrias com semanas de antecedência, obtendo melhores preços de frete, garantindo entrega no prazo e evitando a ruptura no momento de maior consumo do ano.

---

## 7. Mapeamento das 6 Abas da Interface Web

A interface web corporativa é dividida em 6 visões operacionais especializadas:

1. **`Inicio` (Painel Geral Executivo)**:
   - Cards de KPIs globais (Total de Produtos, Volume de Vendas 30d, Faturamento 30d, Acurácia Média do Modelo, Contadores de Ruptura e Excesso).
   - Gráfico de linha interativo com a evolução das vendas históricas versus projeção calculada.
   - Gráfico de rosca com a distribuição percentual do faturamento por categoria.
   - Painéis de Top 5 Produtos com Maior Giro Projetado e Top 5 Produtos com Risco Iminente de Falta.
   - Grade de resumo das Ações Prioritárias de Reposição.
2. **`Estoque` (Catálogo e Parâmetros Logísticos)**:
   - Tabela com listagem paginada de produtos, categoria, preço, estoque atual, mínimo e ponto de pedido calculado.
   - Filtros combinados de busca textual, categoria mercadológica e status de risco.
   - Botão de ajuste rápido de entrada (+20 unidades direto na tabela).
   - Modal de cadastro de novos produtos e modal de edição completa de parâmetros.
3. **`Vendas` (Histórico e Ingestão de Dados)**:
   - Histórico cronológico detalhado de vendas com preço praticado e indicador promocional.
   - Filtros por produto, intervalo de datas (início/fim) e condição comercial.
   - Modal de registro manual de venda avulsa com baixa imediata no saldo físico de estoque.
   - Módulo de download de planilha modelo CSV e upload em lote com sanitização automática.
4. **`Previsão` (Motor Analítico e Simulação)**:
   - Seletor de produto com controle de horizonte temporal (7, 15 ou 30 dias).
   - Checkbox para simulação de impacto promocional (-15%).
   - Cards com Demanda Prevista, Estoque Atual, Sugestão de Reposição e Sazonalidade Identificada.
   - Gráfico detalhado com histórico recente, curva de demanda futura e faixas do intervalo de confiança de 95%.
   - Painel de Decomposição dos Fatores de Demanda (Giro Base, Dia da Semana, Ciclo do Mês, Sazonalidade, Promoção, Ponto de Pedido).
   - Painel com as métricas de validação temporal do modelo (Acurácia, MAE, RMSE, MAPE).
   - Exportação do relatório da previsão gerada em formato CSV.
5. **`Analise de Sazonalidade` (Curvas Comparativas)**:
   - Seletor dos 4 eventos de varejo (Páscoa, Festa Junina, Verão e Natal).
   - Indicadores de pico médio e receita financeira total em risco acumulada no supermercado.
   - Gráfico de linha demonstrando a variação dos índices mensais nos 12 meses do ano.
   - Tabela com os produtos impactados, salto de demanda em %, diagnóstico e unidades sugeridas para compra antecipada.
6. **`Alertas` (Diagnóstico e Reposição com 1 Clique)**:
   - Tabela de classificação dinâmica de risco (`RUPTURA`, `ATENÇÃO`, `EXCESSO`).
   - Apresentação da cobertura estimada de dias de estoque ($C = \frac{\text{Estoque}}{\bar{d}}$) e do impacto financeiro estimado em R$.
   - Botão de "Repor Estoque" com 1 clique (executa a entrada simulada de mercadoria e normaliza os indicadores em tempo real).

---

## 8. Segurança e Controle de Acesso

- **Autenticação Stateless**: Autenticação via JSON REST utilizando credenciais operacionais.
- **Armazenamento de Senhas**: As senhas são criptografadas via algoritmo **SHA-256** unidirecional com *salt* padrão.
- **Credenciais Oficiais Padrão**:
  - **Nome**: `admin`
  - **E-mail**: `admin@admin.com`
  - **Senha**: `admin`
- **Inicialização Limpa e Isolamento**: O banco de dados inicia exclusivamente com o usuário `admin` ativo, sem poluir a base com dados artificiais a menos que o operador solicite expressamente via script CLI ou botão na interface.

---

## 9. Instruções de Execução, Automação e Testes

### 9.1 Pré-requisitos
- Sistema Operacional Linux / macOS / Windows com WSL2.
- Python 3.11 ou superior instalado.
- Ambiente virtual configurado (`.venv`).

### 9.2 Instalação e Execução
```bash
# 1. Ativar o ambiente virtual
source .venv/bin/activate

# 2. Iniciar o servidor web corporativo
python3 scripts/run.py
```
O script `scripts/run.py` detecta dinamicamente a disponibilidade de portas locais (porta 8080 ou 8000) e inicia o serviço Uvicorn.
- **Aplicação Web**: `http://localhost:8080` (ou `http://localhost:8000`)
- **Documentação Interativa da API (Swagger)**: `http://localhost:8080/docs`
- **Documentação Alternativa (ReDoc)**: `http://localhost:8080/redoc`

### 9.3 Carga de Dados Demonstrativos (Opcional)
Para popular o catálogo com produtos realistas de supermercado e um histórico de 180 dias de vendas diárias com sazonalidades:
```bash
# Execução via script CLI independente
python3 scripts/popular_dados.py --force
```
*(Ou através do botão "Popular Base de Dados" na barra superior da interface web).*

### 9.4 Execução da Suíte de Testes Automatizados
```bash
# Execução completa dos testes
pytest -v
```
A suíte é composta por 15 testes de integração e validação matemática:
1. `test_healthcheck`: Verificação do status de vida da API (`/healthz`).
2. `test_login_demo`: Autenticação e emissão de token com `admin@admin.com` / `admin`.
3. `test_listar_produtos`: Consulta paginada do catálogo com cálculo de ponto de pedido e giro.
4. `test_criar_e_consultar_produto`: Operação de escrita e leitura de novas mercadorias.
5. `test_ajuste_rapido_estoque`: Operação de ajuste rápido de saldo (+20 unidades).
6. `test_dashboard_stats`: Consolidação de métricas executivas, rankings e redução de perdas.
7. `test_eventos_sazonalidade`: Consulta dos 4 eventos e cálculo da curva de 12 meses.
8. `test_alertas_estoque`: Diagnóstico preditivo de ruptura, atenção e excesso.
9. `test_gerar_previsao_api`: Geração, decomposição de fatores e persistência de previsões.
10. `test_upload_csv_vendas_e_template`: Validação do upload de CSV com higienização e template.
11. `test_fator_sazonal_pascoa_chocolates`: Teste unitário do multiplicador de Páscoa (3.8x).
12. `test_fator_sazonal_neutro`: Teste unitário de neutralidade sazonal (1.0x).
13. `test_previsao_demanda_e_metricas`: Validação das métricas científicas (MAE, RMSE, MAPE e acurácia).
14. `test_criacao_produto_e_relacionamento_vendas`: Integridade do modelo relacional Produto -> Vendas.
15. `test_relacionamento_previsao`: Integridade do modelo relacional Produto -> Previsões.

