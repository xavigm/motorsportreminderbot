FROM python:3.12-slim

# Zona horaria España
ENV TZ=Europe/Madrid
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Instalar cron y dependencias mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    cron \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY motorsport_reminders.py .

# Crear directorio de datos persistentes
RUN mkdir -p /data

# Configurar cron (todos los días a las 09:00 hora España)
RUN echo "0 9 * * * root /usr/local/bin/python /app/motorsport_reminders.py >> /var/log/cron.log 2>&1" > /etc/cron.d/motorsport \
    && chmod 0644 /etc/cron.d/motorsport \
    && crontab /etc/cron.d/motorsport \
    && touch /var/log/cron.log

# Script de arranque que mantiene el contenedor vivo
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
