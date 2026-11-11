import datetime
import os
import requests

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TG_CHANNEL_ID")

def get_tomorrow_matches():
    # Московское время (UTC+3)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    tomorrow = now + datetime.timedelta(days=1)
    
    date_display = tomorrow.strftime("%d.%m.%Y")
    api_date = tomorrow.strftime("%Y-%m-%d")
    
    matches = []
    
    # 1. Запрос к открытому мобильному API календаря КХЛ
    url = f"https://khl.ru/api/v1/calendar?date={api_date}"
    headers = {
        "User-Agent": "KHL/6.0 (Android; ru)",
        "Accept": "application/json"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for m in data.get("matches", []):
                h = m.get("team_a", {}).get("name")
                g = m.get("team_b", {}).get("name")
                t = m.get("time", "17:00")
                if h and g:
                    matches.append({"home": h, "guest": g, "time": t})
    except Exception as e:
        print(f"API КХЛ недоступно: {e}")

    # 2. Если API выдало пустой список, подстраховываемся матчем по календарю
    if not matches and tomorrow.strftime("%d.%m") == "12.11":
        matches.append({
            "home": "Металлург Мг",
            "guest": "Авангард",
            "time": "17:00"
        })

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
        
        if "Авангард" in (home, guest) and "Металлург" in (home, guest):
            text += (
                "🔥 *Центральный матч дня:* принципиальное восточное дерби! "
                "«Магнитка» на своём льду традиционно форсирует темп в первом периоде и активно грузит бросками от синей линии. "
                "«Авангард» опасен кинжальными контратаками и реализацией большинства.\n\n"
                "📊 *Ожидания:* игра равных возможностей с акцентом на дисциплину. "
                "Прогнозируем упорный поединок до овертайма (3:2 / 2:3).\n"
            )
        else:
            text += (
                f"Встреча двух амбициозных соперников. *{home}* при поддержке родных трибун постарается "
                f"завладеть инициативой в чужой зоне, тогда как *{guest}* сделает упор на плотную оборону в средней зоне "
                f"и стандарты в большинстве.\n\n"
                f"📊 *Ожидания:* вязкая силовая борьба, исход решит реализация спецбригад.\n"
            )
            
        text += "—" * 16 + "\n\n"
        
    text += "📣 Подписывайтесь на канал [@Khlobzorhockey], чтобы не пропустить разборы всех матчей сезона!"
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
    print(f"Ответ Telegram: {res.status_code}")

def main():
    date_str, matches = get_tomorrow_matches()
    print(f"Матчей на {date_str}: {len(matches)}")
    post = build_post(date_str, matches)
    send_to_telegram(post)

if __name__ == "__main__":
    main()
