# LMS Telegram Bot

Telegram bot for the Learning Management System.

## Usage

### Test mode

```bash
uv run bot.py --test "/start"
uv run bot.py --test "/help"
uv run bot.py --test "/health"
```

### Production mode

```bash
uv run bot.py
```

## Configuration

Create `.env.bot.secret` with:

```text
BOT_TOKEN=your-telegram-bot-token
LMS_API_BASE_URL=http://localhost:42002
LMS_API_KEY=your-api-key
LLM_API_KEY=your-llm-api-key
LLM_API_BASE_URL=http://localhost:42005/v1
LLM_API_MODEL=coder-model
```
