"""Telegram bot entry point.

Supports two modes:
1. Test mode: uv run bot.py --test "/command" - prints response to stdout
2. Telegram mode: uv run bot.py - connects to Telegram and handles messages
"""

import argparse
import logging
import sys
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.intent_router import handle_intent
from config import load_config


logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)


def get_main_keyboard() -> InlineKeyboardMarkup:
    """Create an inline keyboard with common actions.

    Returns:
        Inline keyboard markup with buttons for common queries.
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📋 Available Labs", callback_data="labs"),
            InlineKeyboardButton(text="💚 Health Check", callback_data="health"),
        ],
        [
            InlineKeyboardButton(text="📊 Scores", callback_data="scores"),
            InlineKeyboardButton(text="🏆 Top Students", callback_data="top"),
        ],
        [
            InlineKeyboardButton(text="❓ Help", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


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
        # Task 3: LLM intent routing - enable debug output to stderr
        response = handle_intent(args, debug=True)
    else:
        response = f"Unknown command: {command}. Use /help to see available commands."

    print(response)


async def handle_start_command(message: types.Message) -> None:
    """Handle /start command from Telegram."""
    response = handle_start()
    keyboard = get_main_keyboard()
    await message.reply(response, reply_markup=keyboard)


async def handle_help_command(message: types.Message) -> None:
    """Handle /help command from Telegram."""
    response = handle_help()
    await message.reply(response)


async def handle_health_command(message: types.Message) -> None:
    """Handle /health command from Telegram."""
    response = handle_health()
    await message.reply(response)


async def handle_labs_command(message: types.Message) -> None:
    """Handle /labs command from Telegram."""
    response = handle_labs()
    await message.reply(response)


async def handle_scores_command(message: types.Message) -> None:
    """Handle /scores command from Telegram."""
    # Extract the lab argument from the command
    # Message text is like "/scores lab-04" or "/scores@botname lab-04"
    text = message.text or ""
    parts = text.split(maxsplit=1)
    lab_name = parts[1] if len(parts) > 1 else ""

    response = handle_scores(lab_name)
    await message.reply(response)


async def handle_unknown_command(message: types.Message) -> None:
    """Handle unknown commands and plain text from Telegram."""
    text = message.text or ""
    command, args = parse_command(text)

    if command == "/ask":
        # Task 3: LLM intent routing
        response = handle_intent(args, debug=True)
    else:
        response = f"Unknown command: {command}. Use /help to see available commands."

    await message.reply(response)


async def handle_callback(message: types.CallbackQuery) -> None:
    """Handle inline keyboard button clicks."""
    action = message.data
    response = ""

    if action == "labs":
        response = handle_labs()
    elif action == "health":
        response = handle_health()
    elif action == "scores":
        response = "Please specify a lab, e.g., /scores lab-04"
    elif action == "top":
        response = "Please specify a lab, e.g., ask 'who are the top 5 students in lab 4'"
    elif action == "help":
        response = handle_help()
    else:
        response = "Unknown action."

    await message.message.edit_text(response)


def run_telegram_mode() -> None:
    """Run the bot in Telegram mode (connects to Telegram API)."""
    config = load_config()
    bot_token = config.get("BOT_TOKEN", "")

    if not bot_token:
        logger.error("BOT_TOKEN is not set. Please configure .env.bot.secret")
        return

    bot = Bot(token=bot_token)
    dp = Dispatcher()

    # Register command handlers
    dp.message(CommandStart())(handle_start_command)
    dp.message(Command("help"))(handle_help_command)
    dp.message(Command("health"))(handle_health_command)
    dp.message(Command("labs"))(handle_labs_command)
    dp.message(Command("scores"))(handle_scores_command)

    # Handle callback queries (inline buttons)
    dp.callback_query()(handle_callback)

    # Handle plain text messages (LLM intent routing)
    dp.message()(handle_unknown_command)

    logger.info("Starting bot in Telegram mode...")
    dp.run_polling(bot)


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
