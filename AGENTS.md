# PROJECT KNOWLEDGE BASE

**Generated:** 2026-06-05
**Commit:** 6f56a60
**Branch:** main

## OVERVIEW

Pico SafeRoom is a multi-surface IoT safety demo: Pico 2W devices publish sensor/status messages, a Python collector forwards them to FastAPI, SQLite persists state, and a Vite/React dashboard shows liveness, alerts, incident replay, and guided response.

## OPERATING RULES

- Answer in English by default unless the user asks for another language.
- Use applicable Codex skills/plugins before planning, editing, debugging, reviewing, or claiming completion.
- Read relevant files before editing; keep changes small and directly tied to the request.
- Never revert user changes unless explicitly asked.
- Ask before commits, pushes, merges, deployments, destructive commands, account changes, purchases, or outbound messages.
- Validate with the most relevant available check before claiming completion.
- Final answers for code changes must state what changed, important files, validation run, and blockers.

## STRUCTURE

```text
hrd_second_project/
├── apps/              # Python runtime processes: backend, collector, desktop launcher, worker
├── frontend/          # Vite + React + TypeScript dashboard
├── firmware/pico2w/   # MicroPython firmware and Pico wiring docs
├── shared/schemas/    # Pydantic payload contracts shared by services/tests
├── tests/             # pytest suite, including static frontend and firmware contract checks
├── docs/              # technical briefs and Superpowers specs/plans
├── data/              # local runtime SQLite / broker config, not committed when generated
└── logs/              # local runtime logs, not committed when generated
```

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Backend APIs, auth, WebSocket, static dashboard mount | `apps/backend/main.py` | `create_app()` is the app factory and route map. |
| Persistence, alerts, stale sensors, incident replay | `apps/backend/db/sqlite_repository.py` | Large central repository; preserve existing API shapes. |
| OAuth provider logic and sessions | `apps/backend/auth.py` | Env-driven Google/Kakao config. |
| Real MQTT ingestion | `apps/collector/mqtt_client.py` | Subscribes to reading/status topics and posts internal backend APIs. |
| Simulator-only readings | `apps/collector/main.py`, `apps/collector/simulator.py` | Keep separate from real Pico/MQTT path. |
| Desktop launcher | `apps/desktop/app.py` | Starts AMQTT, backend, collector, worker, dashboard. |
| Frontend app behavior | `frontend/src/App.tsx` | Main dashboard/auth/realtime surface. |
| Incident replay UI | `frontend/src/IncidentResponsePanel.tsx` | Uses replay and ack endpoints. |
| Bilingual UI copy | `frontend/src/language.ts` | Keep English/Korean keys aligned. |
| Pico firmware runtime | `firmware/pico2w/main.py` | MicroPython, not CPython app code. |
| Shared event contracts | `shared/schemas/*.py` | Pydantic models consumed across runtime/tests. |
| Regression coverage | `tests/` | Most work should add or update focused pytest coverage. |

## CODE MAP

| Symbol | Type | Location | Role |
| --- | --- | --- | --- |
| `create_app` | function | `apps/backend/main.py` | FastAPI factory, routes, static mount. |
| `ReadingStore` | class | `apps/backend/store.py` | Backend facade over persistence and auth/session helpers. |
| `SQLiteRepository` | class | `apps/backend/db/sqlite_repository.py` | Persistent readings, alerts, users, sessions, timelines. |
| `RealtimeHub` | class | `apps/backend/realtime.py` | WebSocket connection set and broadcast. |
| `parse_reading_message` | function | `apps/collector/mqtt_parser.py` | MQTT topic/payload to `SensorEvent`. |
| `run` | function | `apps/collector/mqtt_client.py` | Real MQTT collector loop. |
| `start_processes` | function | `apps/desktop/app.py` | Launcher process orchestration. |
| `App` | React component | `frontend/src/App.tsx` | Main dashboard, auth, polling, WebSocket handling. |
| `IncidentResponsePanel` | React component | `frontend/src/IncidentResponsePanel.tsx` | Replay and operator response flow. |
| `run_forever` | function | `firmware/pico2w/main.py` | Pico Wi-Fi/MQTT publish loop. |
| `SensorEvent` | Pydantic model | `shared/schemas/sensor_event.py` | Internal reading payload contract. |

## COMMANDS

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install --prefix frontend

.venv/bin/python -m pytest
npm --prefix frontend run build

.venv/bin/python -m uvicorn apps.backend.main:app --host 0.0.0.0 --port 8000
npm --prefix frontend run dev
.venv/bin/python -m apps.collector.mqtt_client --broker-host 127.0.0.1 --broker-port 1883 --backend-url http://127.0.0.1:8000
.venv/bin/python -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
.venv/bin/python -m apps.desktop.app --open browser
```

## CONVENTIONS

- Python runtime target is 3.11.
- Frontend validation is `tsc && vite build --configLoader runner`; there is no frontend test runner script.
- `frontend/vite.config.ts` proxies `/api` and `/internal` to `http://127.0.0.1:8000`.
- Tests use pytest with `tmp_path` and `monkeypatch`; frontend behavior is partly verified by source-inspection tests.
- Runtime/generated files stay out of git: `.env`, `data/`, `logs/`, `frontend/dist/`, `firmware/pico2w/config.py`.
- Keep shared schemas backward-compatible with firmware, collector, backend, and tests.

## ANTI-PATTERNS

- Do not mix simulator behavior into the real Pico/MQTT collector path.
- Do not create duplicate readings on retry; `event_id` uniqueness is part of the persistence contract.
- Do not treat social login as verified without live provider credentials and redirect URLs.
- Do not claim real four-board hardware bring-up unless it was field-tested.
- Do not store OAuth secrets or local Pico config in git.

## NOTES

- Build `frontend/dist/` before expecting the backend root route to serve the dashboard.
- If assets are rebuilding or missing, `apps/backend/main.py` intentionally returns a backend-running JSON fallback at `/`.
- Real sensor wiring must keep Pico ADC input within 0-3.3V.
- `README.md` is partly a Korean development log; `SETUP.md` is the clearer runbook for commands.
