# Pico SafeRoom Level 4 Realtime Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add WebSocket realtime updates for sensor readings and show live connection state in the dashboard.

**Architecture:** `apps/backend/realtime.py` owns connection tracking and broadcast. `apps/backend/main.py` exposes `/ws/realtime` and broadcasts `reading.created` after ingest. `frontend/src/App.tsx` opens the WebSocket and merges incoming readings into current dashboard state.

**Tech Stack:** FastAPI WebSocket, React, TypeScript, pytest.

---

### Task 1: Backend WebSocket

**Files:**
- Create: `apps/backend/realtime.py`
- Modify: `apps/backend/main.py`
- Modify: `tests/test_backend.py`

- [ ] Write a failing test that connects to `/ws/realtime`, posts `/internal/events`, and receives `reading.created`.
- [ ] Run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm failure.
- [ ] Add realtime connection manager and WebSocket route.
- [ ] Broadcast accepted readings after persistence.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm pass.

### Task 2: Frontend Realtime

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/App.css`

- [ ] Add WebSocket connection state.
- [ ] Merge `reading.created` messages into current readings.
- [ ] Keep REST refresh as fallback.
- [ ] Run `npm --prefix frontend run build`.

### Task 3: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
