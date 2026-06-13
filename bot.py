import requests
import asyncio
import os
from datetime import datetime, timedelta
from telegram import Bot

# ── CONFIG ───────────────────────────────────────────────────
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
    current_url = f"http://api.openweathermap.org/data/2.5/weather?q=Colombo,LK&appid={OPENWEATHER_API_KEY}&units=metric"
    current = requests.get(current_url).json()
    temp = current['main']['temp']
    feels_like = current['main']['feels_like']
    description = current['weather'][0]['description'].capitalize()
    humidity = current['main']['humidity']

    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q=Colombo,LK&appid={OPENWEATHER_API_KEY}&units=metric&cnt=5"
    forecast = requests.get(forecast_url).json()

    msg = (f"🌤 <b>Weather — Colombo</b>\n"
           f"{description}\n"
           f"🌡 {temp}°C (feels like {feels_like}°C)\n"
           f"💧 Humidity: {humidity}%\n\n"
           f"<b>Next 15 hours:</b>\n")

    for item in forecast['list']:
        t = item['dt_txt'][11:16]
        temp_f = item['main']['temp']
        desc = item['weather'][0]['description'].capitalize()
        msg += f"  {t} — {temp_f}°C, {desc}\n"

    return msg.strip()


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
        race_dt = datetime.strptime(race_date, "%Y-%m-%d")
        if datetime.now() - race_dt > timedelta(days=7):
            return None
        msg = f"🏁 <b>Last Race Result — {race_name}</b>\n\n"
        for result in results[:3]:
            pos = result['position']
            driver = f"{result['Driver']['givenName']} {result['Driver']['familyName']}"
            team = result['Constructor']['name']
            t = result['Time']['time'] if 'Time' in result else result['status']
            msg += f"{pos}. {driver} ({team}) — {t}\n"
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


# ── F1 STANDINGS ─────────────────────────────────────────────
def get_f1_standings():
    url = "https://api.jolpi.ca/ergast/f1/2026/driverStandings.json"
    response = requests.get(url)
    data = response.json()
    standings = data['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']
    msg = "🏆 <b>F1 Driver Standings — Top 5</b>\n"
    for driver in standings[:5]:
        pos = driver['position']
        name = f"{driver['Driver']['givenName']} {driver['Driver']['familyName']}"
        team = driver['Constructors'][0]['name']
        points = driver['points']
        msg += f"{pos}. {name} ({team}) — {points} pts\n"
    return msg.strip()


# ── F1 FACT OF THE DAY ───────────────────────────────────────
def get_f1_fact():
    facts = [
        "Michael Schumacher holds the record for most F1 wins at a single circuit — 8 wins at Magny-Cours.",
        "Ayrton Senna won 41 races from 65 pole positions — a conversion rate of 63%.",
        "The Monaco Grand Prix has been held since 1929, making it the oldest active F1 circuit.",
        "Lewis Hamilton holds the all-time record for most F1 pole positions with 104.",
        "The fastest F1 pit stop ever recorded was 1.80 seconds by Red Bull in 2023.",
        "Ferrari is the only team to have competed in every Formula 1 World Championship season.",
        "Max Verstappen became the youngest F1 World Champion in 2021 at age 24.",
        "The Brazilian Grand Prix has been held at three different circuits since 1972.",
        "Nigel Mansell holds the record for most wins in a single season without winning the title — 9 in 1992.",
        "The fastest ever F1 lap was set at Monza in 2020 — Bottas averaged 264.362 km/h.",
        "Jackie Stewart was the first driver to wear a full-face helmet in F1.",
        "The 1984 Monaco Grand Prix is considered one of the greatest drives ever — Senna in the rain.",
        "Alain Prost and Ayrton Senna collided at the same corner in consecutive championship-deciding races.",
        "Jenson Button won the 2009 championship with a car that was nearly withdrawn before the season.",
        "The Nurburgring Nordschleife was used for F1 until 1976 after Niki Lauda's near-fatal crash.",
        "Red Bull won 21 out of 22 races in the 2023 season.",
        "Jim Clark won 25 of his 72 Grand Prix starts — a win rate of nearly 35%.",
        "The first F1 World Championship race was held at Silverstone on May 13, 1950.",
        "Kimi Raikkonen holds the record for most F1 starts with 349.",
        "Nelson Piquet won the 1983 championship by just 2 points over Alain Prost.",
        "The Bahrain Grand Prix was the first F1 race held in the Middle East in 2004.",
        "Mika Hakkinen retired from F1 at his peak — leaving as a two-time world champion.",
        "Carlos Reutemann led the 1981 championship by 17 points with two races to go and still lost.",
        "The 2021 Abu Dhabi finale is considered the most controversial finish in F1 history.",
        "Andrea Kimi Antonelli is the youngest driver on the 2026 grid, born in 2006.",
        "Lando Norris took his first F1 win at the 2024 Miami Grand Prix after 110 starts.",
        "The Baku street circuit has the longest straight in F1 at 2.2 kilometres.",
        "Sebastian Vettel won 4 consecutive world championships from 2010 to 2013.",
        "Damon Hill won the 1996 championship in his final season with Williams.",
        "The 2005 United States Grand Prix had only 6 cars start due to a tyre controversy.",
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    fact = facts[day_of_year % len(facts)]
    return f"🏎 <b>F1 Fact of the Day</b>\n{fact}"


# ── NBA RECENT GAMES ─────────────────────────────────────────
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


# ── NBA PLAYOFFS ─────────────────────────────────────────────
def get_nba_playoffs():
    today = datetime.now().strftime("%Y-%m-%d")
    month_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    url = f"https://api.balldontlie.io/v1/games?per_page=10&start_date={month_ago}&end_date={today}&postseason=true"
    headers = {"Authorization": BALLDONTLIE_API_KEY}
    response = requests.get(url, headers=headers)
    data = response.json()
    games = data['data']
    if not games:
        return None
    series = {}
    for game in games:
        home = game['home_team']['full_name']
        visitor = game['visitor_team']['full_name']
        key = tuple(sorted([home, visitor]))
        if key not in series:
            series[key] = {'home': home, 'visitor': visitor,
                           'home_wins': 0, 'visitor_wins': 0}
        if game['home_team_score'] > game['visitor_team_score']:
            series[key]['home_wins'] += 1
        elif game['visitor_team_score'] > game['home_team_score']:
            series[key]['visitor_wins'] += 1
    msg = "🏀 <b>NBA Playoffs — Series Tracker</b>\n"
    for key, s in series.items():
        msg += f"{s['visitor']} vs {s['home']}: {s['visitor_wins']}-{s['home_wins']}\n"
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


# ── EXCHANGE RATE ─────────────────────────────────────────────
def get_exchange_rate():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()
    lkr = data['rates']['LKR']
    eur = data['rates']['EUR']
    gbp = data['rates']['GBP']
    return (f"💱 <b>Exchange Rates</b>\n"
            f"1 USD = {lkr:.2f} LKR\n"
            f"1 USD = {eur:.4f} EUR\n"
            f"1 USD = {gbp:.4f} GBP")


# ── WORD OF THE DAY ──────────────────────────────────────────
def get_word_of_day():
    words = [
        "serendipity", "ephemeral", "perspicacious", "mellifluous", "sycophant",
        "ebullient", "laconic", "ineffable", "luminous", "pernicious",
        "obfuscate", "tenacious", "solipsism", "vicarious", "paradigm",
        "eloquent", "pragmatic", "stoic", "sardonic", "equanimity",
        "hubris", "catharsis", "zeitgeist", "schadenfreude", "wanderlust",
        "petrichor", "sonder", "hiraeth", "liminal", "palimpsest"
    ]
    day_of_year = datetime.now().timetuple().tm_yday
    word = words[day_of_year % len(words)]
    url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
    response = requests.get(url, timeout=10)
    data = response.json()
    meaning = data[0]['meanings'][0]
    part_of_speech = meaning['partOfSpeech']
    definition = meaning['definitions'][0]['definition']
    return (f"📖 <b>Word of the Day</b>\n"
            f"<b>{word}</b> <i>({part_of_speech})</i>\n"
            f"{definition}")


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
        message += get_f1_standings() + "\n\n"
    except Exception:
        pass

    try:
        message += get_f1_fact() + "\n\n"
    except Exception:
        pass

    try:
        message += get_nba() + "\n\n"
    except Exception:
        message += "🏀 NBA unavailable\n\n"

    try:
        playoffs = get_nba_playoffs()
        if playoffs:
            message += playoffs + "\n\n"
    except Exception:
        pass

    try:
        message += get_tech_news() + "\n\n"
    except Exception:
        message += "📱 Tech news unavailable\n\n"

    try:
        message += get_exchange_rate() + "\n\n"
    except Exception:
        message += "💱 Exchange rates unavailable\n\n"

    try:
        message += get_word_of_day() + "\n\n"
    except Exception as e:
        print(f"Word of day error: {e}")

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