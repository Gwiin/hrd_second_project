# Pico SafeRoom Level 5A Quality Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add standard invalid-payload responses and invalid-payload logging for backend ingest.

**Architecture:** FastAPI validation errors are handled in `apps/backend/main.py`. The handler writes a warning system log through `ReadingStore`, which delegates to `SQLiteRepository.add_log`.

**Tech Stack:** FastAPI exception handlers, SQLite via `sqlite3`, pytest.

---

### Task 1: Invalid Payload Tests

**Files:**
- Modify: `tests/test_backend.py`

- [ ] Write a failing test that invalid `/internal/events` payloads return `error.code == "VALIDATION_ERROR"`.
- [ ] Write a failing test that invalid `/internal/events` payloads appear in `/api/logs`.
- [ ] Run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm failure.

### Task 2: Error Handler And Logging

**Files:**
- Modify: `apps/backend/db/sqlite_repository.py`
- Modify: `apps/backend/store.py`
- Modify: `apps/backend/main.py`

- [ ] Add `SQLiteRepository.add_log(level, message)`.
- [ ] Add `ReadingStore.add_log(level, message)`.
- [ ] Add FastAPI `RequestValidationError` handler that logs invalid `/internal/events` payloads.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm pass.

### Task 3: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
