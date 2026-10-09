import sys
import pandas as pd
from pathlib import Path

#raiz do projeto ao sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.config import SILVER_DIR, GOLD_DIR

def construir_camada_gold():
    arquivo_silver = SILVER_DIR / "sivep_gripe_clean.parquet"
    
    if not arquivo_silver.exists():
        print(f"Erro: O arquivo {arquivo_silver} não foi encontrado!")
        return

    print("Iniciando a construção da Camada Gold (Data Mart)...")
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    #Carregar dados da camada Silver
    df = pd.read_parquet(arquivo_silver)

    #Garantir que colunas críticas existam mesmo se vierem ausentes da Silver
    if "CLASSI_FIN_DESC" not in df.columns:
        df["CLASSI_FIN_DESC"] = "Não Informado"
    else:
        df["CLASSI_FIN_DESC"] = df["CLASSI_FIN_DESC"].fillna("Não Informado")

    if "EVOLUCAO_DESC" not in df.columns:
        df["EVOLUCAO_DESC"] = "Não Informado"

    if "UTI_DESC" not in df.columns:
        df["UTI_DESC"] = "Não Informado"

    if "VACINA_COV_DESC" not in df.columns:
        df["VACINA_COV_DESC"] = "Não Informado"

    if "SEM_PRI" not in df.columns:
        df["SEM_PRI"] = 0
    else:
        df["SEM_PRI"] = df["SEM_PRI"].fillna(0)

    #Criar Indicadores Numéricos / Flag Metrics
    df["FL_UTI"] = (df["UTI_DESC"] == "Sim").astype(int)
    df["FL_OBITO"] = (df["EVOLUCAO_DESC"] == "Óbito por SRAG").astype(int)
    df["FL_VACINADO_COV"] = (df["VACINA_COV_DESC"] == "Sim").astype(int)

    #Salvar Tabela Fato Principal
    arquivo_fato = GOLD_DIR / "fato_srag.parquet"
    df.to_parquet(arquivo_fato, index=False, engine="pyarrow")
    
    #Criar Tabela Agregada Semanal por Agente Etiológico
    resumo_semanal = df.groupby(["SEM_PRI", "CLASSI_FIN_DESC"], as_index=False).agg(
        total_casos=("FL_UTI", "count"),
        total_uti=("FL_UTI", "sum"),
        total_obitos=("FL_OBITO", "sum"),
        total_vacinados_cov=("FL_VACINADO_COV", "sum")
    )

    arquivo_resumo = GOLD_DIR / "agg_semanal_virus.parquet"
    resumo_semanal.to_parquet(arquivo_resumo, index=False, engine="pyarrow")

    print("Camada Gold gerada com sucesso!")
    print(f"- Fato SRAG salva em: {arquivo_fato}")
    print(f"- Agregado Semanal salvo em: {arquivo_resumo}")

if __name__ == "__main__":
    construir_camada_gold()