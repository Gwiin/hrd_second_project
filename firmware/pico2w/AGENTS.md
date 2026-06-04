# PICO2W FIRMWARE KNOWLEDGE

## OVERVIEW

MicroPython firmware for Pico 2W devices that reads sensors, publishes readings/status to MQTT, and runs on real hardware.

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Runtime loop | `main.py` | Wi-Fi connect, MQTT connect, publish cycle, reconnect handling. |
| Local board config | `config.py` | Device/Wi-Fi/MQTT pins and secrets; do not commit real values. |
| MQTT topics and payloads | `payloads.py` | Must match collector parser contracts. |
| Sensor drivers/scaling | `sensors.py` | DHT, gas, light, motion helpers. |
| Wiring docs | `README.real-sensors.md` | Real sensor wiring and safety notes. |

## CONVENTIONS

- This is MicroPython, not CPython; keep dependencies board-compatible.
- Entry condition is `if __name__ in ("__main__", "main")` for Pico import behavior.
- Publish reading topics as `saferoom/{zone_id}/{device_id}/sensors/{sensor_id}/reading`.
- Publish heartbeat topics as `saferoom/{zone_id}/{device_id}/status`.
- Tests fake MicroPython modules through `sys.modules`; preserve import-time side-effect boundaries.

## ANTI-PATTERNS

- Do not commit real Wi-Fi credentials or local broker secrets in `config.py`.
- Do not exceed Pico ADC input limits; real sensor wiring must stay within 0-3.3V.
- Do not import simulator code from firmware payload helpers.
- Do not start the infinite loop on normal CPython import; tests assert this.

## VALIDATION

```bash
.venv/bin/python -m pytest tests/test_pico_firmware_main.py tests/test_pico_firmware_payloads.py tests/test_pico_firmware_sensors.py tests/test_pico_sensor_scaling.py
```
