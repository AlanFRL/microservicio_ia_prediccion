# Dockerfile para Microservicio IA - Predicción de Cancelaciones v4.0
# Incluye: MongoDB, Email Service, Cron Job, ML Model

FROM python:3.11-slim

# Metadatos
LABEL maintainer="alanfromerol@gmail.com"
LABEL version="4.0"
LABEL description="Microservicio de IA para predicción de cancelaciones con MongoDB y Email"

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements primero (para aprovechar cache de Docker)
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código de la aplicación
COPY app/ ./app/
COPY main_v4.py .

# Exponer puerto 8001
EXPOSE 8001

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Health check para Kubernetes
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health')" || exit 1

# Comando para ejecutar la aplicación
CMD ["python", "main_v4.py"]
