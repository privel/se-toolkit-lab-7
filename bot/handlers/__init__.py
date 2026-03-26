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
    return """Available commands:
  /start — Welcome message
  /help — Show this help message
  /health — Check backend status
  /labs — List available labs
  /scores <lab> — Show score distribution for a lab (e.g., /scores lab-04)"""


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
        items_count = health.get("items_count", 0)
        return f"Backend is healthy. {items_count} items available."
    except httpx.ConnectError as e:
        return f"Backend error: connection refused. Check that the services are running. ({e})"
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code}. The backend service may be down."
    except httpx.HTTPError as e:
        return f"Backend error: {e}"
    except Exception as e:
        return f"Backend error: {e}"


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
    """Handle /scores command - fetch pass rates from backend.

    Args:
        lab_id: Lab identifier (required).

    Returns:
        Pass rates information string.
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
        pass_rates = await client.get_pass_rates(lab_id)

        if not pass_rates:
            return f"No pass rates found for {lab_id}. The lab may not exist."

        result = [f"Pass rates for {lab_id}:"]
        for task in pass_rates:
            task_name = task.get("task", "Unknown")
            avg_score = task.get("avg_score", 0)
            attempts = task.get("attempts", 0)
            result.append(f"  • {task_name}: {avg_score}% ({attempts} attempts)")

        return "\n".join(result)
    except httpx.ConnectError as e:
        return f"Backend error: connection refused. Check that the services are running. ({e})"
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 422:
            return f"Invalid lab ID: {lab_id}. Use format like 'lab-01'."
        return f"Backend error: HTTP {e.response.status_code}. The backend service may be down."
    except httpx.HTTPError as e:
        return f"Backend error: {e}"
    except Exception as e:
        return f"Backend error: {e}"
