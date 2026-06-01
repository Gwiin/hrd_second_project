# Pico SafeRoom Level 5D Process Logs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add process heartbeat persistence and separate developer file logs from UI logs.

**Architecture:** Add `ProcessHeartbeat` schema. `ReadingStore` accepts optional `log_path`, writes UI logs to SQLite, and appends developer logs to `logs/saferoom.log`. `SQLiteRepository` owns `process_heartbeats` and returns process status for health.

**Tech Stack:** Python 3.11.15, FastAPI, Pydantic, SQLite via `sqlite3`, pytest.

---

### Task 1: Process Heartbeat Tests

**Files:**
- Create: `shared/schemas/process_heartbeat.py`
- Modify: `tests/test_backend.py`

- [ ] Write a failing test for `POST /internal/heartbeats/process`.
- [ ] Write a failing test that `/api/health.processes` reflects persisted process status.
- [ ] Run targeted tests and confirm failure.

### Task 2: File Log Tests

**Files:**
- Modify: `tests/test_backend.py`

- [ ] Write a failing test that invalid payload logging appends to a developer log file.
- [ ] Confirm `/api/logs` still returns UI logs.

### Task 3: Implementation

**Files:**
- Modify: `apps/backend/db/sqlite_repository.py`
- Modify: `apps/backend/store.py`
- Modify: `apps/backend/main.py`

- [ ] Add process heartbeat table and repository methods.
- [ ] Add process heartbeat schema and route.
- [ ] Add file-log append path separate from SQLite UI logs.
- [ ] Re-run targeted tests and confirm pass.

### Task 4: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
