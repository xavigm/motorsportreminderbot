#!/bin/bash
set -e

echo "Motorsport Reminder Bot arrancado..."
echo "Hora actual: $(date)"
echo "Cron programado a las 09:00 todos los días"

# Arrancar cron en primer plano
cron -f
