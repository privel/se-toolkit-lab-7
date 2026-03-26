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

- `bot/services/llm_client.py` — LLM client for intent recognition
- `bot/handlers/intent_router.py` — Route user messages to handlers based on intent
- Tool descriptions for LLM to understand available commands

**Pattern:** LLM tool use — the LLM reads tool descriptions to decide which handler to call. Description quality matters more than prompt engineering.

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
