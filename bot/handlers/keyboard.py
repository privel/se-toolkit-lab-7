"""Inline keyboard buttons for Telegram bot.

Provides keyboard layouts for common actions so users can discover
functionality without typing commands.
"""

from typing import Any


def get_start_keyboard() -> list[list[dict[str, Any]]]:
    """Get inline keyboard for /start command.

    Returns:
        Inline keyboard markup with common action buttons.
    """
    return [
        [
            {
                "text": "📋 Available Labs",
                "callback_data": "cmd_labs",
            },
            {
                "text": "💚 System Health",
                "callback_data": "cmd_health",
            },
        ],
        [
            {
                "text": "📊 Scores by Lab",
                "callback_data": "cmd_scores",
            },
            {
                "text": "🏆 Top Students",
                "callback_data": "cmd_top",
            },
        ],
        [
            {
                "text": "❓ Help",
                "callback_data": "cmd_help",
            },
        ],
    ]


def get_help_keyboard() -> list[list[dict[str, Any]]]:
    """Get inline keyboard for /help command.

    Returns:
        Inline keyboard markup with help buttons.
    """
    return [
        [
            {
                "text": "📋 List Labs",
                "callback_data": "cmd_labs",
            },
            {
                "text": "💚 Health Check",
                "callback_data": "cmd_health",
            },
        ],
        [
            {
                "text": "📊 View Scores",
                "callback_data": "cmd_scores",
            },
            {
                "text": "🏆 Top Learners",
                "callback_data": "cmd_top",
            },
        ],
        [
            {
                "text": "📈 Pass Rates",
                "callback_data": "cmd_pass",
            },
            {
                "text": "👥 Groups",
                "callback_data": "cmd_groups",
            },
        ],
    ]


def get_labs_keyboard(labs: list[dict]) -> list[list[dict[str, Any]]]:
    """Get inline keyboard with lab buttons.

    Args:
        labs: List of lab items from backend

    Returns:
        Inline keyboard markup with lab buttons.
    """
    keyboard = []
    row = []

    for lab in labs[:10]:  # Limit to first 10 labs
        slug = lab.get("slug", "")
        if slug:
            row.append({
                "text": slug,
                "callback_data": f"lab_{slug}",
            })
            if len(row) >= 2:
                keyboard.append(row)
                row = []

    if row:
        keyboard.append(row)

    return keyboard


def format_keyboard_message(text: str, keyboard: list[list[dict[str, Any]]]) -> dict[str, Any]:
    """Format a message with inline keyboard for Telegram API.

    Args:
        text: Message text
        keyboard: Inline keyboard markup

    Returns:
        Dict ready to send to Telegram API
    """
    return {
        "text": text,
        "reply_markup": {
            "inline_keyboard": keyboard,
        },
        "parse_mode": "HTML",
    }
