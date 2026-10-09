import sys
import requests
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.config import BRONZE_DIR, SIVEP_URL

#url de backup caso a principal nao funcione
SIVEP_URL_BACKUP = "https://s3.sa-east-1.amazonaws.com/ckan.sa-east-1.amazoniaweb.com.br/sivep-gripe/INFLUD22.csv"

def baixar_dados_sivep(url: str, destino: Path):
    """Baixa o arquivo CSV bruto do SIVEP-Gripe e salva na camada bronze"""
    print(f"Iniciando o download dos dados em: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()

        arquivo_final = destino / "sivep_gripe_raw.csv"

        with open(arquivo_final, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)

        print(f"Download concluído, arquivo salvo em: {arquivo_final}")
        return True

    except requests.exceptions.HTTPError as err:
        print(f"Erro HTTP ao tentar baixar: {err}")
        return False
    except Exception as e:
        print(f"Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    sucesso = baixar_dados_sivep(SIVEP_URL, BRONZE_DIR)

    #se falhar a priemira, tenta a de backup

    if not sucesso:
        print("\nTentando backup")
        baixar_dados_sivep(SIVEP_URL_BACKUP, BRONZE_DIR)