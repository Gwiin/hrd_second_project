# Pico SafeRoom Level 2B Alerts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add persisted threshold alerts and alert APIs so Level 4 realtime work can broadcast meaningful alert data later.

**Architecture:** Keep alert creation inside `SQLiteRepository.add_event()` for Level 2B. `ReadingStore` delegates alert listing and acknowledgement to the repository. FastAPI exposes `GET /api/alerts` and `POST /api/alerts/{alert_id}/ack`.

**Tech Stack:** Python 3.11.15, FastAPI, SQLite via `sqlite3`, pytest.

---

### Task 1: Repository Alerts

**Files:**
- Modify: `apps/backend/db/sqlite_repository.py`
- Modify: `tests/test_sqlite_repository.py`

- [ ] Write a failing test that a gas warning reading creates one persisted alert.
- [ ] Write a failing test that acknowledging an alert changes status to `acknowledged`.
- [ ] Run `.venv/bin/python -m pytest tests/test_sqlite_repository.py -v` and confirm failure.
- [ ] Add `alerts` table, threshold alert insertion, alert listing, and alert acknowledgement.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_sqlite_repository.py -v` and confirm pass.

### Task 2: Backend Alert API

**Files:**
- Modify: `apps/backend/store.py`
- Modify: `apps/backend/main.py`
- Modify: `tests/test_backend.py`

- [ ] Write failing tests for `GET /api/alerts` and `POST /api/alerts/{alert_id}/ack`.
- [ ] Run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm failure.
- [ ] Add store methods and FastAPI routes.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm pass.

### Task 3: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
- [ ] Review `git status --short`.
