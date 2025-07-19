# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instala dependências do sistema (se necessário)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia e instala dependências Python
COPY requirements/base.txt ./requirements/
RUN pip install --no-cache-dir -r requirements/base.txt

# Copia o código fonte
COPY src/ .

# Porta da API
EXPOSE 8000

# Inicia a API
CMD ["gunicorn", "app.main:app", "--workers", "4", "--bind", "0.0.0.0:8000"]

