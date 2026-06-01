# Pico SafeRoom

Level 1 skeleton for a smart indoor environmental safety monitoring system.

The project currently runs a local mock flow for four real Raspberry Pi Pico 2W device identities:

- `pico-safe-001`
- `pico-safe-002`
- `pico-safe-003`
- `pico-safe-004`

Level 1 uses simulated readings so the backend, collector, worker, desktop shell, and dashboard can be built and tested before MQTT and Pico firmware are connected.

## Setup

Use Python 3.11.15 through the repo-local virtual environment.

```bash
/Users/chanpark/.pyenv/versions/3.11.15/bin/python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install --prefix frontend
```

## Validate

```bash
.venv/bin/python -m pytest
npm --prefix frontend run build
```

## Run Backend And Simulator

Build the dashboard first so FastAPI can serve `frontend/dist`.

```bash
npm --prefix frontend run build
.venv/bin/python -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```bash
.venv/bin/python -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
```

Open:

```text
http://127.0.0.1:8000
```

## Run Desktop Launcher

```bash
.venv/bin/python -m apps.desktop.app
```

The launcher starts backend, collector, and worker as separate processes. It opens pywebview when a GUI session is available; otherwise use the printed local URL.

## Current Scope

Included in Level 1:

- FastAPI backend
- in-memory latest readings
- four-device Pico 2W registry
- mock collector simulator
- worker heartbeat process
- pywebview desktop launcher
- React/Vite dashboard
- Python and frontend build validation

Deferred:

- MQTT broker integration
- Pico 2W MicroPython firmware
- SQLite persistence
- WebSocket updates
- full alert rules


