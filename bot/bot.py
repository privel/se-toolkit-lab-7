#!/usr/bin/env python3
"""Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"     # Test mode (no Telegram connection)
    uv run bot.py                     # Production mode (connects to Telegram)
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


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


def handle_scores(args: str) -> str:
    """Handle /scores command."""
    return f"Scores for {args if args else 'all labs'} (placeholder)"


async def run_test_mode(command: str) -> None:
    """Run bot in test mode - call handler directly without Telegram."""
    # Parse command and arguments
    parts = command.strip().split(maxsplit=1)
    cmd = parts[0]
    args = parts[1] if len(parts) > 1 else ""

    # Route to appropriate handler
    if cmd == "/start":
        response = handle_start()
    elif cmd == "/help":
        response = handle_help()
    elif cmd == "/health":
        response = handle_health()
    elif cmd == "/labs":
        response = handle_labs()
    elif cmd == "/scores":
        response = handle_scores(args)
    else:
        response = f"Unknown command: {cmd}"

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
        metavar="COMMAND",
        help="Run in test mode with the given command (e.g., '/start')",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handler directly
        asyncio.run(run_test_mode(args.test))
    else:
        # Production mode: connect to Telegram
        asyncio.run(run_production_mode())


if __name__ == "__main__":
    main()
