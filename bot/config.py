"""Configuration loader for the Telegram bot.

Reads environment variables from .env.bot.secret file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from environment variables.

    Returns:
        Dictionary with configuration values.
    """
    # Load from .env.bot.secret file
    env_path = Path(__file__).parent.parent / ".env.bot.secret"
    load_dotenv(env_path)

    return {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_BASE_URL": os.getenv("LMS_API_BASE_URL", ""),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", ""),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", "coder-model"),
    }
