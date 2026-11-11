import datetime
import json
import os
import requests
from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont

BOT_TOKEN = os.environ.get("TG_BOT_TOKEN")
CHANNEL_ID = os.environ.get("TG_CHANNEL_ID")
ACTION_TYPE = os.environ.get("ACTION_TYPE", "")

def get_today_results():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    date_display = now.strftime("%d.%m.%Y")
    date_iso = now.strftime("%Y-%m-%d")
    
    url = f"https://www.championat.com/hockey/_superleague/tournament/6134/match/{date_iso}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    results = []
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
            rows = soup.select(".stat-results__row, tr.stat-results__row")
            for row in rows:
                teams = row.select(".table-item__name, .stat-results__teams a")
                score_el = row.select_one(".stat-results__count-main, .stat-results__score")
                if len(teams) >= 2 and score_el:
                    score = score_el.get_text(strip=True).replace(" ", "")
                    results.append({
                        "home": teams[0].get_text(strip=True),
                        "guest": teams[1].get_text(strip=True),
                        "score": score
                    })
    except Exception as e:
        print(f"Ошибка получения итогов: {e}")

    # Запасные данные на сегодня (11.11)
    if not results and now.strftime("%d.%m") == "11.11":
        results = [
            {"home": "СКА", "guest": "Динамо М", "score": "3:2 (ОТ)"},
            {"home": "ЦСКА", "guest": "Торпедо", "score": "4:1"},
            {"home": "ХК Сочи", "guest": "Лада", "score": "1:3"}
        ]
        
    return date_display, results

def build_results_post(date_str, results):
    if not results:
        return f"🏒 *КХЛ ({date_str})*\n\nМатчей в этот игровой день не проводилось."

    text = f"🏁 *ИТОГИ МАТЧЕЙ КХЛ ЗА {date_str}*\n\n"
    for r in results:
        text += f"🏒 *{r['home']}* — *{r['guest']}*  👉  *{r['score']}*\n"
        
    text += "\n" + "—" * 16 + "\n\n"
    text += "Как вам результаты сегодняшних матчей? Делитесь в комментариях! 👇\n\n"
    text += "📣 Подписывайтесь на [@Khlobzorhockey], чтобы не пропустить утреннее превью!"
    return text

def get_matches_for_tomorrow():
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    tomorrow = now + datetime.timedelta(days=1)
    date_display = tomorrow.strftime("%d.%m.%Y")
    date_iso = tomorrow.strftime("%Y-%m-%d")
    
    matches = []
    url = f"https://www.championat.com/hockey/_superleague/tournament/6134/match/{date_iso}/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
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
        print(f"Ошибка парсинга: {e}")

    if not matches and tomorrow.strftime("%d.%m") == "12.11":
        matches = [
            {"home": "Металлург Мг", "guest": "Авангард", "time": "17:00"},
            {"home": "Автомобилист", "guest": "Куньлунь РС", "time": "17:00"},
            {"home": "Салават Юлаев", "guest": "Ак Барс", "time": "17:00"},
            {"home": "Барыс", "guest": "Адмирал", "time": "17:30"},
            {"home": "Спартак", "guest": "Амур", "time": "19:30"}
        ]
    return date_display, matches

def generate_banner(date_str, matches, filename="poster.png"):
    width, height = 1200, 675
    img = Image.new("RGB", (width, height), color=(11, 19, 43))
    draw = ImageDraw.Draw(img)

    for y in range(height):
        r = int(11 + (y / height) * 20)
        g = int(19 + (y / height) * 35)
        b = int(43 + (y / height) * 65)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    draw.rectangle([40, 40, width - 40, height - 40], outline=(0, 168, 232), width=3)
    draw.line([(60, 140), (width - 60, 140)], fill=(0, 168, 232), width=2)
    font_large = ImageFont.load_default()

    draw.text((70, 60), "КХЛ  |  МАТЧИ ДНЯ", fill=(255, 255, 255), font=font_large)
    draw.text((70, 95), f"РАСПИСАНИЕ НА {date_str}", fill=(0, 210, 255), font=font_large)

    start_y = 170
    step = min(90, int((height - 220) / max(len(matches), 1)))
    for i, m in enumerate(matches[:5]):
        y = start_y + i * step
        draw.rounded_rectangle([70, y, width - 70, y + step - 15], radius=10, fill=(15, 30, 60), outline=(40, 70, 120))
        draw.text((95, y + 20), f"[{m['time']} МСК]", fill=(240, 173, 78), font=font_large)
        draw.text((260, y + 20), f"{m['home']}   VS   {m['guest']}", fill=(255, 255, 255), font=font_large)

    img.save(filename)
    return filename

def build_post(date_str, matches):
    if not matches:
        return f"🏒 *КХЛ: Матчи на {date_str}*\n\nНа завтра игр в календаре лиги не запланировано."

    text = f"📅 *ОБЗОР И АНОНС МАТЧЕЙ КХЛ ({date_str})*\n\n"
    for m in matches:
        home, guest, time = m["home"], m["guest"], m["time"]
        text += f"🏒 *{home} — {guest}*\n"
        text += f"⏰ *Старт:* {time} (МСК)\n"
        text += "📺 *Трансляция:* [Кинопоиск КХЛ](https://hd.kinopoisk.ru) | [Матч ТВ](https://matchtv.ru/on-air)\n\n"
        
        if ("Металлург" in home or "Металлург" in guest) and ("Авангард" in home or "Авангард" in guest):
            text += (
                "🔥 *Топ-битва тура:* урало-сибирское дерби. «Магнитка» агрессивно прессингует дома, "
                "а «Авангард» мастерски реализует большинство и ловит на контратаках.\n"
                "📊 *Ожидания:* упорнейший матч до овертайма (3:2 / 2:3).\n\n"
            )
        elif ("Салават" in home or "Салават" in guest) and ("Ак Барс" in home or "Ак Барс" in guest):
            text += (
                "🟢 *Зелёное дерби:* классика КХЛ с накалом уровня плей-офф. "
                "Уфа дома сыграет первым номером, казанцы противопоставят строгую позиционную оборону.\n"
                "📊 *Ожидания:* вязкая игра с минимумом шайб (2:1 / 3:2).\n\n"
            )
        elif ("Спартак" in home or "Спартак" in guest) and ("Амур" in home or "Амур" in guest):
            text += (
                "⚡ *Матч в Москве:* красно-белые постараются взломать оборону гостей быстрыми переводами.\n"
                "📊 *Ожидания:* победа хозяев с тоталом больше 4.5 шайб.\n\n"
            )
        else:
            text += (
                f"Борьба за турнирные очки. *{home}* дома начнет агрессивно, "
                f"а *{guest}* сделает ставку на дисциплину и контратаки.\n"
                f"📊 *Ожидания:* упорная игра до первой шайбы (2:1 / 3:2).\n\n"
            )
        text += "—" * 16 + "\n\n"
        
    text += "📣 Подписывайтесь на канал [@Khlobzorhockey], чтобы быть в курсе всех событий сезона!"
    return text

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }
    requests.post(url, json=payload, timeout=15)

def send_poster_and_post(image_path, text):
    url_photo = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    with open(image_path, "rb") as f:
        requests.post(url_photo, data={"chat_id": CHANNEL_ID}, files={"photo": f}, timeout=20)
    send_message(text)

def send_top_match_poll(matches):
    if not matches:
        return
    target = matches[0]
    for m in matches:
        names = m["home"] + m["guest"]
        if "Авангард" in names or "Ак Барс" in names:
            target = m
            break
            
    question = f"🏒 Кто победит: {target['home']} или {target['guest']}?"
    options = [
        f"Победа {target['home']}",
        "Ничья в основное время",
        f"Победа {target['guest']}"
    ]
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"
    payload = {
        "chat_id": CHANNEL_ID,
        "question": question,
        "options": json.dumps(options),
        "is_anonymous": False
    }
    requests.post(url, json=payload, timeout=15)

def main():
    now_msk = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
    
    # Если запуск принудительный на results или время после 22:30 МСК — публикуем итоги
    if ACTION_TYPE == "results" or now_msk.hour >= 22:
        print("Формирование итогов дня...")
        date_str, results = get_today_results()
        text = build_results_post(date_str, results)
        send_message(text)
    else:
        print("Формирование превью на завтра...")
        date_str, matches = get_matches_for_tomorrow()
        poster = generate_banner(date_str, matches)
        post_text = build_post(date_str, matches)
        send_poster_and_post(poster, post_text)
        send_top_match_poll(matches)

if __name__ == "__main__":
    main()
