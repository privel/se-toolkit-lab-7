"""Configuration loader for the bot.

Loads environment variables from .env.bot.secret (or .env.bot.example).
"""

from pathlib import Path
from dotenv import load_dotenv
import os


def load_config() -> dict[str, str]:
    """Load configuration from environment file.
    
    Returns:
        Dictionary with configuration values.
    """
    # Find the .env file (prefer .secret, fall back to .example)
    bot_dir = Path(__file__).parent
    secret_file = bot_dir.parent / ".env.bot.secret"
    example_file = bot_dir.parent / ".env.bot.example"
    
    env_file = secret_file if secret_file.exists() else example_file
    
    # Load environment variables
    load_dotenv(env_file)
    
    return {
        "bot_token": os.getenv("BOT_TOKEN", ""),
        "lms_api_base_url": os.getenv("LMS_API_BASE_URL", ""),
        "lms_api_key": os.getenv("LMS_API_KEY", ""),
        "llm_api_key": os.getenv("LLM_API_KEY", ""),
        "llm_api_base_url": os.getenv("LLM_API_BASE_URL", ""),
        "llm_api_model": os.getenv("LLM_API_MODEL", "coder-model"),
    }
