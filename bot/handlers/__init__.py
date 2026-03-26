"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They don't depend on Telegram - same logic works from --test mode,
unit tests, or Telegram.
"""

from typing import Optional

import httpx

from config import load_config
from services import LMSClient


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! Use /help to see available commands."


def handle_help() -> str:
    """Handle /help command."""
    return "Available commands: /start, /help, /health, /labs, /scores"


async def handle_health() -> str:
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


async def handle_labs() -> str:
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


async def handle_scores(lab_id: Optional[str] = None) -> str:
    """Handle /scores command - fetch scores from backend.

    Args:
        lab_id: Lab identifier (required).

    Returns:
        Scores information string.
    """
    config = load_config()

    if not config["lms_api_base_url"]:
        return "Error: LMS_API_BASE_URL not configured"

    if not lab_id:
        return "Usage: /scores <lab-id> (e.g., /scores lab-04)"

    try:
        client = LMSClient(
            base_url=config["lms_api_base_url"],
            api_key=config["lms_api_key"],
        )
        scores = await client.get_scores(lab_id)

        if not scores:
            return f"No scores found for {lab_id}"

        # Scores are bucket distributions
        result = [f"Score distribution for {lab_id}:"]
        for bucket in scores:
            bucket_range = bucket.get("bucket", "Unknown")
            count = bucket.get("count", 0)
            result.append(f"  • {bucket_range}: {count} students")

        return "\n".join(result)
    except httpx.ConnectError as e:
        return f"Cannot connect to backend: {e}"
    except httpx.HTTPStatusError as e:
        return f"Backend error: {e.response.status_code}"
    except Exception as e:
        return f"Error: {e}"
