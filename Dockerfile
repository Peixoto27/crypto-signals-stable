FROM python:3.9-slim

WORKDIR /app

# Dependências de sistema
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instala TA-Lib (análise técnica)
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
    tar -xvzf ta-lib-0.4.0-src.tar.gz && \
    cd ta-lib/ && \
    ./configure --prefix=/usr && \
    make && \
    make install

COPY ./requirements/prod.txt .
RUN pip install --no-cache-dir -r prod.txt

COPY src/ .

EXPOSE 8000
