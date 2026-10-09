import sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

#config da pagina
st.set_page_config(
    page_title="Painel Epidemiológico - SRAG / SIVEP-Gripe",
    page_icon="🏥",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
GOLD_DIR = BASE_DIR / "data" / "3_gold"

@st.cache_data
def carregar_dados():
    arquivo_fato = GOLD_DIR / "fato_srag.parquet"
    if not arquivo_fato.exists():
        st.error("Dados da Camada Gold não encontrados, execute o pipeline primeiro")
        return None

    df = pd.read_parquet(arquivo_fato)

    #faixa etaria para enriquecer análise demográfica
    if "NU_IDADE_N" in df.columns:
        bins = [-1, 2, 12, 19, 59, 120]
        labels = ["0-2 anos", "3-12 anos", "13-19 anos", "20-59 anos", "60+ anos"]
        df["FAIXA_ETARIA"] = pd.cut(df["NU_IDADE_N"].fillna(0), bins=bins, labels=labels)
    else:
        df["FAIXA_ETARIA"] = "Não Informado"

    return df

df = carregar_dados()

if df is not None:
    st.title("🏥 Painel Analítico de Síndrome Respiratória Aguda Grave (SRAG)")
    st.markdown("**Vigilância Epidemiológica SIVEP-Gripe** | Pipeline de Dados End-to-End")
    st.markdown("---")

    #filtros
    st.sidebar.header("🔍 Filtros Globais")

    #filtro UF
    ufs_disponiveis = sorted([str(uf) for uf in df["SG_UF_NOT"].dropna().unique()])
    ufs_selecionadas = st.sidebar.multiselect("Selecione a UF:", options=ufs_disponiveis, default=ufs_disponiveis)

    #filtro virus
    virus_disponiveis = df["CLASSI_FIN_DESC"].dropna().unique().tolist()
    virus_selecionados = st.sidebar.multiselect(
        "Selecione o Agente Etiológico:", 
        options=virus_disponiveis, 
        default=virus_disponiveis
    )

    #aplicacao dos filtros
    df_filtrado = df[
        (df["SG_UF_NOT"].astype(str).isin(ufs_selecionadas)) &
        (df["CLASSI_FIN_DESC"].isin(virus_selecionados))
    ]

    #kpis
    col1, col2, col3, col4 = st.columns(4)
    total_casos = len(df_filtrado)
    total_uti = df_filtrado["FL_UTI"].sum()
    total_obitos = df_filtrado["FL_OBITO"].sum()
    taxa_letalidade = (total_obitos / total_casos * 100) if total_casos > 0 else 0

    col1.metric("Total de Internações", f"{total_casos:,}")
    col2.metric("Internações em UTI", f"{total_uti:,}", f"{(total_uti/total_casos*100 if total_casos else 0):.1f}% do total")
    col3.metric("Óbitos Confirmados", f"{total_obitos:,}")
    col4.metric("Taxa de Letalidade", f"{taxa_letalidade:.1f}%")

    st.markdown("---")

    #abas
    aba1, aba2, aba3, aba4 = st.tabs([
        "📈 1. Tendência Temporal", 
        "👤 2. Perfil Demográfico & Risco", 
        "🦠 3. Vigilância Etiológica", 
        "💉 4. Cobertura Vacinal"
    ])

    #aba1
    with aba1:
        st.subheader("Evolução Semanal das Notificações")
        df_semanal = df_filtrado.groupby("SEM_PRI").agg(
            Casos=("FL_UTI", "count"),
            UTI=("FL_UTI", "sum"),
            Obitos=("FL_OBITO", "sum")
        ).reset_index()

        df_semanal_long = df_semanal.melt(
            id_vars=["SEM_PRI"],
            value_vars=["Casos", "UTI", "Obitos"],
            var_name="Métrica", value_name="Quantidade"
        )

        fig_tempo = px.line(
            df_semanal_long, x="SEM_PRI", y="Quantidade", color="Métrica",
            labels={"SEM_PRI": "Semana Epidemiológica", "Quantidade": "Notificações"},
            title="Distribuição Temporal de SRAG por Semana Epidemiológica"
        )
        st.plotly_chart(fig_tempo, use_container_width=True)

    #aba2
    with aba2:
        st.subheader("Análise Demográfica e Fatores de Risco")
        c1, c2 = st.columns(2)

        with c1:
            fig_faixa = px.histogram(
                df_filtrado, x="FAIXA_ETARIA", color="EVOLUCAO_DESC",
                barmode="group", title="Distribuição por Faixa Etária vs Desfecho",
                labels={"FAIXA_ETARIA": "Faixa Etária", "count": "Casos"}
            )
            st.plotly_chart(fig_faixa, use_container_width=True)

        with c2:
            fig_uti = px.histogram(
                df_filtrado, x="UTI_DESC", color="EVOLUCAO_DESC",
                barmode="stack", title="Uso de Leito UTI por Desfecho Clínico",
                labels={"UTI_DESC": "Internou na UTI?"}
            )
            st.plotly_chart(fig_uti, use_container_width=True)


    #aba3
    with aba3:
        st.subheader("Distribuição por Agente Etiológico (Vírus Identificado)")
        df_virus = df_filtrado["CLASSI_FIN_DESC"].value_counts().reset_index()
        df_virus.columns = ["Diagnóstico", "Casos"]
        df_virus = df_virus.sort_values(by="Casos", ascending=True)

        fig_virus = px.bar(
            df_virus, x="Casos", y="Diagnóstico", orientation="h",
            color="Diagnóstico", title="Casos Confirmados por Tipo de Vírus",
            text_auto=True
        )
        st.plotly_chart(fig_virus, use_container_width=True)

    with aba4:
        st.subheader("Impacto da Vacinação nos Desfechos Graves")
        c1, c2 = st.columns(2)

        with c1:
            fig_vac_cov = px.histogram(
                df_filtrado, x="VACINA_COV_DESC", color="EVOLUCAO_DESC",
                barmode="group", title="Status Vacinal COVID-19 vs Evolução do Caso",
                labels={"VACINA_COV_DESC": "Vacina COVID-19"}
            )
            st.plotly_chart(fig_vac_cov, use_container_width=True)

        with c2:
            fig_vac_flu = px.histogram(
                df_filtrado, x="VACINA_DESC", color="EVOLUCAO_DESC",
                barmode="group", title="Status Vacinal Influenza vs Evolução do Caso",
                labels={"VACINA_DESC": "Vacina Gripe/Flu"}
            )
            st.plotly_chart(fig_vac_flu, use_container_width=True)