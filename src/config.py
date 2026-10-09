import os
from pathlib import Path

#caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "1_bronze"
SILVER_DIR = BASE_DIR / "data" / "2_silver"
GOLD_DIR = BASE_DIR / "data" / "3_gold"

#garante que as pastas existam
BRONZE_DIR.mkdir(parents=True, exist_ok=True)

#url publica oficial dos dados do SIVEP-Gripe no OpenDataSus (exemplo de dados recentes)
SIVEP_URL = "https://s3.sa-east-1.amazonaws.com/ckan.sa-east-1.amazoniaweb.com.br/sivep-gripe/INFLUD21.csv"


#selecionar colunas do dicionario SIVEP-Gripe para o escopo

COLUNAS_SELECIONADAS = [
    #identificacao e localidade
    "DT_NOTIFIC", "SEM_NOT", "SG_UF_NOT", "CO_MUN_NOT",

    #perfil demografico
    "CS_SEXO", "NU_IDADE_N", "TP_IDADE", "CS_RACA",

    #evolucao temporal e clinica
    "DT_SIN_PRI", "SEM_PRI", "DT_INTERNA", "UTI", "DT_ENTUTI",
    "DT_SAIDUTI", "EVOLUCAO", "DT_EVOLUCA",

    #etiologia / diagnostico (virus)
    "CLASSI_FIN", "PCR_RESUL", "RES_AN", "POS_AN_FLU", "POS_AN_OUT",

    #vacinacao
    "VACINA", "VACINA_COV", "DOSE_1_COV", "DOSE_2_COV"
]

#dicionario de mapeamento para rotulos amigaveis (camada silver)
MAPEAMENTO_CLASSI_FIN = {
    1: "Influenza",
    1.0: "Influenza",
    2: "Outro Vírus Respiratório",
    2.0: "Outro Vírus Respiratório",
    3: "Outro Agente Etiológico",
    3.0: "Outro Agente Etiológico",
    4: "Não Especificado",
    4.0: "Não Especificado",
    5: "COVID-19",
    5.0: "COVID-19"
}

MAPEAMENTO_EVOLUCAO = {
    1: "Cura",
    2: "Óbito por SRAG",
    3: "Óbito por Outras Causas",
    9: "Ignorado"
}

MAPEAMENTO_SIM_NAO = {
    1: "Sim",
    2: "Não",
    9: "Ignorado"
}


