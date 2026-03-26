"""LMS API client.

Provides methods to interact with the LMS backend API:
- get_health() — check if backend is available
- get_labs() — fetch list of labs and tasks
- get_pass_rates(lab_id) — fetch per-task pass rates for a lab
"""

import httpx
from typing import Optional


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.

        Args:
            base_url: Base URL of the LMS API (e.g., http://localhost:42002)
            api_key: API key for authentication (Bearer token)
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._headers = {"Authorization": f"Bearer {api_key}"}

    async def get_labs(self) -> list[dict]:
        """Fetch list of labs and tasks.

        Returns:
            List of lab and task items.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/items/", headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def get_pass_rates(self, lab_id: Optional[str] = None) -> list[dict]:
        """Fetch per-task pass rates for a lab.

        Args:
            lab_id: Lab identifier to filter pass rates.

        Returns:
            List of pass rate records with task_name, pass_rate, attempts.
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/analytics/pass-rates"
            if lab_id:
                url += f"?lab={lab_id}"
            resp = await client.get(url, headers=self._headers)
            resp.raise_for_status()
            return resp.json()
