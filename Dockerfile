FROM python:3.12-slim

# Evitar archivos .pyc y habilitar salida sin buffer en logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Instalar dependencias del sistema necesarias para psycopg2 y compilación
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar código fuente del proyecto
COPY . .

# Recolectar archivos estáticos usando SQLite temporalmente durante el build
RUN USE_SQLITE=True python manage.py collectstatic --noinput

EXPOSE 8000

# Aplicar migraciones automáticamente e iniciar servidor de producción Gunicorn
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 4 --timeout 120"]
