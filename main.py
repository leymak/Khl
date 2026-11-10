import datetime
import os
import requests
from google import genai

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TG_CHANNEL_ID")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_tomorrow_matches():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    date_str = tomorrow.strftime("%Y-%m-%d")
    
    # Открытый API календаря КХЛ
    url = f"https://khl.ru/api/v1/calendar?date={date_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        matches = []
        for match in data.get("matches", []):
            team_a = match.get("team_a", {}).get("name")
            team_b = match.get("team_b", {}).get("name")
            start_time = match.get("time", "19:00")
            if team_a and team_b:
                matches.append({"home": team_a, "guest": team_b, "time": start_time})
        return date_str, matches
    except Exception as e:
        print(f"Ошибка получения расписания: {e}")
        return date_str, []

def generate_preview(client, home, guest, time_str, date_str):
    prompt = f"""
Ты спортивный аналитик КХЛ. Сделай краткое, ёмкое превью на матч завтра ({date_str}, начало в {time_str} МСК):
{home} vs {guest}.

Формат сообщения строго в Markdown (для Telegram):
🏒 *{home} — {guest}* (Начало: {time_str} МСК)

• *Текущая форма*: 1-2 предложения о состоянии команд и их последних результатах в сезоне 2026.
• *Ключевой фактор*: площадка, мотивация, спецбригады большинства/меньшинства или лидеры.
• *Прогноз*: ожидаемый исход и возможный счёт (например, 3:2 или 4:1).

Пиши экспертно, коротко и без лишних предисловий.
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text

def send_tg(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload, timeout=15)

def main():
    date_str, matches = get_tomorrow_matches()
    if not matches:
        print("На завтра матчей не найдено.")
        return

    client = genai.Client(api_key=GEMINI_API_KEY)
    
    for match in matches:
        preview_text = generate_preview(client, match["home"], match["guest"], match["time"], date_str)
        send_tg(preview_text)
        print(f"Опубликован матч {match['home']} - {match['guest']}")

if __name__ == "__main__":
    main()
