"""Services for the Telegram bot.

Services provide external integrations (API clients, LLM clients, etc.).
"""

from services.lms_client import LMSClient
from services.llm_client import LLMClient
from services.tools import get_tools_definitions, get_system_prompt

__all__ = ["LMSClient", "LLMClient", "get_tools_definitions", "get_system_prompt"]
