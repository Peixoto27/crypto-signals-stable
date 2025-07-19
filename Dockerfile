FROM python:3.9-slim

WORKDIR /app

# Copia apenas o requirements.txt primeiro
COPY requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Restante do seu Dockerfile...
