"""LMS API client.

Provides methods to interact with the LMS backend API.
All 9 endpoints are implemented for LLM tool use.
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

    async def get_items(self) -> list[dict]:
        """Fetch list of all labs and tasks.

        Returns:
            List of lab and task items.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/items/", headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def get_labs(self) -> list[dict]:
        """Fetch list of labs and tasks (alias for get_items).

        Returns:
            List of lab and task items.
        """
        return await self.get_items()

    async def get_learners(self) -> list[dict]:
        """Fetch list of enrolled learners and their groups.

        Returns:
            List of learner records.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/learners/", headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def get_scores(self, lab: str) -> list[dict]:
        """Get score distribution (4 buckets) for a specific lab.

        Args:
            lab: Lab identifier, e.g. 'lab-01'

        Returns:
            List of score bucket records.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/analytics/scores?lab={lab}", headers=self._headers
            )
            resp.raise_for_status()
            return resp.json()

    async def get_pass_rates(self, lab: Optional[str] = None) -> list[dict]:
        """Get per-task average scores and attempt counts for a lab.

        Args:
            lab: Lab identifier, e.g. 'lab-01'

        Returns:
            List of pass rate records with task, avg_score, attempts.
        """
        async with httpx.AsyncClient() as client:
            url = f"{self.base_url}/analytics/pass-rates"
            if lab:
                url += f"?lab={lab}"
            resp = await client.get(url, headers=self._headers)
            resp.raise_for_status()
            return resp.json()

    async def get_timeline(self, lab: str) -> list[dict]:
        """Get submission timeline data showing submissions per day.

        Args:
            lab: Lab identifier, e.g. 'lab-01'

        Returns:
            List of timeline records with date and count.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/analytics/timeline?lab={lab}", headers=self._headers
            )
            resp.raise_for_status()
            return resp.json()

    async def get_groups(self, lab: str) -> list[dict]:
        """Get per-group scores and student counts for a lab.

        Args:
            lab: Lab identifier, e.g. 'lab-01'

        Returns:
            List of group records with group name, avg score, student count.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/analytics/groups?lab={lab}", headers=self._headers
            )
            resp.raise_for_status()
            return resp.json()

    async def get_top_learners(self, lab: str, limit: int = 10) -> list[dict]:
        """Get top N learners by score for a lab.

        Args:
            lab: Lab identifier, e.g. 'lab-01'
            limit: Number of top learners to return

        Returns:
            List of top learner records with name and score.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/analytics/top-learners?lab={lab}&limit={limit}",
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def get_completion_rate(self, lab: str) -> dict:
        """Get completion rate percentage for a lab.

        Args:
            lab: Lab identifier, e.g. 'lab-01'

        Returns:
            Dict with completion rate percentage.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"{self.base_url}/analytics/completion-rate?lab={lab}",
                headers=self._headers,
            )
            resp.raise_for_status()
            return resp.json()

    async def trigger_sync(self) -> dict:
        """Trigger a data sync from the autochecker.

        Returns:
            Sync result dict.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{self.base_url}/pipeline/sync", headers=self._headers
            )
            resp.raise_for_status()
            return resp.json()
