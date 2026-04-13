# Usar imagen oficial de Python ligera
FROM python:3.11-slim

# Evitar que Python escriba archivos .pyc y activar logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar ciertas librerías
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del proyecto
COPY . .

# AJUSTE AUTOMÁTICO: Usar configuración de producción incrustada
COPY .env.production .env

# Exponer el puerto 8000
EXPOSE 8000

# Comando de arranque (usando Gunicorn/Uvicorn para producción)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
