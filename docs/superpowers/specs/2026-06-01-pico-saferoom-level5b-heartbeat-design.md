# Pico SafeRoom Level 5B Heartbeat Design

## Goal

Persist Pico device heartbeats and expose online/offline device status so the dashboard can show whether a real Pico 2W node is still alive.

## Scope

Included:

- `POST /internal/heartbeats/device` endpoint.
- SQLite persistence of each device's latest heartbeat in `devices.last_seen_at` and `devices.status`.
- Device status rule: `offline` when `last_seen_at` is older than 15 seconds.
- `/api/devices` returns computed `online` or `offline` status.
- Tests for heartbeat ingest and timeout-based offline status.

Excluded:

- Process heartbeat persistence.
- Sensor stale detection.
- Worker loop that periodically writes offline alerts.
- WebSocket `device.online` and `device.offline` events.

## API

```json
POST /internal/heartbeats/device
{
  "device_id": "pico-safe-001",
  "zone_id": "room-1",
  "status": "online",
  "timestamp": "2026-06-01T10:00:00+00:00",
  "uptime_ms": 123000
}
```

Response:

```json
{
  "accepted": true,
  "device_id": "pico-safe-001"
}
```

## Success Criteria

- Heartbeat API accepts a valid heartbeat and updates `/api/devices`.
- Devices with heartbeat older than 15 seconds are returned as `offline`.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
