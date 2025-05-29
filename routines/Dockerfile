FROM python:3.9-slim

WORKDIR /app

# Copiar os arquivos necessários
COPY routines/ /app/routines/
COPY api/ /app/api/
COPY requirements.txt /app/

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Adicionar o diretório routines ao PYTHONPATH
ENV PYTHONPATH=/app/routines

# Comando para iniciar o gerenciador de serviços
CMD ["python", "routines/run_services.py"] 