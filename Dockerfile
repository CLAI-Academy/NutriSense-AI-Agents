# Dockerfile
FROM python:3.12-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar pip y herramientas de build
RUN pip install --upgrade pip setuptools wheel

# Copiar archivos de configuración y README
COPY pyproject.toml ./
COPY requirements.txt ./

# Crear README.md si no existe (requerido por pyproject.toml)
RUN touch README.md

# Instalar dependencias primero desde requirements.txt (más rápido para cache)
RUN pip install -r requirements.txt

# Copiar el código de la aplicación
COPY nutrisense_agents/ ./nutrisense_agents/

# Instalar el proyecto en modo editable
RUN pip install -e .

# Variables de entorno
ENV PYTHONPATH=/app

# Comando para ejecutar la aplicación - usar variable PORT de Cloud Run
CMD uvicorn nutrisense_agents.main:app --host 0.0.0.0 --port ${PORT:-8000}