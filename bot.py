import requests
import asyncio
import os
from datetime import datetime, timedelta
from telegram import Bot

# ── CONFIG ───────────────────────────────────────────────────
# Load from environment variables (Railway) or config.py (local)
try:
    from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, OPENWEATHER_API_KEY, BALLDONTLIE_API_KEY, NEWS_API_KEY
except ImportError:
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
    OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
    BALLDONTLIE_API_KEY = os.environ.get("BALLDONTLIE_API_KEY")
    NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

# ── WEATHER ──────────────────────────────────────────────────
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Colombo,LK&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    description = data['weather'][0]['description'].capitalize()
    humidity = data['main']['humidity']
    return (f"🌤 <b>Weather — Colombo</b>\n"
            f"{description}\n"
            f"🌡 {temp}°C (feels like {feels_like}°C)\n"
            f"💧 Humidity: {humidity}%")

# ── F1 NEXT RACE ─────────────────────────────────────────────
def get_f1():
    url = "https://api.jolpi.ca/ergast/f1/current/next.json"
    response = requests.get(url)
    data = response.json()
    race = data['MRData']['RaceTable']['Races'][0]
    race_name = race['raceName']
    circuit = race['Circuit']['circuitName']
    country = race['Circuit']['Location']['country']
    date = race['date']
    return (f"🏎 <b>Formula 1 — Next Race</b>\n"
            f"{race_name}\n"
            f"📍 {circuit}, {country}\n"
            f"📅 {date}")

# ── F1 LAST RACE RESULT ──────────────────────────────────────
def get_f1_race_result():
    url = "https://api.jolpi.ca/ergast/f1/2026/last/results.json"
    response = requests.get(url)
    data = response.json()

    try:
        race = data['MRData']['RaceTable']['Races'][0]
        race_date = race['date']
        race_name = race['raceName']
        results = race['Results']

        # Only show if race was in the last 7 days
        race_dt = datetime.strptime(race_date, "%Y-%m-%d")
        if datetime.now() - race_dt > timedelta(days=7):
            return None

        msg = f"🏁 <b>Last Race Result — {race_name}</b>\n\n"
        for result in results[:3]:
            pos = result['position']
            driver = f"{result['Driver']['givenName']} {result['Driver']['familyName']}"
            team = result['Constructor']['name']
            time = result['Time']['time'] if 'Time' in result else result['status']
            msg += f"{pos}. {driver} ({team}) — {time}\n"

        fastest = sorted(
            [r for r in results if 'FastestLap' in r],
            key=lambda x: x['FastestLap']['rank']
        )[0]
        fastest_driver = f"{fastest['Driver']['givenName']} {fastest['Driver']['familyName']}"
        fastest_time = fastest['FastestLap']['Time']['time']
        msg += f"\n⚡ Fastest Lap: {fastest_driver} — {fastest_time}"

        return msg
    except Exception:
        return None

# ── NBA ───────────────────────────────────────────────────────
def get_nba():
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    url = f"https://api.balldontlie.io/v1/games?per_page=5&start_date={week_ago}&end_date={today}"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    games = data['data']

    if not games:
        return "🏀 <b>NBA</b> — No games in the last 7 days (off season)"

    msg = "🏀 <b>NBA — Recent Games</b>\n"
    for game in games[:3]:
        home = game['home_team']['full_name']
        visitor = game['visitor_team']['full_name']
        home_score = game['home_team_score']
        visitor_score = game['visitor_team_score']
        date = game['date'][:10]
        msg += f"{visitor} {visitor_score} @ {home} {home_score} ({date})\n"
    return msg.strip()

# ── TECH NEWS ─────────────────────────────────────────────────
def get_tech_news():
    url = (f"https://newsapi.org/v2/top-headlines?"
           f"sources=techcrunch,the-verge,wired,ars-technica&"
           f"pageSize=3&apiKey={NEWS_API_KEY}")
    response = requests.get(url)
    data = response.json()
    articles = data['articles']

    if not articles:
        return "📱 <b>Tech News</b> — No headlines available"

    msg = "📱 <b>Tech News</b>\n\n"
    for article in articles:
        title = article['title']
        source = article['source']['name']
        msg += f"• {title} <i>({source})</i>\n\n"
    return msg.strip()
# ── SEND BRIEFING ─────────────────────────────────────────────
async def send_daily_briefing():
    bot = Bot(token=TELEGRAM_TOKEN)
    message = "🌅 <b>Good Morning! Here's your daily briefing:</b>\n\n"

    try:
        message += get_weather() + "\n\n"
    except Exception:
        message += "🌤 Weather unavailable\n\n"

    try:
        message += get_f1() + "\n\n"
    except Exception:
        message += "🏎 F1 unavailable\n\n"

    try:
        f1_result = get_f1_race_result()
        if f1_result:
            message += f1_result + "\n\n"
    except Exception:
        pass

    try:
        message += get_nba() + "\n\n"
    except Exception:
        message += "🏀 NBA unavailable\n\n"

    try:
        message += get_tech_news() + "\n\n"
    except Exception:
        message += "📱 Tech news unavailable\n\n"

    async with bot:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
    print("Briefing sent!")

# ── MAIN LOOP ─────────────────────────────────────────────────
async def main():
    await send_daily_briefing()
    while True:
        now = datetime.now()
        if now.hour == 3 and now.minute == 30:
            await send_daily_briefing()
            await asyncio.sleep(61)
        await asyncio.sleep(30)

print("Bot is running. Briefing scheduled for 9:00am daily.")
print("Press Ctrl+C to stop.")
asyncio.run(main())