FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/api

# Copy the rest of the application
COPY . .

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application with reload
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app"] 