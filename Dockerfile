FROM python:3.11-slim

# Instala dependências do sistema para compilar pacotes Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copia requirements para cache eficiente
COPY requirements.txt .

# Atualiza pip e instala libs
RUN python3.11 -m pip install --upgrade pip setuptools wheel
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Copia todo código da aplicação
COPY . .

# Expõe a porta padrão Flask (ajuste se quiser)
EXPOSE 8000

# Inicia Gunicorn, binding na porta 8000, usando app:app (arquivo app.py, variável app)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
