# 🏎️ Motorsport Reminder Bot

**Nunca más te pierdas una carrera.**

Bot automático que te envía recordatorios por **Telegram** 2-3 días antes de los eventos más importantes del motorsport mundial.

---

### Series incluidas

| Categoría          | Series                                      |
|--------------------|---------------------------------------------|
| **Fórmula**        | Formula 1                                   |
| **Motociclismo**   | MotoGP • WorldSBK                           |
| **Resistencia**    | WEC • ELMS • IMSA                           |
| **Rally**          | WRC • ERC                                   |
| **GT / Turismo**   | Super GT • GT World Challenge Europe • DTM  |

Muchas de estas series tienen **streams gratuitos en YouTube** o están disponibles en DAZN.

---

### Características

- ✅ 100% automático (Docker + cron)
- ✅ Recordatorios 2 y 3 días antes
- ✅ Hora local de España (Europe/Madrid)
- ✅ Evita enviar el mismo aviso dos veces
- ✅ Fácil de ampliar con más series
- ✅ Soporte para eventos locales personalizados
- ✅ Pensado para Raspberry Pi y cualquier servidor

---

### Instalación rápida

```bash
# 1. Clona el repositorio
git clone https://github.com/TU_USUARIO/motorsport-reminder-bot.git
cd motorsport-reminder-bot

# 2. Edita el docker-compose.yml y pon tus credenciales de Telegram
nano docker-compose.yml

# 3. Levanta el bot
docker compose up -d --build
Listo. El bot se ejecutará todos los días a las 09:00 (hora de España).
```
---

### Configuración de Telegram

Habla con @BotFather → /newbot
Copia el token
Envía cualquier mensaje a tu bot
Abre esta URL en el navegador (sustituye TU_TOKEN):

https://api.telegram.org/botTU_TOKEN/getUpdates

Busca "chat":{"id": 123456789} → ese es tu CHAT_ID

Pon ambos valores en el docker-compose.yml:
YAMLenvironment:
  - TELEGRAM_TOKEN=123456:ABC-DEF...
  - TELEGRAM_CHAT_ID=123456789

---

### Comandos útiles
Ver logs en tiempo real
```bash
docker logs -f motorsport-reminder-bot
```
#### Forzar una ejecución ahora mismo
```bash
docker exec motorsport-reminder-bot python /app/motorsport_reminders.py
```
#### Ver qué avisos se han enviado
```bash
cat data/sent_today.json
```
---

### Estructura del proyecto

```bash
textmotorsport-reminder-bot/
├── motorsport_reminders.py   # Lógica principal
├── requirements.txt
├── Dockerfile
├── entrypoint.sh
├── docker-compose.yml
└── data/                     # Persistencia (se crea automáticamente)
    ├── sent_today.json
    └── eventos_locales.json
```
---

### Personalización

Cambiar la hora de ejecución → edita el Dockerfile (línea del cron)

Añadir/quitar series → edita el diccionario FEEDS en motorsport_reminders.py

Cambiar los días de antelación → modifica DIAS_AVISO = [2, 3]

---

### Créditos de calendarios
Los feeds ICS provienen principalmente de:

toomuchracing.com

Better F1 Calendar

Hecho con ❤️ para los aficionados al motorsport.
