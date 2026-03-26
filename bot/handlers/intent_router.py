"""Intent-based natural language router.

Routes user messages through LLM with tool calling:
1. User sends plain text message
2. LLM decides which tool(s) to call based on message
3. Bot executes tool calls against backend
4. Tool results fed back to LLM
5. LLM produces final answer
"""

import sys
from typing import Any

from config import load_config
from services import LLMClient, LMSClient, get_tools_definitions, get_system_prompt


# Maximum iterations to prevent infinite loops
MAX_ITERATIONS = 5


async def route(message: str, debug: bool = True) -> str:
    """Route a user message through LLM with tool calling.

    Args:
        message: User's plain text message
        debug: If True, print debug info to stderr

    Returns:
        Final response text
    """
    config = load_config()

    # Check if LLM is configured
    if not config.get("llm_api_base_url") or not config.get("llm_api_key"):
        return "LLM is not configured. Please set LLM_API_BASE_URL and LLM_API_KEY in .env.bot.secret"

    # Initialize clients
    llm_client = LLMClient(
        api_key=config["llm_api_key"],
        base_url=config["llm_api_base_url"],
        model=config.get("llm_api_model", "coder-model"),
    )

    lms_client = LMSClient(
        base_url=config["lms_api_base_url"],
        api_key=config["lms_api_key"],
    )

    # Get tool definitions and system prompt
    tools = get_tools_definitions()
    system_prompt = get_system_prompt()

    # Conversation history
    messages: list[dict[str, Any]] = [
        {"role": "user", "content": message}
    ]

    # Tool call results for building tool response messages
    tool_results: list[dict[str, Any]] = []

    iteration = 0
    while iteration < MAX_ITERATIONS:
        iteration += 1

        if debug:
            print(
                f"[loop] Iteration {iteration}, {len(messages)} messages",
                file=sys.stderr,
            )

        # Call LLM
        response = await llm_client.chat(
            messages=messages,
            tools=tools,
            system_prompt=system_prompt,
        )

        # Extract tool calls
        tool_calls = llm_client.extract_tool_calls(response)

        # If no tool calls, LLM has a final answer
        if not tool_calls:
            response_text = llm_client.get_response_text(response)
            if debug and response_text:
                print(
                    f"[response] LLM returned text response",
                    file=sys.stderr,
                )
            return response_text or "I'm not sure how to help with that. Try asking about labs, scores, or students."

        # Execute each tool call
        for tool_call in tool_calls:
            tool_name = tool_call["name"]
            tool_args = tool_call["arguments"]
            tool_id = tool_call["id"]

            if debug:
                print(
                    f"[tool] LLM called: {tool_name}({tool_args})",
                    file=sys.stderr,
                )

            # Execute the tool
            try:
                result = await _execute_tool(tool_name, tool_args, lms_client)
                result_str = _format_tool_result(result)

                if debug:
                    print(
                        f"[tool] Result: {result_str[:100]}{'...' if len(result_str) > 100 else ''}",
                        file=sys.stderr,
                    )

                # Store result for feeding back to LLM
                tool_results.append({
                    "tool_call_id": tool_id,
                    "result": result,
                })

            except Exception as e:
                if debug:
                    print(
                        f"[tool] Error executing {tool_name}: {e}",
                        file=sys.stderr,
                    )
                tool_results.append({
                    "tool_call_id": tool_id,
                    "result": {"error": str(e)},
                })

        # Feed tool results back to LLM
        if debug:
            print(
                f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM",
                file=sys.stderr,
            )

        # Build tool response messages
        for tr in tool_results:
            messages.append({
                "role": "tool",
                "tool_call_id": tr["tool_call_id"],
                "content": _format_tool_result(tr["result"]),
            })

        # Clear tool results for next iteration
        tool_results = []

    # If we hit max iterations, return what we have
    return "I'm having trouble processing your request. Please try rephrasing your question."


async def _execute_tool(
    tool_name: str, arguments: dict[str, Any], lms_client: LMSClient
) -> Any:
    """Execute a tool call against the LMS backend.

    Args:
        tool_name: Name of the tool to call
        arguments: Tool arguments from LLM
        lms_client: LMS client instance

    Returns:
        Tool result (depends on tool)
    """
    # Map tool names to LMS client methods
    tool_methods = {
        "get_items": lms_client.get_items,
        "get_learners": lms_client.get_learners,
        "get_scores": lms_client.get_scores,
        "get_pass_rates": lms_client.get_pass_rates,
        "get_timeline": lms_client.get_timeline,
        "get_groups": lms_client.get_groups,
        "get_top_learners": lms_client.get_top_learners,
        "get_completion_rate": lms_client.get_completion_rate,
        "trigger_sync": lms_client.trigger_sync,
    }

    method = tool_methods.get(tool_name)
    if not method:
        raise ValueError(f"Unknown tool: {tool_name}")

    # Call the method with arguments
    result = await method(**arguments)
    return result


def _format_tool_result(result: Any) -> str:
    """Format a tool result for the LLM.

    Args:
        result: Tool result (list, dict, or primitive)

    Returns:
        Formatted string representation
    """
    if isinstance(result, list):
        if len(result) == 0:
            return "[]"
        # Summarize long lists
        if len(result) > 20:
            return f"[{len(result)} items, showing first 5: {result[:5]}]"
        return str(result)
    elif isinstance(result, dict):
        return str(result)
    else:
        return str(result)
