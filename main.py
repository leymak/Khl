import datetime
import os
import requests

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TG_CHANNEL_ID")

def get_tomorrow_matches():
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    date_str = tomorrow.strftime("%d.%m.%Y")
    api_date = tomorrow.strftime("%Y-%m-%d")

    url = f"https://khl.ru/api/v1/calendar?date={api_date}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code != 200:
            return date_str, []

        data = res.json()
        matches = []
        for match in data.get("matches", []):
            home_team = match.get("team_a", {}).get("name")
            guest_team = match.get("team_b", {}).get("name")
            start_time = match.get("time", "19:00")

            if home_team and guest_team:
                matches.append({
                    "home": home_team,
                    "guest": guest_team,
                    "time": start_time
                })
        return date_str, matches
    except Exception as e:
        print(f"Ошибка получения матчей: {e}")
        return date_str, []

def create_preview_text(date_str, matches):
    if not matches:
        return ""

    text = f"📅 *МАТЧИ КХЛ НА ЗАВТРА ({date_str})*\n\n"

    for match in matches:
        home = match["home"]
        guest = match["guest"]
        time = match["time"]

        text += f"🏒 *{home} — {guest}*\n"
        text += f"⏰ Начало: {time} (МСК)\n\n"
        text += f"Встречаются два принципиальных соперника. Хозяева льда ({home}) традиционно сильны дома и постараются диктовать свой темп, тогда как {guest} отлично умеет ловить оппонентов на контратаках и опасно разыгрывает большинство.\n\n"
        text += f"🔥 *Ожидания:*\n"
        text += f"Борьба за инициативу с первого периода. Вероятен близкий счёт (3:2 / 4:3) и высокая интрига до финальной сирены.\n"
        text += "—" * 15 + "\n\n"

    text += "📣 Подписывайтесь на канал, чтобы быть в курсе всех событий КХЛ!"
    return text

def send_to_telegram(text):
    if not text:
        print("Нет текста для отправки")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("Успешно опубликовано в Telegram!")
        else:
            print(f"Ошибка отправки: {response.text}")
    except Exception as e:
        print(f"Сетевой сбой: {e}")

def main():
    date_str, matches = get_tomorrow_matches()
    if not matches:
        print("Матчей на завтра не найдено.")
        return

    post_text = create_preview_text(date_str, matches)
    send_to_telegram(post_text)

if __name__ == "__main__":
    main()
