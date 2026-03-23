# Project Documentation

## 1. Overview

**Telegram AI Personality Bot** is a Python Telegram bot project with:

- AI-based dialogue
- personality profile support
- free request limits
- subscription logic
- SQLite-based storage
- admin commands

The project was built as a pet-project / portfolio MVP and is not a final production-ready system.

---

## 2. Main idea

The bot allows a user to:

1. start interacting with the bot via `/start`
2. subscribe to a required Telegram channel
3. choose a personality type
4. start dialogue mode using `/begin`
5. communicate with the AI assistant
6. stop dialogue with `/end`
7. view profile information using `/profile`

The bot also supports free requests and subscription-based access control.

---

## 3. Main technologies

- **Python** — core language
- **pyTelegramBotAPI** — Telegram bot interaction
- **OpenAI API** — AI dialogue generation
- **SQLite** — local database
- **python-dotenv** — environment variables from `.env`

---

## 4. Configuration

The project uses environment variables instead of hardcoded secrets.

Required `.env` variables:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
CHANNEL_USERNAME=@your_channel
DB_PATH=tg_base_psiho.db
```

Variable description
- **TELEGRAM_BOT_TOKEN** — Telegram bot token
- **OPENAI_API_KEY** — OpenAI API key
- **CHANNEL_USERNAME** — Telegram channel username used for subscription check
- **DB_PATH** — path to SQLite database file

⸻

## 5. Database

The project uses SQLite with a users table.

Current table structure
- **id** — internal primary key
- **user_id** — Telegram user ID
- **call_item** — remaining free requests
- **data** — subscription expiration date
- **colih** — dialogue request counter
- **tip** — personality type
- **dialog** — stored dialogue history

Notes

This is a simple MVP table design.
In a more mature version, subscriptions, profiles, and dialogue history would likely be separated into multiple tables.

⸻

## 6. Main commands

User commands
- /start — register the user if needed and show start information
- /info — same behavior as /start
- /begin — start dialogue mode
- /end — stop dialogue mode and clear dialogue history
- /profile — show profile and available data

Admin commands
- /1010 user_id months — set subscription based on current date
- /1011 user_id months — extend existing subscription
- /1012 user_id amount — add free requests
- /1020 — show user statistics
- /1030 — send database file

⸻

## 7. Main logic

**Registration**

When a user sends /start, the bot:
- checks whether the user exists in the database
- creates a new record if needed
- initializes a default expired subscription state
- shows the start message

**Subscription check**

Before most interactions, the bot checks whether the user is subscribed to the configured Telegram channel.

**Dialogue mode**

Dialogue mode starts from /begin.

The bot:
- checks subscription or free requests
- validates that the user selected a personality type
- clears previous dialogue history if needed
- starts a multi-step interaction through Telegram handlers

**AI request flow**

For each user message:
1. bot loads stored dialogue history
2.	bot loads personality type
3.	bot builds prompt text
4.	bot sends request to OpenAI
5.	bot sends generated answer back to the user
6.	bot updates dialogue history and counters in SQLite

⸻

## 8. Project structure

Current structure is simple and monolithic.

Main files
- main.py — main application logic
- start.txt — start message text
- requirements.txt — Python dependencies
- .env — local secrets and settings (not committed)
- tg_base_psiho.db — local SQLite database (not committed)

**Current architectural limitation**

Most logic is currently stored in main.py.
This is acceptable for an MVP, but future improvements should separate:
- bot handlers
- database logic
- AI service logic
- subscription logic
- utility functions

⸻

## 9. Known limitations

Current known limitations include:
- monolithic file structure
- repeated SQLite connection logic
- minimal validation in some flows
- basic exception handling
- callback logic can be improved
- user/chat ID usage should be made more consistent
- project is designed for local launch, not production deployment

⸻

## 10. Security notes

The following must never be committed to GitHub:
- .env
- real API tokens
- tg_base_psiho.db
- local virtual environment files

Use .gitignore to prevent accidental upload of local secrets and data.

⸻

## 11. Future improvements

Planned or recommended improvements:
1.	split main.py into modules
2.	add structured logging
3.	improve exception handling
4.	refactor repeated database code
5.	improve variable naming
6.	make user ID / chat ID handling more consistent
7.	update OpenAI integration to the current SDK style if needed
8.	add tests
9.	prepare Docker / deployment version
10.	add clearer admin permissions and validation

⸻

## 12. Intended purpose

This repository is published primarily as a portfolio project.
Its purpose is to demonstrate:
- Python basics in a real project
- Telegram bot development
- environment variable handling
- database interaction
- external API integration
- MVP product logic

