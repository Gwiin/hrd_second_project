# Pico SafeRoom Pico 2W Firmware

This folder contains the Level 3 MicroPython scaffold for four Raspberry Pi Pico 2W sensor nodes.

## Device IDs

- `pico-safe-001` -> `room-1`
- `pico-safe-002` -> `room-2`
- `pico-safe-003` -> `room-3`
- `pico-safe-004` -> `room-4`

## Setup

1. Copy `config.example.py` to `config.py` on the Pico.
2. Fill in Wi-Fi and MQTT broker settings in `config.py`.
3. Set `DEVICE_ID` and `ZONE_ID` for the board you are flashing.
4. Copy `main.py` and `config.py` to the Pico filesystem.
5. Reset the board.

Do not commit `config.py`; it contains local Wi-Fi details.

## MQTT Topics

Readings publish to:

```text
saferoom/{ZONE_ID}/{DEVICE_ID}/sensors/{sensor_id}/reading
```

Heartbeats publish to:

```text
saferoom/{ZONE_ID}/{DEVICE_ID}/status
```
