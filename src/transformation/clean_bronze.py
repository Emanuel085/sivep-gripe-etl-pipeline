import sys
import pandas as pd
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from src.config import (
    BRONZE_DIR, SILVER_DIR, COLUNAS_SELECIONADAS,
    MAPEAMENTO_CLASSI_FIN, MAPEAMENTO_EVOLUCAO, MAPEAMENTO_SIM_NAO
)

def processar_camada_silver():
    arquivo_bronze = BRONZE_DIR / "sivep_gripe_raw.csv"
    arquivo_silver = SILVER_DIR / "sivep_gripe_clean.parquet"

    if not arquivo_bronze.exists():
        print(f"Erro: O arquivo {arquivo_bronze} não foi encontrado!")
        return

    print("Iniciando o processamento da Camada Silver...")
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    #Carregar CSV completo das colunas (sem usecols restritivo no momento da leitura para evitar perder colunas)
    df = pd.read_csv(
        arquivo_bronze,
        sep=";",
        encoding="utf-8",
        low_memory=False
    )

    #Normalizar nomes das colunas (remover espaços nas pontas)
    df.columns = df.columns.str.strip()

    #Manter apenas as colunas que realmente existem na base
    cols_presentes = [c for c in COLUNAS_SELECIONADAS if c in df.columns]
    df = df[cols_presentes].copy()

    print(f"Registros carregados: {len(df):,}")

    #Mapeamento robusto de CLASSI_FIN
    if "CLASSI_FIN" in df.columns:
        #Converte valores numéricos mantendo nulos
        s_classi = pd.to_numeric(df["CLASSI_FIN"], errors="coerce")
        df["CLASSI_FIN_DESC"] = s_classi.map(MAPEAMENTO_CLASSI_FIN)
        df["CLASSI_FIN_DESC"] = df["CLASSI_FIN_DESC"].fillna("Não Informado / Em Investigação")
    else:
        df["CLASSI_FIN_DESC"] = "Não Informado / Em Investigação"

    #Mapeamento de Evolução
    if "EVOLUCAO" in df.columns:
        s_evol = pd.to_numeric(df["EVOLUCAO"], errors="coerce")
        df["EVOLUCAO_DESC"] = s_evol.map(MAPEAMENTO_EVOLUCAO).fillna("Não Informado")
    else:
        df["EVOLUCAO_DESC"] = "Não Informado"

    #Mapeamento de Sim/Não
    for col in ["UTI", "VACINA", "VACINA_COV"]:
        if col in df.columns:
            s_sn = pd.to_numeric(df[col], errors="coerce")
            df[f"{col}_DESC"] = s_sn.map(MAPEAMENTO_SIM_NAO).fillna("Não Informado")

    #Converter Datas
    cols_data = [c for c in df.columns if c.startswith("DT_")]
    for col in cols_data:
        df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")

    #Salvar em Parquet
    df.to_parquet(arquivo_silver, index=False, engine="pyarrow")
    print(f"Camada Silver gerada com sucesso! Colunas: {df.columns.tolist()}")

if __name__ == "__main__":
    processar_camada_silver()