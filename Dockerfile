# Imagem base com Python 3.11
FROM python:3.11-slim

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala dependências
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta (Railway usa a env PORT)
EXPOSE 8000

# Comando de start
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"]
