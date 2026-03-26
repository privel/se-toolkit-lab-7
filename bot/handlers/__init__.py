"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They don't depend on Telegram - same logic works from --test mode,
unit tests, or Telegram.
"""

import asyncio
from typing import Optional

from config import load_config
from services import LMSClient


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return "Available commands: /start, /help, /health, /labs, /scores"


async def handle_health_async() -> str:
    """Handle /health command - check backend availability."""
    config = load_config()

    if not config["lms_api_base_url"]:
        return "Error: LMS_API_BASE_URL not configured"

    try:
        client = LMSClient(
            base_url=config["lms_api_base_url"],
            api_key=config["lms_api_key"],
        )
        health = await client.get_health()
        status = health.get("status", "unknown")
        return f"Backend status: {status}"
    except httpx.ConnectError as e:
        return f"Cannot connect to backend: {e}"
    except httpx.HTTPStatusError as e:
        return f"Backend error: {e.response.status_code}"
    except Exception as e:
        return f"Error: {e}"


def handle_health() -> str:
    """Handle /health command (sync wrapper)."""
    return asyncio.run(handle_health_async())


async def handle_labs_async() -> str:
    """Handle /labs command - fetch labs from backend."""
    config = load_config()

    if not config["lms_api_base_url"]:
        return "Error: LMS_API_BASE_URL not configured"

    try:
        client = LMSClient(
            base_url=config["lms_api_base_url"],
            api_key=config["lms_api_key"],
        )
        items = await client.get_labs()

        # Filter only labs (not tasks)
        labs = [item for item in items if item.get("type") == "lab"]

        if not labs:
            return "No labs available"

        result = ["Available labs:"]
        for lab in labs:
            title = lab.get("title", "Unknown")
            result.append(f"  • {title}")

        return "\n".join(result)
    except httpx.ConnectError as e:
        return f"Cannot connect to backend: {e}"
    except httpx.HTTPStatusError as e:
        return f"Backend error: {e.response.status_code}"
    except Exception as e:
        return f"Error: {e}"


def handle_labs() -> str:
    """Handle /labs command (sync wrapper)."""
    return asyncio.run(handle_labs_async())


async def handle_scores_async(lab_id: Optional[str] = None) -> str:
    """Handle /scores command - fetch scores from backend.

    Args:
        lab_id: Optional lab identifier.

    Returns:
        Scores information string.
    """
    config = load_config()

    if not config["lms_api_base_url"]:
        return "Error: LMS_API_BASE_URL not configured"

    try:
        client = LMSClient(
            base_url=config["lms_api_base_url"],
            api_key=config["lms_api_key"],
        )
        scores = await client.get_scores(lab_id)

        if not scores:
            return f"No scores found{'for ' + lab_id if lab_id else ''}"

        result = [f"Scores{' for ' + lab_id if lab_id else ''}:"]
        for score in scores[:10]:  # Limit to 10 results
            title = score.get("item_title", "Unknown")
            value = score.get("score", "N/A")
            result.append(f"  • {title}: {value}")

        if len(scores) > 10:
            result.append(f"  ... and {len(scores) - 10} more")

        return "\n".join(result)
    except httpx.ConnectError as e:
        return f"Cannot connect to backend: {e}"
    except httpx.HTTPStatusError as e:
        return f"Backend error: {e.response.status_code}"
    except Exception as e:
        return f"Error: {e}"


def handle_scores(args: str = "") -> str:
    """Handle /scores command (sync wrapper)."""
    return asyncio.run(handle_scores_async(args if args else None))


# Import httpx at module level for exception handling
import httpx
