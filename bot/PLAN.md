# Development Plan for LMS Telegram Bot

This document outlines the development plan for the LMS Telegram Bot that connects to the LMS API and provides analytics for learners.

## Goals
- Implement a Telegram bot that listens for commands like `/start`, `/help`, `/health`, and learners‑related requests.
- Retrieve course analytics from the LMS API (items, scores, submissions, etc.).
- Display charts or textual summaries in response to user queries.
- Handle authentication and error cases gracefully (no crashing on unknown commands).

## Infrastructure
- The bot runs on the VM via `uv run` or `docker-compose` in the `se-toolkit-lab-7` repository.
- The LMS API is exposed on `http://<lms-api-base-url>` (`localhost:42002` on VM) with `LMS_API_KEY` for authentication.
- Environment variables are stored in `.env.bot.secret` (`BOT_TOKEN`, `LMS_API_BASE_URL`, `LMS_API_KEY`, etc.).

## Components
- `bot/bot.py` — main entry point, sets up the Telegram handlers and links them to business logic.
- `bot/handlers/` — pure functions that handle commands and queries, separated from the Telegram API.
- `bot/config.py` (optional) — central config for API URLs, keys, and logging.

## Implementation Steps
1. Set up the project structure (`bot/PLAN.md`, `bot/handlers/__init__.py`, `bot/handlers/commands.py`).
2. Define handlers for `/start`, `/help`, `/health`, and `/analytics`.
3. Implement a client to call `LMS_API_BASE_URL` with `Authorization: Bearer` header.
4. Test each handler locally with `uv run --env-file .env.bot.secret python bot/bot.py --test "/health"`.
5. Deploy the bot on the VM with `uv run poe bot` or via `docker compose` and verify it works in Telegram.

## Risk Mitigation
- Use structured logging and error handling to avoid crashes on invalid inputs.
- Validate that the LMS API responses are correct before rendering output.
- Keep handlers small and testable.

This plan outlines the overall architecture and development milestones required to implement the LMS Telegram Bot.
