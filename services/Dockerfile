FROM python:3.9-slim

WORKDIR /app

# Copiar os arquivos necessários
COPY services/ /app/services/
COPY api/ /app/api/
COPY requirements.txt /app/

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

# Adicionar o diretório api ao PYTHONPATH
ENV PYTHONPATH=/app

# Comando para iniciar o gerenciador de serviços
CMD ["python", "services/run_services.py"] 