# Pico SafeRoom Level 5C Stale Sensors Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add query-time stale sensor detection to alert listing.

**Architecture:** `SQLiteRepository.alerts()` combines persisted threshold alerts with computed stale alerts generated from the latest reading per device/sensor. This keeps Level 5C deterministic without adding a background worker.

**Tech Stack:** Python 3.11.15, SQLite via `sqlite3`, pytest.

---

### Task 1: Stale Alert Tests

**Files:**
- Modify: `tests/test_sqlite_repository.py`
- Modify: `tests/test_backend.py`

- [ ] Write a failing repository test that an old reading appears as `sensor.stale`.
- [ ] Write a failing backend test that fresh readings do not produce stale alerts.
- [ ] Run targeted tests and confirm failure.

### Task 2: Stale Alert Implementation

**Files:**
- Modify: `apps/backend/db/sqlite_repository.py`

- [ ] Add stale threshold constant.
- [ ] Add helper to compute stale alerts from latest readings.
- [ ] Merge computed stale alerts into `alerts()`.
- [ ] Re-run targeted tests and confirm pass.

### Task 3: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
