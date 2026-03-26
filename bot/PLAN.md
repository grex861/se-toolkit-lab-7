# Development Plan — LMS Telegram Bot

## Overview

This document outlines the implementation plan for building a Telegram bot that allows users to interact with the LMS (Learning Management System) backend. The bot will support slash commands like `/health`, `/labs`, and `/scores`, as well as natural language queries powered by an LLM.

## Task 1: Project Scaffold (Current)

**Goal:** Establish a testable project structure with handler separation.

**Approach:**
- Create a `bot/` directory with clear separation between handlers (business logic) and transport (Telegram)
- Implement `--test` mode that calls handlers directly without Telegram
- Build placeholder handlers for `/start`, `/help`, `/health`, `/labs`, `/scores`
- Set up `pyproject.toml` with dependencies (aiogram, httpx, python-dotenv)
- Create configuration loader that reads from `.env.bot.secret`

**Why this matters:** Testable handlers mean we can verify logic without deploying to Telegram. The same handler function works in `--test` mode, unit tests, and production.

## Task 2: Backend Integration

**Goal:** Connect handlers to the LMS backend API.

**Approach:**
- Create `services/api_client.py` with Bearer token authentication
- Implement real `/health` handler that calls `GET /health` on backend
- Implement `/labs` handler that calls `GET /items` to list labs
- Implement `/scores <lab>` handler that calls analytics endpoints
- Add error handling for network failures, auth errors, and backend downtime
- Return user-friendly messages when things go wrong

**Key pattern:** API client is a separate service. Handlers call the client, not HTTP directly. This makes testing easier and keeps concerns separated.

## Task 3: Intent-Based Natural Language Routing

**Goal:** Let users ask questions in plain language.

**Approach:**
- Create `services/llm_client.py` to communicate with the LLM API
- Define tool descriptions for each backend endpoint (what it does, what params it needs)
- Build intent router that sends user query + tool descriptions to LLM
- LLM decides which tool to call and with what arguments
- Execute the tool and return the result to the user

**Why LLM routing:** Instead of regex or keyword matching, the LLM understands intent. "Show me lab 4 scores" and "what did I get on lab-04?" both map to the scores tool.

**Critical:** Tool description quality matters more than prompt engineering. Clear, specific descriptions = reliable tool selection.

## Task 4: Containerization and Deployment

**Goal:** Deploy the bot alongside the existing backend on the VM.

**Approach:**
- Create `Dockerfile` for the bot (multi-stage build with uv)
- Add bot service to `docker-compose.yml`
- Configure container networking (bot talks to backend via service name, not localhost)
- Document deployment process in README
- Set up health checks and restart policies

**Docker networking insight:** Inside Docker Compose, containers use service names as hostnames. The bot connects to `http://backend:42002`, not `localhost:42002`.

## Architecture Summary

```
User (Telegram) → Bot Entry Point → Handler → Service → External API
                      ↓
                 --test mode (same handler, no Telegram)
```

**Handlers:** Pure functions. Input → text output. No Telegram, no HTTP, no side effects.

**Services:** API clients (LMS backend, LLM). Handle HTTP, auth, retries, error handling.

**Entry Point:** Telegram bot startup OR `--test` CLI. Routes to handlers.

## Testing Strategy

1. **Unit tests:** Test handlers with mock services
2. **Test mode:** Manual verification via `--test` flag
3. **Integration tests:** Test full flow with real backend (Task 2+)
4. **Deploy verification:** Test in Telegram after deployment

## Git Workflow

For each task:
1. Create issue on GitHub
2. Branch: `task-N-short-description`
3. Implement, test locally
4. PR with "Closes #..." in description
5. Partner review, then merge

## Success Criteria

- **P0:** All slash commands work with real backend data
- **P1:** Natural language queries routed correctly by LLM
- **P3:** Bot deployed and running on VM, accessible in Telegram
