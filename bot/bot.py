#!/usr/bin/env python3
"""Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"     # Test mode (no Telegram connection)
    uv run bot.py --test "question"   # Test mode with plain text (LLM routing)
    uv run bot.py                     # Production mode (connects to Telegram)
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    route_intent,
)


async def run_test_mode(input_text: str) -> None:
    """Run bot in test mode - call handler directly without Telegram.

    Args:
        input_text: Command or plain text message to process
    """
    input_text = input_text.strip()

    # Check if it's a slash command
    if input_text.startswith("/"):
        parts = input_text.split(maxsplit=1)
        cmd = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        # Route to appropriate handler (async handlers)
        if cmd == "/start":
            response = handle_start()
        elif cmd == "/help":
            response = handle_help()
        elif cmd == "/health":
            response = await handle_health()
        elif cmd == "/labs":
            response = await handle_labs()
        elif cmd == "/scores":
            response = await handle_scores(args)
        else:
            response = f"Unknown command: {cmd}"
    else:
        # Plain text - use intent router with LLM
        response = await route_intent(input_text)

    # Print response to stdout
    print(response)


async def run_production_mode() -> None:
    """Run bot in production mode - connect to Telegram."""
    # TODO: Implement Telegram bot client
    print("Production mode not yet implemented")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="MESSAGE",
        help="Run in test mode with the given command or message (e.g., '/start' or 'what labs are available')",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler or intent router
        asyncio.run(run_test_mode(args.test))
    else:
        # Production mode: connect to Telegram
        asyncio.run(run_production_mode())


if __name__ == "__main__":
    main()
