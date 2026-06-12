import requests
import schedule
import time
from telegram import Bot
import os
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY")
BALLDONTLIE_API_KEY = os.environ.get("BALLDONTLIE_API_KEY")

# ── WEATHER ──────────────────────────────────────────────────
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Colombo,LK&appid={OPENWEATHER_API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    description = data['weather'][0]['description'].capitalize()
    humidity = data['main']['humidity']
    return (f"🌤 *Weather — Colombo*\n"
            f"{description}\n"
            f"🌡 {temp}°C (feels like {feels_like}°C)\n"
            f"💧 Humidity: {humidity}%")

# ── FORMULA 1 ─────────────────────────────────────────────────
def get_f1():
    url = "https://api.jolpi.ca/ergast/f1/current/next.json"
    response = requests.get(url)
    data = response.json()
    race = data['MRData']['RaceTable']['Races'][0]
    race_name = race['raceName']
    circuit = race['Circuit']['circuitName']
    country = race['Circuit']['Location']['country']
    date = race['date']
    return (f"🏎 *Formula 1 — Next Race*\n"
            f"{race_name}\n"
            f"📍 {circuit}, {country}\n"
            f"📅 {date}")

# ── NBA ───────────────────────────────────────────────────────
def get_nba():
    from datetime import datetime, timedelta
    
    
    # Get games from the last 7 days
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = f"https://api.balldontlie.io/v1/games?per_page=5&start_date={week_ago}&end_date={today}"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    games = data['data']
    
    if not games:
        return "🏀 *NBA* — No games in the last 7 days (off season)"
    
    msg = "🏀 *NBA — Recent Games*\n"
    for game in games[:3]:
        home = game['home_team']['full_name']
        visitor = game['visitor_team']['full_name']
        home_score = game['home_team_score']
        visitor_score = game['visitor_team_score']
        date = game['date'][:10]
        msg += f"{visitor} {visitor_score} @ {home} {home_score} ({date})\n"
    return msg.strip()
# ── TEST ALL FUNCTIONS ────────────────────────────────────────
try:
    print("Testing weather...")
    print(get_weather())
except Exception as e:
    print(f"Weather error: {e}")

try:
    print("\nTesting F1...")
    print(get_f1())
except Exception as e:
    print(f"F1 error: {e}")

try:
    print("\nTesting NBA...")
    print(get_nba())
except Exception as e:
    print(f"NBA error: {e}")
import asyncio

from datetime import datetime

async def send_daily_briefing():
    bot = Bot(token=TELEGRAM_TOKEN)
    message = "🌅 <b>Good Morning! Here's your daily briefing:</b>\n\n"
    
    try:
        message += get_weather() + "\n\n"
    except Exception as e:
        message += "🌤 Weather unavailable\n\n"
    
    try:
        message += get_f1() + "\n\n"
    except Exception as e:
        message += "🏎 F1 unavailable\n\n"
    
    try:
        message += get_nba() + "\n\n"
    except Exception as e:
        message += "🏀 NBA unavailable\n\n"

    async with bot:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='HTML')
    print("Briefing sent!")

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