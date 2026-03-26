import httpx
import asyncio

async def test():
    try:
        resp = await httpx.get('https://auche.namaz.live/', timeout=10.0)
        print(f"Status: {resp.status_code}")
    except Exception as e:
        print(f"Error: {e}")

asyncio.run(test())
