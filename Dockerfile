FROM python:3.9-slim

WORKDIR /app

# ========== NOVAS INSTRUÇÕES ==========
# 1. Instala dependências de sistema
RUN apt-get update && \
    apt-get install -y \
    libta-lib-dev \      # Biblioteca TA-Lib
    gcc \                # Compilador C
    python3-dev \        # Headers Python
    wget \               # Para baixar o TA-Lib
    make \               # Para compilar
    && rm -rf /var/lib/apt/lists/*

# 2. Instala TA-Lib manualmente
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib*       # Limpeza
# ========== FIM DAS NOVAS INSTRUÇÕES ==========

# Copia e instala requirements
COPY requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

# Copia o código fonte
COPY src/ .

EXPOSE 8000
CMD ["gunicorn", "app.main:app", "--workers", "4", "--bind", "0.0.0.0:8000"]
