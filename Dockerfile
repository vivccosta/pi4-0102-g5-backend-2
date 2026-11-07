FROM python:3.12-slim

# Evita criação de arquivos .pyc e garante logs em tempo real no console
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    BLOCKCHAIN_STORAGE_PATH=/app/data/blockchain.json

WORKDIR /app

# Cria diretório para persistência da cadeia em disco
RUN mkdir -p /app/data

# Instala a biblioteca websockets a partir do requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copia os códigos-fonte da aplicação
COPY src/ /app/

EXPOSE 8000

CMD ["python", "servidor.py"]
