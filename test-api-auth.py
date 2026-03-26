import httpx
import asyncio
import os


async def test():
    url = os.environ.get("AUTOCHECKER_API_URL", "https://auche.namaz.live")
    login = os.environ.get("AUTOCHECKER_API_LOGIN", "")
    password = os.environ.get("AUTOCHECKER_API_PASSWORD", "")

    print(f"URL: {url}")
    print(f"Login: {login}")

    async with httpx.AsyncClient(
        timeout=120,
        follow_redirects=True,
        http2=False,
    ) as client:
        try:
            # Test /api/items
            resp = await client.get(
                f"{url}/api/items",
                auth=(login, password),
            )
            print(f"Items Status: {resp.status_code}")
            print(f"Items Response length: {len(resp.text)}")

            # Test /api/logs WITHOUT since parameter (like first sync)
            resp = await client.get(
                f"{url}/api/logs",
                params={"limit": 100},
                auth=(login, password),
            )
            print(f"Logs (no since) Status: {resp.status_code}")
            print(f"Logs (no since) Response length: {len(resp.text)}")

            # Test /api/logs WITH since=None explicitly - this might cause issues
            resp = await client.get(
                f"{url}/api/logs",
                params={"limit": 100, "since": None},
                auth=(login, password),
            )
            print(f"Logs (since=None) Status: {resp.status_code}")
            print(f"Logs (since=None) Response length: {len(resp.text)}")

        except Exception as e:
            print(f"Error: {type(e).__name__}: {e}")
            import traceback

            traceback.print_exc()


asyncio.run(test())
