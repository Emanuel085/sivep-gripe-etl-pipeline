# 🏥 Pipeline Epidemiológico SRAG / SIVEP-Gripe (Arquitetura Medalhão)

> Pipeline de dados *end-to-end* para ingestão, tratamento, modelagem e visualização de dados públicos de Síndrome Respiratória Aguda Grave (SRAG) do OpenDataSUS, orquestrado via Docker.

---

## 📌 Visão Geral do Projeto

Este projeto automatiza a coleta e o processamento de dados epidemiológicos públicos de saúde no Brasil. Utilizando a **Arquitetura Medalhão** (Bronze, Silver e Gold), os dados brutos de notificações de internamentos são transformados em um *Data Mart* otimizado em formato colunar (Parquet) e consumidos por um painel analítico interativo construído em Streamlit e Plotly.

### 🛠️ Tecnologias Utilizadas

- **Linguagem & Processamento:** Python 3.12, Pandas, PyArrow
- **Visualização & BI:** Streamlit, Plotly
- **Orquestração & Isolamento:** Docker, Docker Compose
- **Armazenamento:** Apache Parquet, CSV

---

## 🏗️ Arquitetura do Pipeline (Medalhão)

```mermaid
flowchart LR
    A[OpenDataSUS / SIVEP-Gripe] -->|Streaming HTTP| B[(1_bronze: sivep_gripe_raw.csv)]
    B -->|Limpeza & Tipagem| C[(2_silver: sivep_gripe_cleaned.parquet)]
    C -->|Modelagem & Flag Metrics| D[(3_gold: fato_srag.parquet / agg_semanal.parquet)]
    D -->|"@st.cache_data"| E[Dashboard Streamlit]
Detalhamento das Camadas
Bronze (Raw Data): Extração dos dados brutos em formato CSV utilizando requisições em streaming (requests.iter_content), evitando estouro de memória RAM e garantindo resiliência com fallback de URLs.
```

Silver (Cleansing & Normalization): Padronização de cabeçalhos, tratamento de valores nulos, conversão defensiva de tipos de dados e salvamento otimizado em formato colunar Parquet.

Gold (Analytics & Data Mart): Construção da tabela fato e visões agregadas semanais com indicadores calculados (FL_UTI, FL_OBITO, FL_VACINADO_COV) prontas para consumo de BI.

📊 Visualizações do Dashboard
O painel analítico interativo disponibiliza 4 visões estratégicas:

📈 Tendência Temporal: Evolução semanal de notificações, internações em UTI e óbitos.

👤 Perfil Demográfico & Risco: Análise demográfica por faixa etária vs. desfecho clínico.

🦠 Vigilância Etiológica: Distribuição e relevância dos agentes etiológicos identificados (COVID-19, Influenza, etc.).

💉 Cobertura Vacinal: Relação entre o status de vacinação e o risco de evolução grave.

🚀 Como Executar o Projeto
Pré-requisitos
Docker Desktop instalado e em execução.

Git configurado.

1. Clonar o repositório
Bash
git clone [https://github.com/Emanuel085/sivep-gripe-etl-pipeline.git](https://github.com/Emanuel085/sivep-gripe-etl-pipeline.git)
cd sivep-gripe-etl-pipeline
2. Baixar os dados brutos (Camada Bronze)
Baixe o arquivo CSV de dados de SRAG no portal do OpenDataSUS e salve-o em:

Plaintext
data/1_bronze/sivep_gripe_raw.csv
3. Rodar o pipeline ETL localmente
Bash
python src/transformation/clean_bronze.py
python src/transformation/build_gold.py
4. Subir a aplicação via Docker Compose
Bash
docker compose up --build
Acesse o painel no seu navegador no endereço: http://localhost:8501

📂 Estrutura do Repositório
Plaintext
sivep-gripe-etl-pipeline/
├── app/
│   └── dashboard.py          # Interface gráfica interativa (Streamlit + Plotly)
├── data/
│   ├── 1_bronze/             # Dados brutos (sivep_gripe_raw.csv)
│   ├── 2_silver/             # Dados limpos e padronizados (Parquet)
│   └── 3_gold/               # Data Mart e agregados modelados (Parquet)
├── src/
│   ├── config.py             # Centralizador de caminhos e mapeamentos
│   ├── download_sivep.py     # Script de ingestão resiliente via streaming
│   └── transformation/
│       ├── clean_bronze.py   # ETL Bronze -> Silver
│       └── build_gold.py     # ETL Silver -> Gold
├── .dockerignore              # Otimização do contexto de build do Docker
├── docker-compose.yml        # Orquestração do container e montagem de volumes
├── Dockerfile                # Imagem base Python 3.12-slim
└── requirements.txt          # Dependências do projeto