# Pico SafeRoom Level 2B Alerts Design

## Goal

Complete the missing alert portion of the original Level 2 data-storage scope before building the realtime Level 4 dashboard.

## Scope

Included:

- SQLite `alerts` table.
- Automatic alert creation when accepted readings cross simple gas or temperature thresholds.
- `GET /api/alerts` for newest-first alert listing.
- `POST /api/alerts/{alert_id}/ack` to mark an open alert acknowledged.
- Tests for alert creation, listing, and acknowledgement.

Excluded:

- Heartbeat/offline alerting.
- Sensor stale detection.
- WebSocket `alert.created` events.
- Alert resolution rules.
- User accounts or alert ownership.

## Alert Rules

The backend creates an alert when a newly accepted `SensorEvent` matches one of these rules:

| Sensor | Warning | Critical |
| --- | --- | --- |
| `gas` | `value >= 300` | `value >= 600` |
| `temperature` | `value >= 45` | `value >= 60` |

Generated alert codes:

- `gas.warning`
- `gas.critical`
- `temperature.warning`
- `temperature.critical`

The alert status starts as `open`. The ack endpoint changes it to `acknowledged` and sets `resolved_at`.

## API Behavior

`GET /api/alerts` returns:

```json
{
  "alerts": [],
  "count": 0
}
```

`POST /api/alerts/{alert_id}/ack` returns the updated alert:

```json
{
  "alert": {
    "alert_id": 1,
    "status": "acknowledged"
  }
}
```

## Success Criteria

- Repository tests prove threshold readings create persisted alerts.
- Backend tests prove `GET /api/alerts` returns created alerts.
- Backend tests prove `POST /api/alerts/{alert_id}/ack` acknowledges an alert.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
