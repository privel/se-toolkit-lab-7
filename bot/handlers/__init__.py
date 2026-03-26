"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They don't depend on Telegram - same logic works from --test mode,
unit tests, or Telegram.
"""

from typing import Optional

import httpx

from config import load_config
from services import LMSClient
from handlers.intent_router import route as route_intent


def handle_start() -> str:
    """Handle /start command."""
    return "Welcome to the LMS Bot! I can help you check system health, browse labs, and view scores. Use /help to see all available commands."


def handle_help() -> str:
    """Handle /help command."""
    return """Available commands:
/start — Welcome message and bot introduction
/help — Show this help message with all commands
/health — Check if the backend is running and healthy
/labs — List all available labs
/scores <lab> — Show pass rates for a specific lab (e.g., /scores lab-04)"""


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
        items = await client.get_labs()
        item_count = len(items) if items else 0
        return f"Backend is healthy. {item_count} items available."
    except httpx.ConnectError as e:
        return (
            f"Backend error: connection refused. Check that the services are running."
        )
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {str(e)}. Check that the services are running."


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
            # Extract lab number from slug if available
            slug = lab.get("slug", "")
            if slug:
                result.append(f"- {slug} — {title}")
            else:
                result.append(f"- {title}")

        return "\n".join(result)
    except httpx.ConnectError as e:
        return (
            f"Backend error: connection refused. Check that the services are running."
        )
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {str(e)}. Check that the services are running."


async def handle_scores(lab_id: Optional[str] = None) -> str:
    """Handle /scores command - fetch scores from backend.

    Args:
        lab_id: Optional lab identifier.

    Returns:
        Scores information string.
    """
    config = load_config()

    if not config["lms_api_base_url"]:
        return "Error: LMS_API_BASE_URL not configured"

    # Handle missing lab_id argument
    if not lab_id or not lab_id.strip():
        return "Usage: /scores <lab-id>. Example: /scores lab-04"

    try:
        client = LMSClient(
            base_url=config["lms_api_base_url"],
            api_key=config["lms_api_key"],
        )
        # Use pass-rates endpoint for per-task data
        pass_rates = await client.get_pass_rates(lab_id)

        if not pass_rates:
            return f"No pass rates found for {lab_id}. Check that the lab exists."

        # Extract lab name for display
        lab_name = lab_id.replace("lab-", "Lab ").replace("-", " ").title()

        result = [f"Pass rates for {lab_name}:"]
        for rate in pass_rates:
            # API returns: task, avg_score, attempts
            task_name = rate.get(
                "task", rate.get("task_name", rate.get("item_title", "Unknown"))
            )
            pass_rate = rate.get(
                "avg_score", rate.get("pass_rate", rate.get("score", 0))
            )
            attempts = rate.get("attempts", 0)
            # Format as percentage
            percentage = (
                f"{pass_rate:.1f}%"
                if isinstance(pass_rate, (int, float))
                else str(pass_rate)
            )
            result.append(f"- {task_name}: {percentage} ({attempts} attempts)")

        return "\n".join(result)
    except httpx.ConnectError as e:
        return (
            f"Backend error: connection refused. Check that the services are running."
        )
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code}. The backend service may be down."
    except Exception as e:
        return f"Backend error: {str(e)}. Check that the services are running."
