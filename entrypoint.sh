#!/bin/bash
set -e

echo "Motorsport Reminder Bot arrancado..."
echo "Hora actual: $(date)"

# Guardar las variables de entorno para que cron las pueda usar
printenv | grep -E 'TELEGRAM_|TZ=' > /etc/environment

# Crear el crontab correcto (SIN el usuario "root")
echo "0 9 * * * . /etc/environment; /usr/local/bin/python /app/motorsport_reminders.py >> /var/log/cron.log 2>&1" > /etc/cron.d/motorsport
chmod 0644 /etc/cron.d/motorsport

# También lo instalamos en el crontab de root (por compatibilidad)
crontab -r 2>/dev/null || true
echo "0 9 * * * . /etc/environment; /usr/local/bin/python /app/motorsport_reminders.py >> /var/log/cron.log 2>&1" | crontab -

echo "Cron programado a las 09:00 todos los días"
echo "Variables de entorno guardadas:"
cat /etc/environment

# Arrancar cron en primer plano
cron -f
