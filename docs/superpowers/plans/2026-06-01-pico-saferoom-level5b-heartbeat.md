# Pico SafeRoom Level 5B Heartbeat Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add device heartbeat persistence and offline status computation.

**Architecture:** Add a shared `DeviceHeartbeat` schema. `apps/backend/main.py` exposes `/internal/heartbeats/device`. `ReadingStore` delegates heartbeat writes and device listing to `SQLiteRepository`, which updates `devices.last_seen_at` and computes status on read.

**Tech Stack:** Python 3.11.15, FastAPI, Pydantic, SQLite via `sqlite3`, pytest.

---

### Task 1: Heartbeat Schema And API Tests

**Files:**
- Create: `shared/schemas/device_heartbeat.py`
- Modify: `tests/test_backend.py`

- [ ] Write a failing test that posts a valid heartbeat and sees the device remain `online`.
- [ ] Write a failing test that a device with an old heartbeat is returned as `offline`.
- [ ] Run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm failure.

### Task 2: Repository And Route

**Files:**
- Modify: `apps/backend/db/sqlite_repository.py`
- Modify: `apps/backend/store.py`
- Modify: `apps/backend/main.py`

- [ ] Add heartbeat persistence to the repository.
- [ ] Compute device status from `last_seen_at` with a 15-second timeout.
- [ ] Add store method and FastAPI route.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm pass.

### Task 3: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
