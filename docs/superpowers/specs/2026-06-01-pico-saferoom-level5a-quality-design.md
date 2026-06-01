# Pico SafeRoom Level 5A Quality Design

## Goal

Add backend quality hardening for invalid payloads before expanding worker heartbeat and stale-sensor rules.

## Scope

Included:

- Standard JSON error shape for invalid request payloads.
- UI-visible system log entry when `/internal/events` receives an invalid payload.
- Tests proving invalid payloads return the standard error shape.
- Tests proving invalid payloads are visible through `/api/logs`.

Excluded:

- Heartbeat timeout rules.
- Sensor stale detection.
- File logging split.
- Alert resolution.
- Retry/dead-letter queues.

## Error Shape

Invalid payload responses use:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request payload",
    "details": []
  }
}
```

## Success Criteria

- Invalid `/internal/events` payload returns HTTP 422 with `error.code == "VALIDATION_ERROR"`.
- Invalid `/internal/events` payload inserts a warning log visible from `/api/logs`.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
