"""LLM client for intent recognition and tool use.

This client wraps the LLM API (OpenAI-compatible) and handles:
- Sending user messages with tool definitions
- Parsing tool calls from LLM responses
- Feeding tool results back for multi-turn reasoning
"""

import httpx
import json
from typing import Any


class LLMClient:
    """Client for LLM API with tool calling support."""

    def __init__(self, api_key: str, base_url: str, model: str):
        """Initialize the LLM client.

        Args:
            api_key: API key for authentication
            base_url: Base URL of the LLM API (e.g., http://localhost:42005)
            model: Model name to use (e.g., "coder-model")
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        system_prompt: str | None = None,
    ) -> dict[str, Any]:
        """Send a chat message to the LLM.

        Args:
            messages: List of conversation messages with role and content
            tools: Optional list of tool definitions for function calling
            system_prompt: Optional system prompt to prepend

        Returns:
            LLM response dict with choices containing message and/or tool_calls

        Raises:
            httpx.HTTPStatusError: If LLM API returns error status
            httpx.ConnectError: If LLM API is unreachable
        """
        # Build messages list with system prompt first
        all_messages = []
        if system_prompt:
            all_messages.append({"role": "system", "content": system_prompt})
        all_messages.extend(messages)

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": all_messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=self._headers,
                json=payload,
            )
            resp.raise_for_status()
            return resp.json()

    def extract_tool_calls(self, response: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract tool calls from LLM response.

        Args:
            response: LLM response dict

        Returns:
            List of tool calls with name, arguments, and call_id
        """
        choices = response.get("choices", [])
        if not choices:
            return []

        message = choices[0].get("message", {})
        tool_calls = message.get("tool_calls", [])

        result = []
        for tc in tool_calls:
            function = tc.get("function", {})
            try:
                arguments = json.loads(function.get("arguments", "{}"))
            except json.JSONDecodeError:
                arguments = {}

            result.append(
                {
                    "id": tc.get("id", ""),
                    "name": function.get("name", ""),
                    "arguments": arguments,
                }
            )

        return result

    def get_response_text(self, response: dict[str, Any]) -> str:
        """Extract text response from LLM.

        Args:
            response: LLM response dict

        Returns:
            Text content of the response
        """
        choices = response.get("choices", [])
        if not choices:
            return ""

        message = choices[0].get("message", {})
        return message.get("content", "")
