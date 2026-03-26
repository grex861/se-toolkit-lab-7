"""Intent router for natural language queries.

Uses the LLM to interpret user messages and route to appropriate tools.
"""

from services.llm_client import LLMClient


def handle_intent(user_message: str, debug: bool = False) -> str:
    """Handle a natural language query using LLM intent routing.

    Args:
        user_message: The user's input message
        debug: Whether to print debug info to stderr

    Returns:
        The bot's response
    """
    client = LLMClient()
    return client.route(user_message, debug=debug)
