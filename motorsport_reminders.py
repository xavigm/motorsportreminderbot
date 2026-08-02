#!/usr/bin/env python3
"""
Motorsport Reminder Bot
Recordatorios automáticos de F1, MotoGP, WSBK, WEC, WRC, ERC, ELMS, IMSA, Super GT, GTWC Europe y DTM.
"""

import os
import json
import requests
from icalendar import Calendar
from datetime import datetime, timezone
from pathlib import Path
import pytz

# ============== CONFIGURACIÓN DESDE VARIABLES DE ENTORNO ==============
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    raise ValueError("Faltan TELEGRAM_TOKEN o TELEGRAM_CHAT_ID en las variables de entorno")

# Días de antelación
DIAS_AVISO = [2, 3]

# Zona horaria España
TZ = pytz.timezone("Europe/Madrid")

# Feeds ICS
FEEDS = {
    "F1": "https://better-f1-calendar.vercel.app/api/calendar.ics",
    "MotoGP": "https://calendar.google.com/calendar/ical/832vbii8pmrvma356b4vn3v42c%40group.calendar.google.com/public/basic.ics",
    "WorldSBK": "https://calendar.google.com/calendar/ical/0rts2iu5gd88eis52c084ltlhc%40group.calendar.google.com/public/basic.ics",
    "WEC": "https://calendar.google.com/calendar/ical/61jccgg4rshh1temqk0dj4lens%40group.calendar.google.com/public/basic.ics",
    "WRC": "https://calendar.google.com/calendar/ical/fei68gpe16c85ed3jjdtvrn8ns%40group.calendar.google.com/public/basic.ics",
    "ERC": "https://calendar.google.com/calendar/ical/tqcc98soldjf5ofrgmjc70eulk%40group.calendar.google.com/public/basic.ics",
    "ELMS": "https://calendar.google.com/calendar/ical/ur7thj1o6ctignecm0uia024js%40group.calendar.google.com/public/basic.ics",
    "IMSA": "https://calendar.google.com/calendar/ical/njulhksvo83qeoruc3nhend9js%40group.calendar.google.com/public/basic.ics",
    "Super GT": "https://calendar.google.com/calendar/ical/5ni9rjbofnkfvmpidmjpep9ek0%40group.calendar.google.com/public/basic.ics",
    "GTWC Europe": "https://calendar.google.com/calendar/ical/drne83rrmn7m9baje25qh2248s%40group.calendar.google.com/public/basic.ics",
    "DTM": "https://calendar.google.com/calendar/ical/0urnjij5qqj3ijoht52fdsqk18%40group.calendar.google.com/public/basic.ics",
}

STREAMING = {
    "F1": "DAZN / Movistar+",
    "MotoGP": "DAZN",
    "WorldSBK": "Eurosport / DAZN",
    "WEC": "YouTube oficial WEC (gratis) + Eurosport",
    "WRC": "DAZN (frecuentemente gratis) + Rally.TV",
    "ERC": "DAZN / Rally.TV + YouTube (algunas etapas)",
    "ELMS": "YouTube FIAWEC+ (gratis)",
    "IMSA": "YouTube oficial IMSA (gratis fuera de EE.UU.)",
    "Super GT": "YouTube oficial Super GT (gratis)",
    "GTWC Europe": "YouTube / DAZN",
    "DTM": "YouTube / DAZN",
}

# Persistencia dentro del contenedor
DATA_DIR = Path("/data")
SENT_FILE = DATA_DIR / "sent_today.json"
LOCAL_EVENTS_FILE = DATA_DIR / "eventos_locales.json"
# =====================================================================


def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    r = requests.post(url, json=payload, timeout=20)
    r.raise_for_status()


def load_sent() -> dict:
    if SENT_FILE.exists():
        try:
            return json.loads(SENT_FILE.read_text())
        except Exception:
            return {}
    return {}


def save_sent(data: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SENT_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def get_events_from_ics(url: str, serie: str) -> list:
    try:
        r = requests.get(url, timeout=25)
        r.raise_for_status()
        cal = Calendar.from_ical(r.content)
    except Exception as e:
        print(f"[{datetime.now()}] Error leyendo {serie}: {e}")
        return []

    events = []
    now = datetime.now(timezone.utc)

    for component in cal.walk():
        if component.name != "VEVENT":
            continue

        summary = str(component.get("SUMMARY", "Sin título"))
        dtstart = component.get("DTSTART")
        if not dtstart:
            continue

        start = dtstart.dt
        if not isinstance(start, datetime):
            start = datetime.combine(start, datetime.min.time())

        if start.tzinfo is None:
            start = pytz.UTC.localize(start)
        else:
            start = start.astimezone(pytz.UTC)

        if start < now:
            continue

        location = str(component.get("LOCATION", ""))
        description = str(component.get("DESCRIPTION", ""))[:180]

        events.append({
            "serie": serie,
            "title": summary,
            "start": start,
            "location": location,
            "description": description,
        })

    return events


def get_local_events() -> list:
    if not LOCAL_EVENTS_FILE.exists():
        return []
    try:
        data = json.loads(LOCAL_EVENTS_FILE.read_text())
        events = []
        now = datetime.now(timezone.utc)
        for e in data:
            start = datetime.fromisoformat(e["start"])
            if start.tzinfo is None:
                start = TZ.localize(start).astimezone(pytz.UTC)
            if start > now:
                events.append({
                    "serie": e.get("serie", "Local"),
                    "title": e["title"],
                    "start": start,
                    "location": e.get("location", ""),
                    "description": e.get("description", ""),
                })
        return events
    except Exception as e:
        print(f"[{datetime.now()}] Error eventos locales: {e}")
        return []


def main():
    print(f"[{datetime.now()}] Ejecutando Motorsport Reminder Bot...")

    all_events = []
    for serie, url in FEEDS.items():
        all_events.extend(get_events_from_ics(url, serie))

    all_events.extend(get_local_events())
    all_events.sort(key=lambda x: x["start"])

    now = datetime.now(timezone.utc)
    sent = load_sent()
    today_str = now.astimezone(TZ).strftime("%Y-%m-%d")

    # Primero intentamos la ventana normal (2 y 3 días)
    dias_a_buscar = list(DIAS_AVISO)  # [2, 3]
    mensajes = []
    dia_encontrado = None

    # Si no hay nada en 2-3 días, vamos ampliando de 1 en 1
    max_dias = 60  # límite de seguridad (2 meses)
    while not mensajes and dias_a_buscar[-1] <= max_dias:
        for event in all_events:
            delta = event["start"] - now
            dias = delta.days

            if dias not in dias_a_buscar:
                continue

            key = f"{event['serie']}_{event['title']}_{event['start'].date()}"
            if sent.get(key) == today_str:
                continue

            local_start = event["start"].astimezone(TZ)
            fecha_str = local_start.strftime("%A %d/%m/%Y %H:%M").capitalize()
            streaming = STREAMING.get(event["serie"], "Consulta web oficial")

            msg = (
                f"🏁 <b>{event['serie']}</b>\n"
                f"<b>{event['title']}</b>\n"
                f"📅 {fecha_str} (hora España)\n"
            )
            if event["location"]:
                msg += f"📍 {event['location']}\n"
            msg += f"📺 {streaming}\n"
            msg += f"⏳ Faltan {dias} días"

            mensajes.append(msg)
            sent[key] = today_str
            dia_encontrado = dias

        # Si no encontramos nada, ampliamos un día más
        if not mensajes:
            siguiente = dias_a_buscar[-1] + 1
            dias_a_buscar.append(siguiente)
            print(f"[{datetime.now()}] No hay eventos en {dias_a_buscar[:-1]}, probando con {siguiente} días...")

    if mensajes:
        # Añadimos una nota si no es la ventana normal de 2-3 días
        nota = ""
        if dia_encontrado not in DIAS_AVISO:
            nota = f"\n\nℹ️ No había eventos en 2-3 días. Mostrando el más cercano (faltan {dia_encontrado} días)."

        texto_final = "🏎️ <b>Próximos eventos de motorsport</b>\n\n" + "\n\n".join(mensajes) + nota
        send_telegram(texto_final)
        print(f"[{datetime.now()}] Enviados {len(mensajes)} recordatorios (día más cercano: {dia_encontrado})")
    else:
        print(f"[{datetime.now()}] No se encontró ningún evento en los próximos {max_dias} días")

    save_sent(sent)
    print(f"[{datetime.now()}] Listo.")

if __name__ == "__main__":
    main()
