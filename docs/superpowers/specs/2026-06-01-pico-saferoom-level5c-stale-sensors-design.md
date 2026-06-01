# Pico SafeRoom Level 5C Stale Sensors Design

## Goal

Detect stale sensor data from persisted readings so the system can flag sensors that have stopped reporting.

## Scope

Included:

- Stale sensor rule: latest reading timestamp older than 30 seconds.
- `GET /api/alerts` includes info-level stale sensor alerts.
- Stale alerts are computed from latest readings and do not create duplicate persistent rows.
- Tests for stale and fresh readings.

Excluded:

- Periodic worker loop.
- WebSocket `alert.created` for stale events.
- Alert resolution lifecycle.
- Per-sensor custom stale thresholds.

## Rule

| Rule | Condition | Level |
| --- | --- | --- |
| sensor stale | latest reading age > 30 seconds | `info` |

Alert code:

- `sensor.stale`

## Success Criteria

- Fresh readings do not produce stale alerts.
- Old readings produce an info-level `sensor.stale` alert from `GET /api/alerts`.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
