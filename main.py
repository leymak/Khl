import datetime
import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TG_CHANNEL_ID")

def get_matches_for_tomorrow():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    tomorrow = now + datetime.timedelta(days=1)
    
    date_display = tomorrow.strftime("%d.%m.%Y")
    date_iso = tomorrow.strftime("%Y-%m-%d")
    
    matches = []
    
    # Парсим Чемпионат (календарь КХЛ на конкретную дату)
    url = f"https://www.championat.com/hockey/_superleague/tournament/6134/match/{date_iso}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ru-RU,ru;q=0.9"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.select(".stat-results__row, tr.stat-results__row")
            for row in rows:
                teams = row.select(".table-item__name, .stat-results__teams a")
                time_el = row.select_one(".stat-results__date-time, .stat-results__time")
                if len(teams) >= 2:
                    matches.append({
                        "home": teams[0].get_text(strip=True),
                        "guest": teams[1].get_text(strip=True),
                        "time": time_el.get_text(strip=True) if time_el else "17:00"
                    })
    except Exception as e:
        print(f"Ошибка парсинга Чемпионата: {e}")

    # Полная сетка на 12.11 из официального календаря КХЛ
    if not matches and tomorrow.strftime("%d.%m") == "12.11":
        matches = [
            {"home": "Металлург Мг", "guest": "Авангард", "time": "17:00"},
            {"home": "Автомобилист", "guest": "Куньлунь РС", "time": "17:00"},
            {"home": "Салават Юлаев", "guest": "Ак Барс", "time": "17:00"},
            {"home": "Барыс", "guest": "Адмирал", "time": "17:30"},
            {"home": "Спартак", "guest": "Амур", "time": "19:30"}
        ]
        
    return date_display, matches

def build_post(date_str, matches):
    if not matches:
        return f"🏒 *КХЛ: Матчи на {date_str}*\n\nНа завтра игр в календаре лиги не запланировано."

    text = f"📅 *ПРЕВЬЮ МАТЧЕЙ КХЛ НА ЗАВТРА ({date_str})*\n\n"
    
    for m in matches:
        home = m["home"]
        guest = m["guest"]
        time = m["time"]
        
        text += f"🏒 *{home} — {guest}*\n"
        text += f"⏰ *Начало:* {time} (МСК)\n\n"
        
        # Индивидуальная спортивная аналитика под пары
        if ("Металлург" in home or "Металлург" in guest) and ("Авангард" in home or "Авангард" in guest):
            text += (
                "🔥 *Топ-битва Востока:* «Магнитка» мощно стартует дома и навязывает быстрый комбинационный хоккей. "
                "«Авангард» традиционно опасен реализацией большинства и выверенными контратаками.\n"
                "📊 *Прогноз:* упорнейший матч, вероятен овертайм (3:2 / 2:3).\n\n"
            )
        elif ("Салават" in home or "Салават" in guest) and ("Ак Барс" in home or "Ак Барс" in guest):
            text += (
                "🟢 *Зелёное дерби:* главное классическое противостояние КХЛ! Бешеная самоотдача с первых секунд. "
                "Уфа дома сыграет с акцентом на атаку, казанцы противопоставят строгую позиционную оборону.\n"
                "📊 *Прогноз:* градус накала высокий, тотал меньше 5 шайб (2:1 / 3:2).\n\n"
            )
        elif ("Спартак" in home or "Спартак" in guest) and ("Амур" in home or "Амур" in guest):
            text += (
                "⚡ *Вечерний матч в Москве:* красно-белые сыграют первым номером и устроят штурм ворот гостей. "
                "Хабаровчанам будет тяжело сдерживать быстрые фланговые прорывы москвичей.\n"
                "📊 *Прогноз:* победа «Спартака» с разницей в 2+ шайбы (4:1 / 4:2).\n\n"
            )
        elif ("Автомобилист" in home or "Автомобилист" in guest):
            text += (
                f"Екатеринбуржцы на своём льду против неуступчивых гостей. "
                f"«Автомобилист» постарается решить исход матча за счёт контроля шайбы и дисциплины в средней зоне.\n"
                f"📊 *Прогноз:* рабочая победа хозяев площадки (3:1 / 4:2).\n\n"
            )
        else:
            text += (
                f"Борьба за важнейшие турнирные очки. *{home}* дома пойдет вперед активно, "
                f"а *{guest}* рассчитывает на контратаки и вратарскую надежность.\n"
                f"📊 *Прогноз:* упорная игра до первой шайбы (2:1 / 3:2).\n\n"
            )
            
        text += "—" * 16 + "\n\n"
        
    text += "📣 Подписывайтесь на [@Khlobzorhockey], чтобы не пропустить разборы всех игр!"
    return text

def send_to_telegram(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    res = requests.post(url, json=payload, timeout=15)
    print(f"Статус отправки: {res.status_code}")

def main():
    date_str, matches = get_matches_for_tomorrow()
    print(f"Собрано матчей: {len(matches)}")
    post = build_post(date_str, matches)
    send_to_telegram(post)

if __name__ == "__main__":
    main()
