"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They don't depend on Telegram - same logic works from --test mode,
unit tests, or Telegram.
"""


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return "Available commands: /start, /help, /health, /labs, /scores"


def handle_health() -> str:
    """Handle /health command."""
    return "Bot is healthy (placeholder)"


def handle_labs() -> str:
    """Handle /labs command."""
    return "Labs list (placeholder)"


def handle_scores(args: str = "") -> str:
    """Handle /scores command.
    
    Args:
        args: Lab identifier (e.g., "lab-04")
    
    Returns:
        Scores information string.
    """
    return f"Scores for {args if args else 'all labs'} (placeholder)"
