# Bot Development Plan

## Overview

This document describes the implementation plan for the LMS Telegram Bot across four tasks. The bot provides a conversational interface to the Learning Management System backend, allowing students to check their scores, view lab information, and ask questions using natural language.

## Task 1: Plan and Scaffold

**Goal:** Create project structure and development plan.

**Deliverables:**

- `bot/bot.py` — Entry point with `--test` mode
- `bot/handlers/` — Command handlers (separated from Telegram)
- `bot/services/` — API clients (for later tasks)
- `bot/config.py` — Configuration loader
- `bot/pyproject.toml` — Dependencies
- `bot/PLAN.md` — This file

**Architecture:** Testable handlers — handler functions take input and return text without depending on Telegram. The same handlers work from `--test` mode, unit tests, and Telegram.

## Task 2: Backend Integration

**Goal:** Connect bot to the LMS backend API.

**Deliverables:**

- `bot/services/lms_client.py` — HTTP client for LMS API
- Implement real `/health` — check backend availability and item count
- Implement real `/labs` — fetch lab list from backend
- Implement real `/scores <lab>` — fetch per-task pass rates from backend
- Error handling — friendly messages with actual error details

**Pattern:** API client with Bearer token authentication. All credentials loaded from environment variables.

**Implementation:**

- `/health` — Calls `GET /items/` endpoint, returns "Backend is healthy. N items available."
- `/labs` — Filters items by type="lab", formats as "- lab-01 — Lab Title"
- `/scores <lab>` — Calls `GET /analytics/pass-rates?lab=<lab_id>`, formats as "- Task: XX.X% (N attempts)"
- Error handling — Catches ConnectError, HTTPStatusError and returns user-friendly messages with error details

## Task 3: Intent-Based Natural Language Routing

**Goal:** Enable natural language queries using LLM.

**Deliverables:**

- `bot/services/llm_client.py` — LLM client for intent recognition and tool calling
- `bot/services/tools.py` — Definitions for all 9 backend endpoints as LLM tools
- `bot/handlers/intent_router.py` — Route user messages through LLM with tool calling loop
- `bot/handlers/keyboard.py` — Inline keyboard buttons for common actions

**Pattern:** LLM tool use — the LLM reads tool descriptions to decide which API calls to make. Description quality matters more than prompt engineering.

**Implementation Details:**

1. **Tool Definitions (`services/tools.py`):**
   - `get_items` — List of all labs and tasks
   - `get_learners` — Enrolled students and groups
   - `get_scores` — Score distribution for a lab
   - `get_pass_rates` — Per-task pass rates
   - `get_timeline` — Submissions per day
   - `get_groups` — Per-group scores
   - `get_top_learners` — Top N learners
   - `get_completion_rate` — Completion percentage
   - `trigger_sync` — Refresh data from autochecker

2. **LLM Client (`services/llm_client.py`):**
   - Wraps OpenAI-compatible chat completions API
   - Sends tool definitions with messages
   - Extracts tool calls from responses
   - Supports multi-turn conversation with tool results

3. **Intent Router (`handlers/intent_router.py`):**
   - Receives plain text message from user
   - Sends to LLM with tool definitions
   - Executes tool calls against backend
   - Feeds results back to LLM
   - Returns final summarized answer
   - Maximum 5 iterations to prevent loops

4. **Inline Keyboards (`handlers/keyboard.py`):**
   - `/start` keyboard: Labs, Health, Scores, Top Students, Help
   - `/help` keyboard: Additional buttons for Pass Rates, Groups
   - Dynamic lab buttons from backend data

**Tool Calling Loop:**

```
User: "which lab has the lowest pass rate?"
  → LLM receives message + 9 tool definitions
  → LLM calls: get_items()
  → Bot executes get_items(), returns 44 items
  → LLM sees result, calls: get_pass_rates(lab="lab-01"), get_pass_rates(lab="lab-02"), ...
  → Bot executes each call, returns results
  → LLM analyzes all pass rates, returns: "Lab 02 has the lowest pass rate at 58.1%"
  → Bot sends final answer to user
```

**Test Mode Usage:**

```bash
# Single-step queries
uv run bot.py --test "what labs are available"
uv run bot.py --test "show me scores for lab 4"

# Multi-step queries (require tool calling loop)
uv run bot.py --test "which lab has the lowest pass rate"
uv run bot.py --test "which group is best in lab 3"

# Fallback cases
uv run bot.py --test "hello"        # Greeting
uv run bot.py --test "asdfgh"       # Gibberish → helpful response
```

**Debug Output:**
Debug messages are printed to stderr during `--test` mode:

- `[loop]` — Iteration count
- `[tool]` — Tool calls and results
- `[response]` — Final LLM response

## Task 4: Containerize and Document

**Goal:** Deploy bot in Docker and document the solution.

**Deliverables:**

- `bot/Dockerfile` — Container image for the bot
- `docker-compose.yml` update — Add bot service
- Documentation in wiki/

**Pattern:** Docker networking — containers use service names, not `localhost`.

## Key Design Decisions

1. **Handler Separation:** Handlers are pure functions. This makes them testable without Telegram and reusable across different entry points.

2. **Environment Configuration:** All secrets (bot token, API keys) loaded from `.env.bot.secret`. Never commit secrets to git.

3. **Test Mode First:** The `--test` flag allows testing without Telegram setup. This speeds up development and enables automated testing.

4. **LLM for Intent Recognition:** Instead of regex matching, use LLM to understand user intent. This allows natural language queries like "what labs are available" instead of just `/labs`.
