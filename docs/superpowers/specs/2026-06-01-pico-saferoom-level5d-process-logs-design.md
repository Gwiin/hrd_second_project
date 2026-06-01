# Pico SafeRoom Level 5D Process Logs Design

## Goal

Finish the remaining Level 5 hardening by persisting process heartbeats and separating UI-facing system logs from developer file logs.

## Scope

Included:

- `POST /internal/heartbeats/process` endpoint.
- SQLite `process_heartbeats` table with latest process status.
- `/api/health` uses persisted process heartbeat status when present.
- UI logs remain in SQLite `system_logs` and `/api/logs`.
- Developer logs are appended to `logs/saferoom.log`.
- Tests for process heartbeat API and developer log file writing.

Excluded:

- Full process supervisor.
- Log rotation.
- WebSocket `process.heartbeat` event.
- External observability tools.

## API

```json
POST /internal/heartbeats/process
{
  "process": "collector",
  "status": "online",
  "timestamp": "2026-06-01T10:00:00+00:00",
  "metadata": {
    "mode": "mqtt"
  }
}
```

Response:

```json
{
  "accepted": true,
  "process": "collector"
}
```

## Success Criteria

- Process heartbeat API persists collector/backend/worker status.
- `/api/health.processes` reflects persisted process heartbeat status.
- UI logs remain queryable through `/api/logs`.
- Developer log entries are written to `logs/saferoom.log`.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
