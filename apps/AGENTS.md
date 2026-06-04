# APPS KNOWLEDGE

## OVERVIEW

`apps/` contains Python runtime processes that cooperate through HTTP, MQTT, subprocess orchestration, and shared Pydantic schemas.

## STRUCTURE

```text
apps/
├── backend/    # FastAPI, SQLite, auth, alerts, realtime
├── collector/  # real MQTT collector plus simulator-only path
├── desktop/    # launcher that starts broker/backend/collector/worker/dashboard
└── worker/     # process heartbeat poster
```

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Backend routes and app startup | `backend/main.py` | Uses `create_app()` and `uvicorn.run()` guard. |
| Real MQTT ingestion | `collector/mqtt_client.py` | Posts to `/internal/events` and `/internal/heartbeats/device`. |
| Simulator telemetry | `collector/main.py`, `collector/simulator.py` | Development-only mock protocol. |
| Process orchestration | `desktop/app.py` | Starts AMQTT, backend, collector, worker. |
| Worker liveness | `worker/main.py` | Posts `/internal/heartbeats/process`. |

## CONVENTIONS

- Use `.venv/bin/python -m ...` module execution for app entry points.
- Keep `backend_url` configurable in collector/worker/launcher call sites.
- Use shared schemas from `shared/schemas` for payload contracts.
- Prefer narrow unit tests with `monkeypatch` over real network or subprocess work.

## ANTI-PATTERNS

- Do not make the desktop launcher start the simulator by default; it is real Pico + MQTT collector mode.
- Do not add real network or process side effects to tests when a monkeypatched client/process is enough.
- Do not hardcode secrets or provider credentials in app modules.
