# COLLECTOR KNOWLEDGE

## OVERVIEW

Collector code has two separate paths: real MQTT ingestion from Pico devices and simulator-only telemetry for development.

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Real MQTT client | `mqtt_client.py` | Subscribes to reading/status topics and posts backend internal APIs. |
| Topic and payload parsing | `mqtt_parser.py` | Converts MQTT messages to shared Pydantic schemas. |
| Simulator CLI | `main.py` | Posts generated mock events to backend. |
| Simulator data | `simulator.py` | Produces Level 1 sensor readings with `protocol="mock"`. |

## CONVENTIONS

- Real reading topic: `saferoom/+/+/sensors/+/reading`.
- Real status topic: `saferoom/+/+/status`.
- Reading messages post to `/internal/events`.
- Status messages post to `/internal/heartbeats/device`.
- Collector process heartbeat posts to `/internal/heartbeats/process` with `metadata.mode = "mqtt"`.
- Parser tests should cover topic/payload mismatch, invalid topic shape, and schema conversion.

## ANTI-PATTERNS

- Do not let simulator code become the launcher default or real demo path.
- Do not silently accept topic/payload identity mismatches.
- Do not swallow backend HTTP failures in direct posting helpers; tests expect `raise_for_status()` behavior there.

## VALIDATION

```bash
.venv/bin/python -m pytest tests/test_collector_mqtt_client.py tests/test_collector_simulator.py tests/test_mqtt_parser.py
```
