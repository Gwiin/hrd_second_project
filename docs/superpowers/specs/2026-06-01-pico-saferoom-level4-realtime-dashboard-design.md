# Pico SafeRoom Level 4 Realtime Dashboard Design

## Goal

Make the dashboard update immediately when new sensor readings arrive by adding a FastAPI WebSocket stream and a frontend realtime connection.

## Scope

Included:

- `WS /ws/realtime` backend endpoint.
- `reading.created` event broadcast after `/internal/events` accepts a reading.
- Frontend WebSocket client that updates latest readings from `reading.created`.
- Frontend connection status display: `live`, `reconnecting`, `offline`.
- REST polling remains as fallback.
- Tests proving an ingested reading emits a WebSocket event.

Excluded:

- `alert.created` WebSocket events.
- Device offline/degraded timing logic.
- WebSocket authentication.
- Cross-process event bus.

## Event Shape

```json
{
  "type": "reading.created",
  "reading": {
    "device_id": "pico-safe-001",
    "sensor_id": "temperature",
    "value": 23.6
  }
}
```

## Success Criteria

- Backend test connects to `/ws/realtime`, posts `/internal/events`, and receives `reading.created`.
- Frontend build passes with WebSocket client code.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
