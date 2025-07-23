FROM python:3.11-slim

WORKDIR /app

# Copia só o requirements para cache melhor
COPY requirements.txt .

# Atualiza pip e instala dependências
RUN pip install --upgrade --no-cache-dir pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código depois para aproveitar cache anterior
COPY . .

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]


