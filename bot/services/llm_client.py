"""LLM client with tool calling support.

Handles communication with the LLM API, including:
- Building tool schemas for all 9 backend endpoints
- Sending user messages with tool definitions
- Parsing tool call responses
- Feeding tool results back for multi-turn reasoning
"""

import json
import sys
from typing import Any
from openai import OpenAI
from config import load_config


def get_tool_schemas() -> list[dict[str, Any]]:
    """Define all 9 backend endpoints as LLM tools.

    Returns:
        List of tool schemas in OpenAI function calling format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get the list of all labs and tasks available in the system. Use this to discover what labs exist.",
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
                "description": "Get the list of enrolled students and their groups. Use this to find information about learners.",
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
                "description": "Get score distribution (4 buckets) for a specific lab. Use this to see how scores are distributed across ranges.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average scores and attempt counts for a specific lab. Use this to see detailed pass rates for each task.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline data (submissions per day) for a specific lab. Use this to see when students submitted.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group scores and student counts for a specific lab. Use this to compare how different groups performed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a specific lab. Use this to find the best performing students.",
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
                            "default": 10,
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
                "description": "Get the completion rate percentage for a specific lab. Use this to see what percentage of students completed the lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g. 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from the autochecker to refresh the backend data. Use this when the user asks to update or refresh data.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]


def get_system_prompt() -> str:
    """Get the system prompt that guides the LLM's behavior.

    Returns:
        System prompt string.
    """
    return """You are a helpful assistant for an LMS (Learning Management System). You have access to tools that let you query data about labs, students, scores, and pass rates.

When a user asks a question:
1. Think about what data you need to answer the question
2. Call ALL the tools you need at ONCE - don't call them one at a time
3. For example, if you need pass rates for multiple labs, call get_pass_rates for ALL labs in a single response
4. If some tools return empty results, work with the data you have - don't keep retrying
5. Once you have the data, summarize it clearly for the user

If the user's message is a greeting or casual conversation, respond naturally without using tools.

If the user's message is unclear or ambiguous, ask for clarification about what they want to know.

Always be helpful and provide data-driven answers when possible."""


class LLMClient:
    """Client for communicating with the LLM API."""

    def __init__(self) -> None:
        """Initialize the LLM client."""
        config = load_config()
        self.api_key = config.get("LLM_API_KEY", "")
        self.base_url = config.get("LLM_API_BASE_URL", "")
        self.model = config.get("LLM_API_MODEL", "coder-model")

        # Ensure /v1 suffix is present for OpenAI-compatible API
        base_url_clean = self.base_url.rstrip("/")
        if not base_url_clean.endswith("/v1"):
            base_url_clean = base_url_clean + "/v1"

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url_clean,
        )
        self.tool_schemas = get_tool_schemas()

    def _execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool by calling the appropriate backend function.

        Args:
            name: The tool name (e.g., "get_items", "get_pass_rates")
            arguments: The arguments for the tool

        Returns:
            The result from the tool

        Raises:
            ValueError: If the tool name is unknown
        """
        # Import here to avoid circular imports
        from services.api_client import (
            get_items,
            get_pass_rates,
            get_learners,
            get_scores,
            get_timeline,
            get_groups,
            get_top_learners,
            get_completion_rate,
            trigger_sync,
        )

        tools = {
            "get_items": get_items,
            "get_learners": get_learners,
            "get_scores": lambda **kwargs: get_scores(kwargs.get("lab", "")),
            "get_pass_rates": lambda **kwargs: get_pass_rates(kwargs.get("lab", "")),
            "get_timeline": lambda **kwargs: get_timeline(kwargs.get("lab", "")),
            "get_groups": lambda **kwargs: get_groups(kwargs.get("lab", "")),
            "get_top_learners": lambda **kwargs: get_top_learners(
                kwargs.get("lab", ""), kwargs.get("limit", 10)
            ),
            "get_completion_rate": lambda **kwargs: get_completion_rate(
                kwargs.get("lab", "")
            ),
            "trigger_sync": trigger_sync,
        }

        if name not in tools:
            raise ValueError(f"Unknown tool: {name}")

        return tools[name](**arguments)

    def route(self, user_message: str, debug: bool = False) -> str:
        """Route a user message through the LLM to get a response.

        This implements the tool calling loop:
        1. Send user message + tool schemas to LLM
        2. If LLM returns tool calls, execute them
        3. Feed tool results back to LLM
        4. Return the final response

        Args:
            user_message: The user's input message
            debug: Whether to print debug info to stderr

        Returns:
            The LLM's response text
        """

        def log_debug(msg: str) -> None:
            if debug:
                print(msg, file=sys.stderr)

        # Track tool calls to prevent infinite retry loops
        seen_tool_calls: set[str] = set()
        empty_result_retries: dict[str, int] = {}
        MAX_EMPTY_RETRIES = 2

        # Initialize conversation with system prompt and user message
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": get_system_prompt()},
            {"role": "user", "content": user_message},
        ]

        max_iterations = 20  # Prevent infinite loops (increased for multi-step queries)
        iteration = 0

        while iteration < max_iterations:
            iteration += 1

            # Call the LLM
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tool_schemas,
                tool_choice="auto",
            )

            choice = response.choices[0]
            assistant_message = choice.message

            # Check if the LLM wants to call tools
            if assistant_message.tool_calls:
                # First, add the assistant message with tool_calls
                messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments,
                                },
                            }
                            for tc in assistant_message.tool_calls
                        ],
                    }
                )

                # Execute each tool call and add tool results
                for tool_call in assistant_message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    tool_call_id = tool_call.id

                    # Create a key to track this specific tool call
                    tool_key = f"{tool_name}:{json.dumps(tool_args, sort_keys=True)}"

                    # Check if we've seen this tool call before with empty results
                    if tool_key in seen_tool_calls:
                        empty_count = empty_result_retries.get(tool_key, 0)
                        if empty_count >= MAX_EMPTY_RETRIES:
                            log_debug(f"[tool] Skipping retry of {tool_name} (already tried {empty_count} times with empty results)")
                            # Add a message saying we already tried this
                            messages.append(
                                {
                                    "role": "tool",
                                    "tool_call_id": tool_call_id,
                                    "content": json.dumps({"error": "Already attempted - no data available"}),
                                }
                            )
                            continue

                    seen_tool_calls.add(tool_key)
                    log_debug(f"[tool] LLM called: {tool_name}({tool_args})")

                    try:
                        result = self._execute_tool(tool_name, tool_args)
                        result_str = json.dumps(result, default=str)
                        log_debug(f"[tool] Result: {len(result_str)} chars")

                        # Track empty results
                        if result_str == "[]" or result_str == "{}":
                            empty_result_retries[tool_key] = empty_result_retries.get(tool_key, 0) + 1
                    except Exception as e:
                        result_str = json.dumps({"error": str(e)})
                        log_debug(f"[tool] Error: {e}")

                    # Add tool result to conversation
                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": result_str,
                        }
                    )

                log_debug(f"[summary] Feeding {len(assistant_message.tool_calls)} tool result(s) back to LLM")
                # Continue the loop - LLM will see tool results and respond

            else:
                # No tool calls - LLM has a final response
                response_text = assistant_message.content or ""
                return response_text

        # Max iterations reached - return what we have
        return "I'm having trouble processing your request. Please try rephrasing your question."
