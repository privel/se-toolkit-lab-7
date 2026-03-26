import httpx
import asyncio
import os
from datetime import datetime


async def test():
    url = os.environ.get("AUTOCHECKER_API_URL", "https://auche.namaz.live")
    login = os.environ.get("AUTOCHECKER_API_LOGIN", "")
    password = os.environ.get("AUTOCHECKER_API_PASSWORD", "")

    print(f"URL: {url}")
    print(f"Login: {login}")

    all_logs = []
    max_pages = 20
    page_count = 0
    cursor = None  # since=None for first request

    while page_count < max_pages:
        # Create a new client for each request (like the fixed etl.py)
        async with httpx.AsyncClient(
            timeout=120,
            follow_redirects=True,
            http2=False,
        ) as client:
            params = {"limit": 100}
            if cursor is not None:
                params["since"] = cursor.isoformat()

            print(f"\nPage {page_count}: Fetching with params {params}")

            try:
                resp = await client.get(
                    f"{url}/api/logs",
                    params=params,
                    auth=(login, password),
                )
                resp.raise_for_status()
                data = resp.json()

                logs = data.get("logs", [])
                has_more = data.get("has_more", False)

                print(f"  Status: {resp.status_code}")
                print(f"  Logs received: {len(logs)}")
                print(f"  Has more: {has_more}")

                all_logs.extend(logs)

                if not has_more or not logs:
                    print("  Breaking - no more data")
                    break

                # Update cursor to last log's submitted_at
                cursor = datetime.fromisoformat(logs[-1]["submitted_at"])
                print(f"  Next cursor: {cursor}")
                page_count += 1

            except Exception as e:
                print(f"  Error: {type(e).__name__}: {e}")
                import traceback

                traceback.print_exc()
                break

    print(f"\nTotal logs fetched: {len(all_logs)}")


asyncio.run(test())
