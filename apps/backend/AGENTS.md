# BACKEND KNOWLEDGE

## OVERVIEW

FastAPI backend surface for health, readings, alerts, incident replay, auth/session handling, WebSocket updates, and static dashboard serving.

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Route map and app factory | `main.py` | `create_app()` wires all public/internal endpoints. |
| Store facade | `store.py` | Thin coordinator around repository, auth, logs, and safety state. |
| SQLite persistence | `db/sqlite_repository.py` | Central large module for readings, alerts, users, sessions, timeline. |
| OAuth/session helpers | `auth.py` | Google/Kakao config, password hashing, session tokens. |
| Incident guidance payloads | `incidents.py` | Guidance and response text validation. |
| WebSocket broadcast | `realtime.py` | Connection set and JSON broadcast cleanup. |

## CONVENTIONS

- Use `create_app(db_path=..., log_path=..., frontend_dist=...)` in tests to avoid default local files.
- Keep `/api/*` for dashboard-facing endpoints and `/internal/*` for collector/worker ingestion.
- Validation errors for `/internal/events` return a standard error envelope and write a warning log.
- Session cookie name and max age come from `auth.py`; keep cookie path `/`.
- Auth routes use `credentials: include` from the frontend, so cookie behavior is user-visible.
- Static dashboard mount happens only when `frontend/dist/index.html` and `frontend/dist/assets/` exist.

## ANTI-PATTERNS

- Do not import backend `main.py` in a way that creates `data/saferoom.db`; tests assert import is side-effect-light.
- Do not duplicate persistent readings on repeated `event_id`.
- Do not broaden social OAuth scopes casually; Kakao intentionally avoids requesting account email.
- Do not collapse stale-sensor computed alerts into duplicate persistent rows.

## VALIDATION

```bash
.venv/bin/python -m pytest tests/test_backend.py tests/test_sqlite_repository.py tests/test_sensor_event.py
```
