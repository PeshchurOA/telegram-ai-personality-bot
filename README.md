# Telegram AI Personality Bot

Telegram bot with AI dialogue, personality profile, subscription logic, and SQLite storage.

## About the project

This project is a Python pet-project / MVP of a Telegram bot that allows users to:

- interact with an AI assistant in dialogue mode;
- store and update a personality type;
- use free requests or subscription-based access;
- view their profile and available limits;
- work with a simple admin panel for managing subscriptions and requests.

The project was created as a portfolio project and is currently **in progress**.  
It is **not a final production-ready version** and may contain architectural limitations, edge cases, and unfinished improvements.

For more details, see [DOCUMENTATION.md](DOCUMENTATION.md).

## Features

- Telegram bot interface
- AI dialogue mode
- personality type selection
- user profile
- free request limits
- subscription-based access
- SQLite database for user data and dialogue history
- admin commands for managing users and subscriptions

## Tech stack

- Python
- pyTelegramBotAPI
- OpenAI API
- SQLite
- python-dotenv

## Project status

Current status: **MVP / in progress**

Known limitations:

- monolithic structure (`main.py`)
- repeated database access patterns
- basic error handling
- not optimized for production deployment
- uses SQLite as a simple local database

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/telegram-ai-personality-bot.git
cd telegram-ai-personality-bot
```

### 2. Create and activate virtual environment

macOS / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
```

Windows:

```
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```pip install -r requirements.txt```

### 4. Create .env

Create a .env file in the project root:
```
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
CHANNEL_USERNAME=@your_channel
DB_PATH=tg_base_psiho.db
```
Run

```
python main.py
```
### Repository notes

The following files are not included in the repository:
- .env
- base_psiho.db
- .venv
- config.py

This is done for security and to avoid publishing secrets or local data.

### Planned improvements
- split logic into separate modules
- improve naming and readability
- improve error handling
- refactor database access
- improve callback and user state handling
- add deployment instructions
- improve project structure

### License

This repository currently has no license.
The code is published as a portfolio project.

