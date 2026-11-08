# Usa uma imagem oficial e leve do Python 3.12
FROM python:3.12-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia o ficheiro de dependências primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as bibliotecas do Python sem guardar cache de instalação
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do projeto para dentro do container
COPY . .

# Expõe a porta padrão do Streamlit (8501)
EXPOSE 8501

# Comando padrão ao iniciar o container: executa o painel
CMD ["streamlit", "run", "app/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]