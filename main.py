import datetime
import os
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TG_CHANNEL_ID")

def get_matches():
    # Пробуем получить матчи на завтра, а если их нет — на сегодня (для теста)
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3) # Московское время
    tomorrow = now + datetime.timedelta(days=1)
    
    date_str = tomorrow.strftime("%d.%m.%Y")
    
    # Надежный открытый спортивный источник расписания
    url = f"https://www.championat.com/hockey/_superleague/tournament/6134/match/{tomorrow.strftime('%Y-%m-%d')}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    matches = []
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.find_all("tr", class_="stat-results__row")
            for row in rows:
                teams = row.find_all("span", class_="table-item__name")
                time_tag = row.find("td", class_="stat-results__date-time")
                if len(teams) >= 2:
                    matches.append({
                        "home": teams[0].get_text(strip=True),
                        "guest": teams[1].get_text(strip=True),
                        "time": time_tag.get_text(strip=True) if time_tag else "19:00"
                    })
    except Exception as e:
        print(f"Ошибка парсинга Чемпионата: {e}")

    # Запасной вариант: если на завтра матчей нет или парсинг не нашел, проверим сегодня
    if not matches:
        print("На завтра матчей не найдено, проверяем текущий день для теста...")
        date_str = now.strftime("%d.%m.%Y")
        url_today = f"https://www.championat.com/hockey/_superleague/tournament/6134/match/{now.strftime('%Y-%m-%d')}/"
        try:
            res = requests.get(url_today, headers=headers, timeout=15)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, "html.parser")
                rows = soup.find_all("tr", class_="stat-results__row")
                for row in rows:
                    teams = row.find_all("span", class_="table-item__name")
                    time_tag = row.find("td", class_="stat-results__date-time")
                    if len(teams) >= 2:
                        matches.append({
                            "home": teams[0].get_text(strip=True),
                            "guest": teams[1].get_text(strip=True),
                            "time": time_tag.get_text(strip=True) if time_tag else "19:00"
                        })
        except Exception as e:
            print(f"Ошибка запасного парсинга: {e}")

    return date_str, matches

def create_preview_text(date_str, matches):
    if not matches:
        return f"📅 *КХЛ ({date_str})*\n\nНа выбранную дату матчей в расписании не запланировано."
        
    text = f"📅 *ОБЗОР МАТЧЕЙ КХЛ ({date_str})*\n\n"
    for match in matches:
        home = match["home"]
        guest = match["guest"]
        time = match["time"]
        
        text += f"🏒 *{home} — {guest}*\n"
        text += f"⏰ Начало: {time} (МСК)\n\n"
        text += f"Команды подходят к очной встрече с максимальным настроем на результат. "
        text += f"*{home}* традиционно опирается на поддержку домашних трибун и давление в чужой зоне. "
        text += f"*{guest}* сделает ставку на дисциплину, игру в меньшинстве и контратаки.\n\n"
        text += f"🔥 *Прогноз*: ожидается равная борьба с акцентом на реализацию численного преимущества. Вероятен близкий счёт (3:2 или 4:2).\n"
        text += "—" * 15 + "\n\n"
        
    text += "📣 Подписывайтесь на канал, чтобы не пропустить ежедневные разборы!"
    return text

def send_to_telegram(text):
    print(f"Отправка сообщения в канал {CHANNEL_ID}...")
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    
    res = requests.post(url, json=payload, timeout=15)
    print(f"Ответ Telegram: {res.status_code} - {res.text}")

def main():
    date_str, matches = get_matches()
    print(f"Найдено матчей: {len(matches)}")
    post_text = create_preview_text(date_str, matches)
    send_to_telegram(post_text)

if __name__ == "__main__":
    main()
