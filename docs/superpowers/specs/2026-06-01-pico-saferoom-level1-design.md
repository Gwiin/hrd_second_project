# Pico SafeRoom Level 1 Design

## Goal

Build the first runnable skeleton for Pico SafeRoom: a local desktop IoT safety monitoring demo with separated backend, collector, worker, and UI roles, shaped around four real Raspberry Pi Pico 2W devices.

The Python runtime is a repository-local virtual environment created from Python 3.11.15, with `.venv/` ignored for team use.

## Scope

Level 1 proves the architecture before hardware, MQTT, SQLite, and full alert processing are added. It must run from this repository without Pico 2W hardware or Mosquitto.

Included:

- FastAPI backend with health, latest readings, ingest, and static dashboard serving.
- Shared `SensorEvent` schema.
- Collector simulator that generates mock Pico SafeRoom readings for four real device identities and posts them to the backend.
- Worker process stub that reports status and keeps the multi-process boundary visible.
- pywebview desktop launcher that starts backend, collector, and worker, then opens the dashboard. If pywebview is unavailable or a GUI cannot open, it prints the local dashboard URL.
- React/Vite dashboard matching the approved operational dashboard concept at `docs/superpowers/assets/pico-saferoom-level1-concept.png`.
- Tests for schema validation, backend ingest/latest readings, and simulator event shape.

Excluded from Level 1:

- MQTT broker integration.
- Pico 2W firmware. Level 1 reserves device IDs for the four real boards but does not flash or connect them yet.
- SQLite persistence.
- WebSocket push.
- Full worker alert rules.
- Packaging or installer work.

## Architecture

```text
Collector simulator process
  -> mock events for pico-safe-001..004
  -> HTTP POST /internal/events
Backend process
  -> in-memory latest readings
  -> REST API
  -> static React dashboard
Worker process
  -> periodic heartbeat log
Desktop launcher
  -> starts backend, collector, worker
  -> opens pywebview or prints local URL
```

The process split mirrors the project docs while keeping Level 1 easy to run locally.

## Components

- `shared/schemas/sensor_event.py` owns the normalized `SensorEvent` model.
- `apps/backend/main.py` owns FastAPI routes and static dashboard mounting.
- `apps/backend/store.py` owns in-memory readings and system state.
- `apps/backend/devices.py` owns the four-device registry.
- `apps/collector/simulator.py` creates deterministic-looking mock readings for all four Pico 2W device identities.
- `apps/collector/main.py` posts generated readings to the backend.
- `apps/worker/main.py` runs a visible worker heartbeat loop.
- `apps/desktop/app.py` launches the Level 1 processes and opens the dashboard.
- `frontend/src/App.tsx` renders the dashboard.

## UI Design

The accepted dashboard concept is a light operational app, not a landing page. The first screen has:

- top status header with `Pico SafeRoom`, safety state, backend, collector, worker, uptime, and last update
- left rail for `Room 1` through `Room 4` and `pico-safe-001` through `pico-safe-004`
- latest readings for Temperature, Humidity, Light, Motion, and Gas
- simple timeline visualization
- right panel for recent alerts and system log
- footer with last event, runtime, data rate, and local time

The implementation uses code-native text and controls, CSS/SVG for simple visuals, and no generated bitmap assets in the runtime UI.

## Testing

Level 1 is complete when:

- `python3 -m pytest` passes.
- `.venv/bin/python -m pytest` passes after installing `requirements.txt`.
- `npm --prefix frontend run build` passes.
- backend API returns health and latest readings after ingest.
- the desktop launcher can start the process group or fall back to a printed local URL if GUI opening is unavailable.

## Follow-Up Levels

- Level 2: SQLite persistence and historical readings.
- Level 3: MQTT collector and Pico 2W MicroPython firmware.
- Level 4: WebSocket real-time dashboard.
- Level 5: worker alert rules, heartbeat timeout, stale sensor detection, and richer logs.
