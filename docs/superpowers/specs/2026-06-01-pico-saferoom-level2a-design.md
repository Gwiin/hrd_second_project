# Pico SafeRoom Level 2A Design

## Goal

Add SQLite persistence to the Level 1 Pico SafeRoom skeleton so sensor readings survive process restarts and can be queried as recent history.

## Approved Scope

Level 2A is the small database foundation approved after the broader Level 2 attempt was undone.

Included:

- Repository-local SQLite database file at `data/saferoom.db` by default.
- SQLite schema for `devices`, `sensors`, `sensor_readings`, and `system_logs`.
- Backend persistence for every accepted `SensorEvent`.
- Existing `/api/readings/latest` behavior backed by SQLite.
- New `/api/readings/history` endpoint with optional `device_id`, `sensor_id`, and `limit` query parameters.
- System log entries for accepted readings.
- Tests using temporary SQLite database files.

Excluded:

- Alert persistence and alert APIs.
- Device heartbeat persistence.
- Process heartbeat persistence.
- WebSocket push.
- MQTT collector and Pico 2W firmware.
- SQLAlchemy migration tooling.

## Architecture

```text
POST /internal/events
  -> ReadingStore
  -> SQLiteRepository
  -> sensor_readings + system_logs

GET /api/readings/latest
  -> SQLiteRepository.latest_readings()

GET /api/readings/history
  -> SQLiteRepository.reading_history()
```

The backend keeps the existing `ReadingStore` interface so the API layer changes minimally. `ReadingStore` delegates persistence and queries to a small SQLite repository built on Python's standard `sqlite3` module. This avoids adding a new ORM dependency before the schema stabilizes.

## Data Model

`devices` stores the four known Pico 2W device identities from Level 1.

`sensors` stores the sensor IDs observed for a device.

`sensor_readings` stores normalized `SensorEvent` payloads. `event_id` is unique so retries do not create duplicate readings.

`system_logs` stores recent backend log messages for the dashboard.

## API Behavior

`POST /internal/events` still returns `201` with `accepted` and `event_id`.

`GET /api/readings/latest` returns the same shape as Level 1:

```json
{
  "readings": {
    "pico-safe-001": {
      "temperature": {
        "device_id": "pico-safe-001",
        "sensor_id": "temperature",
        "value": 23.6
      }
    }
  },
  "updated_at": "2026-06-01T10:00:00+00:00"
}
```

`GET /api/readings/history` returns newest-first persisted readings:

```json
{
  "readings": [],
  "count": 0
}
```

## Success Criteria

- Backend tests prove a reading persists across two app/store instances using the same database file.
- Backend tests prove `/api/readings/history` returns persisted readings newest-first.
- Repository tests prove duplicate `event_id` ingestion does not duplicate rows.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
