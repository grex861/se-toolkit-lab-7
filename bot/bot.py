"""Telegram bot entry point.

Supports two modes:
1. Test mode: uv run bot.py --test "/command" - prints response to stdout
2. Telegram mode: uv run bot.py - connects to Telegram and handles messages
"""

import argparse
import sys
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)


def parse_command(text: str) -> tuple[str, str]:
    """Parse a command string into command and arguments.
    
    Args:
        text: The input text (e.g., "/scores lab-04" or "/start")
        
    Returns:
        Tuple of (command, arguments)
    """
    text = text.strip()
    if text.startswith("/"):
        parts = text[1:].split(maxsplit=1)
        command = "/" + parts[0]
        args = parts[1] if len(parts) > 1 else ""
    else:
        # Plain text - for Task 3 intent routing
        command = "/ask"
        args = text
    
    return command, args


def run_test_mode(command_text: str) -> None:
    """Run a command in test mode and print the result.
    
    Args:
        command_text: The command to run (e.g., "/start", "/help")
    """
    command, args = parse_command(command_text)
    
    # Route to appropriate handler
    if command == "/start":
        response = handle_start()
    elif command == "/help":
        response = handle_help()
    elif command == "/health":
        response = handle_health()
    elif command == "/labs":
        response = handle_labs()
    elif command == "/scores":
        response = handle_scores(args)
    elif command == "/ask":
        # Task 3: LLM intent routing
        response = "Plain text queries will be handled by LLM in Task 3."
    else:
        response = f"Unknown command: {command}. Use /help to see available commands."
    
    print(response)


def run_telegram_mode() -> None:
    """Run the bot in Telegram mode (connects to Telegram API)."""
    # Task 2: Implement Telegram bot
    print("Telegram mode not yet implemented. Will be added in Task 2.")
    print("For now, use --test mode to test handlers.")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  uv run bot.py --test "/start"      # Test /start command
  uv run bot.py --test "/help"       # Test /help command
  uv run bot.py                      # Run in Telegram mode
""",
    )
    parser.add_argument(
        "--test",
        type=str,
        metavar="COMMAND",
        help="Run a command in test mode (no Telegram connection)",
    )
    
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_mode()


if __name__ == "__main__":
    main()
