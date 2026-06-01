# Pico SafeRoom Level 3 Pico MQTT Design

## Goal

Connect the Level 2A backend foundation to real Raspberry Pi Pico 2W devices through MQTT while keeping the existing simulator path available for local development.

## Scope

Included:

- MQTT topic contract for sensor readings and device heartbeats.
- Host-side parser that converts Pico MQTT reading payloads into the shared `SensorEvent` schema.
- MQTT collector entry point that subscribes to Pico topics and posts normalized readings to `/internal/events`.
- MicroPython firmware scaffold for Pico 2W devices using generated sensor values when physical sensors are not attached.
- Example Pico config file with placeholders only.
- Tests for MQTT topic parsing, payload normalization, and invalid topic rejection.

Excluded:

- Real Wi-Fi credentials or MQTT passwords.
- Flash automation for Pico boards.
- Device heartbeat persistence and offline detection.
- Alert generation and WebSocket dashboard push.
- Mosquitto installation or system service management.

## MQTT Contract

Reading topic:

```text
saferoom/{zone_id}/{device_id}/sensors/{sensor_id}/reading
```

Heartbeat topic:

```text
saferoom/{zone_id}/{device_id}/status
```

Reading payload:

```json
{
  "device_id": "pico-safe-001",
  "zone_id": "room-1",
  "sensor_id": "gas",
  "value": 320,
  "unit": "ppm",
  "timestamp": "2026-06-01T10:00:00+09:00",
  "seq": 1024
}
```

The collector trusts the topic as the routing contract and verifies that payload `device_id`, `zone_id`, and `sensor_id` match when present.

## Runtime Flow

```text
Pico 2W firmware
  -> publishes MQTT reading
Mosquitto broker
  -> MQTT collector subscribes
MQTT collector
  -> normalize to SensorEvent(protocol="mqtt")
  -> POST /internal/events
Backend
  -> SQLite persistence
  -> dashboard APIs
```

## Success Criteria

- Tests prove valid MQTT reading topics and payloads become `SensorEvent` objects with `protocol="mqtt"`.
- Tests prove invalid reading topics are rejected.
- Firmware scaffold contains no secrets and documents the four device IDs.
- `.venv/bin/python -m pytest` passes.
- `npm --prefix frontend run build` passes.
