# Daily Briefing Telegram Bot

A Python bot that sends a personalised daily briefing to Telegram every morning at 9am.

## What it includes
- 🌤 Weather forecast for Colombo (temperature, conditions, humidity)
- 🏎 Formula 1 next race details (circuit, country, date)
- 🏀 NBA recent game scores (last 7 days)

## How it works
The bot runs continuously in the background and sends a formatted 
Telegram message at 9:00am daily. Each section is wrapped in error 
handling so a failed API call won't break the whole message.

## APIs used
- OpenWeatherMap (weather)
- Jolpi Ergast F1 API (Formula 1)
- BallDontLie API (NBA)
- Telegram Bot API

## Setup
1. Create a Telegram bot via @BotFather and get your token
2. Get your Telegram Chat ID via the getUpdates endpoint
3. Create a free OpenWeatherMap account for the API key
4. Create a free BallDontLie account for the NBA API key
5. Add all keys to config.py (not included in repo)
6. Run: python bot.py

## Tools
Python, python-telegram-bot, requests, asyncio
