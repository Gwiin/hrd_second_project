# TESTS KNOWLEDGE

## OVERVIEW

Pytest suite covering backend APIs/persistence/auth, collector parsing/posting, desktop launcher process commands, worker heartbeat, firmware contracts, runtime deps, and static frontend contracts.

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Backend API behavior | `test_backend.py` | Uses `TestClient`, `tmp_path`, and monkeypatched OAuth clients. |
| SQLite persistence | `test_sqlite_repository.py` | Cross-instance DB and duplicate event behavior. |
| Frontend contract checks | `test_frontend_auth_gate.py` | Reads TSX/CSS/source text directly. |
| MQTT parser/client | `test_mqtt_parser.py`, `test_collector_mqtt_client.py` | Topic contracts and HTTP forwarding. |
| Firmware behavior | `test_pico_firmware_*.py`, `test_pico_sensor_scaling.py` | Fake MicroPython modules and payload contracts. |
| Launcher/worker/runtime | `test_desktop_launcher.py`, `test_worker.py`, `test_runtime_requirements.py` | No real subprocess/network dependency in tests. |

## CONVENTIONS

- Use `tmp_path` for database/log/env files.
- Use `monkeypatch` for env vars, fake HTTP clients, fake subprocesses, fake modules, and browser launch hooks.
- Prefer direct function/API assertions over broad end-to-end tests unless the surface requires it.
- Keep frontend source assertions synchronized with actual user-visible contract changes.
- Add focused regression tests near the relevant subsystem test file.

## ANTI-PATTERNS

- Do not delete or weaken failing tests to pass validation.
- Do not introduce tests that require real OAuth providers, real Pico hardware, live MQTT broker, or real browser launch unless explicitly requested.
- Do not rely on global local files; tests should isolate state.

## VALIDATION

```bash
.venv/bin/python -m pytest
```
