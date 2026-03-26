"""Services for the Telegram bot.

Services provide external integrations (API clients, LLM clients, etc.).
"""

from services.lms_client import LMSClient

__all__ = ["LMSClient"]
