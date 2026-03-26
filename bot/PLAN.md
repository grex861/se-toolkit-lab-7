# Development Plan for LMS Telegram Bot

This document outlines the development plan for the LMS Telegram Bot that connects to the LMS API and provides analytics for learners.

## Goals
- Implement a Telegram bot that listens for commands like `/start`, `/help`, `/health`, and learners‑related requests.
- Retrieve course analytics from the LMS API (items, scores, submissions, etc.).
- Display charts or textual summaries in response to user queries.
- Handle authentication and error cases gracefully (no crashing on unknown commands).
- **Task 3**: Add LLM-powered intent routing for natural language queries.

## Infrastructure
- The bot runs on the VM via `uv run` or `docker-compose` in the `se-toolkit-lab-7` repository.
- The LMS API is exposed on `http://<lms-api-base-url>` (`localhost:42002` on VM) with `LMS_API_KEY` for authentication.
- The LLM API is exposed on `http://<llm-api-base-url>` (`10.93.26.101:42005` on VM) with `LLM_API_KEY` for authentication.
- Environment variables are stored in `.env.bot.secret` (`BOT_TOKEN`, `LMS_API_BASE_URL`, `LMS_API_KEY`, `LLM_API_KEY`, `LLM_API_BASE_URL`, `LLM_API_MODEL`).

## Components
- `bot/bot.py` — main entry point, sets up the Telegram handlers and links them to business logic.
- `bot/handlers/` — pure functions that handle commands and queries, separated from the Telegram API.
  - `handlers/commands.py` — slash command handlers (`/start`, `/help`, `/health`, `/labs`, `/scores`)
  - `handlers/intent_router.py` — LLM-powered natural language intent router
- `bot/config.py` — central config for API URLs, keys, and logging.
- `bot/services/` — service layer for external API calls.
  - `services/api_client.py` — LMS API client with all 9 endpoint wrappers
  - `services/llm_client.py` — LLM client with tool calling support

## Implementation Steps

### Task 1: Project Structure and Test Mode
1. Set up the project structure (`bot/PLAN.md`, `bot/handlers/__init__.py`, `bot/handlers/commands.py`).
2. Define handlers for `/start`, `/help`, `/health`, `/labs`, and `/scores`.
3. Implement `--test` mode for local testing without Telegram connection.
4. Test each handler locally with `uv run bot.py --test "/health"`.

### Task 2: Backend Integration
1. Implement API client (`services/api_client.py`) to call `LMS_API_BASE_URL` with `Authorization: Bearer` header.
2. Add all required endpoint functions: `get_items()`, `get_pass_rates(lab)`.
3. Update handlers to use real API data.
4. Deploy the bot on the VM and verify it works in Telegram.

### Task 3: Intent-Based Natural Language Routing (COMPLETED)
1. **Add LLM client** (`services/llm_client.py`):
   - Define all 9 backend endpoints as LLM tool schemas
   - Implement tool calling loop with OpenAI-compatible API
   - Handle multi-turn conversations (feed tool results back to LLM)
   - Prevent infinite retry loops for empty results

2. **Tool schemas defined**:
   - `get_items` — List of labs and tasks
   - `get_learners` — Enrolled students and groups
   - `get_scores` — Score distribution (4 buckets)
   - `get_pass_rates` — Per-task averages and attempt counts
   - `get_timeline` — Submissions per day
   - `get_groups` — Per-group scores and student counts
   - `get_top_learners` — Top N learners by score
   - `get_completion_rate` — Completion rate percentage
   - `trigger_sync` — Refresh data from autochecker

3. **Intent router** (`handlers/intent_router.py`):
   - Simple wrapper that calls LLM client
   - Returns LLM's final response after tool execution

4. **Update bot.py**:
   - Add `--test` mode support for plain text queries
   - Route plain text to LLM intent router
   - Add inline keyboard buttons for common actions

5. **System prompt design**:
   - Encourage parallel tool calls (call all tools at once)
   - Work with empty results instead of retrying
   - Handle greetings and ambiguous queries gracefully

6. **Testing**:
   - Single-step queries: "what labs are available", "show me scores for lab 4"
   - Multi-step queries: "which lab has the lowest pass rate"
   - Fallback cases: "asdfgh" (gibberish), "hello" (greeting), "lab 4" (ambiguous)

### Task 4: Containerize and Deploy
1. Create Dockerfile for the bot.
2. Add bot service to `docker-compose.yml`.
3. Deploy to VM and verify in Telegram.

## Risk Mitigation
- Use structured logging and error handling to avoid crashes on invalid inputs.
- Validate that the LMS API responses are correct before rendering output.
- Keep handlers small and testable.
- **LLM-specific**: Track tool call history to prevent infinite retry loops.
- **LLM-specific**: Use system prompt to encourage parallel tool calls.

## Acceptance Criteria (Task 3)

### On GitHub
- [x] Git workflow followed (issue, branch, PR, review, merge)
- [x] Source code contains keyboard/button setup
- [x] Source code defines at least 9 tool/function schemas
- [x] The LLM decides which tool to call — no regex or keyword matching
- [x] Tool results are fed back to the LLM for the final answer

### On the VM (REMOTE)
- [x] `--test "what labs are available"` returns non-empty answer (at least 20 chars)
- [x] `--test "which lab has the lowest pass rate"` mentions a specific lab
- [x] `--test "asdfgh"` returns a helpful message, no crash

## Testing Commands

```bash
# Single-step queries
uv run bot.py --test "what labs are available"
uv run bot.py --test "show me scores for lab 4"
uv run bot.py --test "who are the top 5 students in lab 4"

# Multi-step queries
uv run bot.py --test "which lab has the lowest pass rate"
uv run bot.py --test "which group is doing best in lab 3"

# Fallback and edge cases
uv run bot.py --test "asdfgh"      # gibberish
uv run bot.py --test "hello"       # greeting
uv run bot.py --test "lab 4"       # ambiguous
```
