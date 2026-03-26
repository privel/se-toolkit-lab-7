"""Tool definitions for LLM function calling.

Defines all 9 backend endpoints as tools that the LLM can call.
Each tool has a name, description, and parameter schema.
"""

from typing import Any


def get_tools_definitions() -> list[dict[str, Any]]:
    """Return all tool definitions for the LLM.

    Returns:
        List of tool definitions in OpenAI function calling format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get list of all labs and tasks available in the system. Use this to discover what labs exist.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get list of enrolled learners and their groups. Use this to find student information.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab. Shows how scores are distributed across ranges.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a lab. Use this to see detailed pass rates for each task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline data showing submissions per day for a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a lab. Use this to compare group performance.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab. Use this to find the best performing students.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Number of top learners to return, e.g. 5, 10",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get completion rate percentage for a lab. Shows what fraction of students completed the lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from the autochecker to refresh data. Use this when data seems outdated.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def get_system_prompt() -> str:
    """Return the system prompt for the LLM.

    This prompt instructs the LLM to:
    1. Use tools to fetch data before answering
    2. Be helpful and concise
    3. Handle edge cases gracefully
    """
    return """You are a helpful assistant for a Learning Management System.
You have access to tools that let you fetch data about labs, students, scores, and analytics.

IMPORTANT RULES:
1. When a user asks a question about data (labs, scores, students, etc.), you MUST use the available tools to fetch the actual data before answering.
2. Do NOT make up information or guess - always call the appropriate tool first.
3. AFTER you have fetched the data you need, STOP calling tools and provide a clear, helpful answer based on the tool results.
4. Do NOT call the same tool multiple times with the same arguments - you already have the result.
5. If you have tool results that contain the answer, analyze them and respond directly. Do NOT call more tools.

For example:
- If user asks "which lab has the lowest pass rate?", call get_items() to get labs, then call get_pass_rates() for each lab, then COMPARE the results and answer. Do NOT call more tools after you have all pass rates.
- If user asks "show me scores for lab 4", call get_scores(lab="lab-04") ONCE, then format and present the results.

If the user's message is unclear or ambiguous, ask for clarification about what they want to know.

If the user greets you or says something unrelated to the LMS data, respond naturally without using tools."""
