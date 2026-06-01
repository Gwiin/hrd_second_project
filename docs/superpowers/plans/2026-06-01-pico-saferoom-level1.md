# Pico SafeRoom Level 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a runnable Level 1 Pico SafeRoom skeleton that proves backend, collector, worker, desktop, and dashboard boundaries with mock sensor data for four real Pico 2W device identities.

**Architecture:** The collector simulator posts normalized `SensorEvent` data for `pico-safe-001` through `pico-safe-004` to a FastAPI backend. The backend stores latest readings in memory and serves the React dashboard. The desktop launcher starts backend, collector, and worker as separate child processes and opens the dashboard through pywebview when available.

**Tech Stack:** Python 3.11.15 in `.venv`, FastAPI, Pydantic, pytest, httpx, pywebview, React, Vite, TypeScript, CSS.

---

### Task 1: Shared Schema

**Files:**
- Create: `.python-version`
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `shared/__init__.py`
- Create: `shared/schemas/__init__.py`
- Create: `shared/schemas/sensor_event.py`
- Test: `tests/test_sensor_event.py`

- [ ] Write tests proving valid readings parse and invalid quality is rejected.
- [ ] Create `.venv` with Python 3.11.15 and install `requirements.txt`.
- [ ] Run `.venv/bin/python -m pytest tests/test_sensor_event.py -v` and confirm the tests fail before implementation.
- [ ] Implement `SensorEvent` with Pydantic.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_sensor_event.py -v` and confirm it passes.

### Task 2: Backend API

**Files:**
- Create: `apps/__init__.py`
- Create: `apps/backend/__init__.py`
- Create: `apps/backend/store.py`
- Create: `apps/backend/devices.py`
- Create: `apps/backend/main.py`
- Test: `tests/test_backend.py`

- [ ] Write tests for `/api/health`, `/api/devices`, `/internal/events`, and `/api/readings/latest`.
- [ ] Run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm the tests fail before implementation.
- [ ] Implement in-memory backend store and FastAPI routes.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_backend.py -v` and confirm it passes.

### Task 3: Collector Simulator

**Files:**
- Create: `apps/collector/__init__.py`
- Create: `apps/collector/simulator.py`
- Create: `apps/collector/main.py`
- Test: `tests/test_collector_simulator.py`

- [ ] Write tests proving generated events match the shared schema and include all Level 1 sensors for all four device IDs.
- [ ] Run `.venv/bin/python -m pytest tests/test_collector_simulator.py -v` and confirm it fails before implementation.
- [ ] Implement sensor event generation and HTTP posting loop.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_collector_simulator.py -v` and confirm it passes.

### Task 4: Worker And Desktop Launcher

**Files:**
- Create: `apps/worker/__init__.py`
- Create: `apps/worker/main.py`
- Create: `apps/desktop/__init__.py`
- Create: `apps/desktop/app.py`

- [ ] Implement worker heartbeat loop.
- [ ] Implement process launcher with backend readiness polling.
- [ ] Implement pywebview opening with printed URL fallback.

### Task 5: Frontend Dashboard

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/index.html`
- Create: `frontend/tsconfig.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/App.css`

- [ ] Install React/Vite dependencies.
- [ ] Implement the accepted dashboard concept as a real app screen.
- [ ] Fetch `/api/health` and `/api/readings/latest`.
- [ ] Show seeded fallback data before readings arrive.
- [ ] Run `npm --prefix frontend run build` and confirm it passes.

### Task 6: Validation And Runtime Smoke

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `README.md`

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
- [ ] Run backend and post one simulator event.
- [ ] Verify `/api/readings/latest` returns the posted event.
- [ ] Start a local dashboard target and inspect it in a browser.
