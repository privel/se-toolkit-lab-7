"""LMS API client.

Provides methods to interact with the LMS backend API:
- get_health() — check if backend is available
- get_labs() — fetch list of labs and tasks
- get_scores(lab_id) — fetch student scores for a lab
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

    async def get_health(self) -> dict:
        """Check if the backend is healthy.
        
        Returns:
            Health status dictionary.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/health", headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def get_labs(self) -> list[dict]:
        """Fetch list of labs and tasks.
        
        Returns:
            List of lab and task items.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/items/", headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def get_scores(self, lab_id: Optional[str] = None) -> list[dict]:
        """Fetch student scores.
        
        Args:
            lab_id: Optional lab identifier to filter scores.
            
        Returns:
            List of score records.
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/analytics/scores"
            if lab_id:
                url += f"?lab_id={lab_id}"
            resp = await client.get(url, headers=self._headers)
            resp.raise_for_status()
            return resp.json()
