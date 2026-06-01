# Pico SafeRoom Level 2A Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add SQLite-backed persistence for accepted sensor readings and recent system logs while preserving the Level 1 API shape.

**Architecture:** `ReadingStore` remains the backend-facing boundary. A new `SQLiteRepository` owns schema initialization, inserts, latest reading queries, history queries, and log queries using Python's built-in `sqlite3` module.

**Tech Stack:** Python 3.11.15, FastAPI, Pydantic, pytest, SQLite via `sqlite3`, React/Vite unchanged.

---

### Task 1: Repository Tests

**Files:**
- Create: `tests/test_sqlite_repository.py`
- Create: `apps/backend/db/__init__.py`
- Create: `apps/backend/db/sqlite_repository.py`

- [ ] Write a failing test that creates a temporary database, inserts a `SensorEvent`, creates a second repository on the same path, and verifies the latest reading is still present.
- [ ] Write a failing test that inserting the same `event_id` twice leaves one history row.
- [ ] Run `.venv/bin/python -m pytest tests/test_sqlite_repository.py -v` and confirm failure because `SQLiteRepository` does not exist.
- [ ] Implement `SQLiteRepository` with schema creation and event insertion.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_sqlite_repository.py -v` and confirm pass.

### Task 2: Backend API Integration

**Files:**
- Modify: `apps/backend/store.py`
- Modify: `apps/backend/main.py`
- Modify: `tests/test_backend.py`

- [ ] Write a failing backend test that posts a reading to an app with a temporary database path, creates a second app with the same path, and verifies `/api/readings/latest` still returns the reading.
- [ ] Write a failing backend test for `/api/readings/history`.
- [ ] Run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm failure because `create_app` does not accept `db_path` and history route is missing.
- [ ] Update `create_app(db_path: Path | None = None)` and `ReadingStore(db_path: Path | None = None)`.
- [ ] Add `/api/readings/history` delegating to `ReadingStore.reading_history`.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm pass.

### Task 3: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
- [ ] Run `git status --short` and review changed files.
