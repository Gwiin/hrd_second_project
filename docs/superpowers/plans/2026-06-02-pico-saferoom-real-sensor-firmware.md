# Pico SafeRoom Real Sensor Firmware Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the MicroPython real-sensor firmware path for four Pico 2W devices while keeping the host-side simulator separate.

**Architecture:** Keep MQTT as the hardware ingress boundary. Add host-testable payload helpers for firmware JSON/topic shape, add MQTT heartbeat parsing/forwarding for real device liveness, move Pico readings from virtual values to a `sensors.py` adapter layer, and preserve `apps/collector/simulator.py` as the simulator-only path.

**Tech Stack:** MicroPython on Raspberry Pi Pico 2W, `network`, `machine`, `dht`, `umqtt.simple`, Python 3.11.15, pytest, paho-mqtt, FastAPI backend internal APIs.

---

## File Structure

- Create `firmware/pico2w/payloads.py`: MicroPython-compatible pure helpers for MQTT topics and JSON payload dictionaries. This file has no `machine`, `network`, or `umqtt` imports so CPython tests can import it.
- Create `firmware/pico2w/sensors.py`: MicroPython sensor adapters for DHT-style temperature/humidity, PIR motion, analog gas, and analog light sensors.
- Modify `firmware/pico2w/main.py`: Replace `virtual_readings()` with real sensor reads from `sensors.py`, keep Wi-Fi/MQTT/publish loop responsibility here.
- Modify `firmware/pico2w/config.example.py`: Add pin map and sensor calibration constants.
- Modify `apps/collector/mqtt_parser.py`: Add parsing for `saferoom/{zone}/{device}/status` device heartbeat messages.
- Modify `apps/collector/mqtt_client.py`: Subscribe to both reading and heartbeat topics and forward heartbeats to `/internal/heartbeats/device`.
- Modify `firmware/pico2w/README.md`: Reference real-sensor files and deployment files.
- Test `tests/test_pico_firmware_payloads.py`: Host tests for firmware topic/payload helpers.
- Test `tests/test_pico_sensor_scaling.py`: Host tests for pure ADC scaling functions in `sensors.py`.
- Test `tests/test_mqtt_parser.py`: Add status heartbeat parsing tests.
- Test `tests/test_collector_mqtt_client.py`: Add tests that reading messages post to `/internal/events`, heartbeat messages post to `/internal/heartbeats/device`, and simulator code is not imported.

## Task 1: Firmware Payload Helpers

**Files:**
- Create: `firmware/pico2w/payloads.py`
- Create: `tests/test_pico_firmware_payloads.py`

- [ ] **Step 1: Write the failing payload helper tests**

Create `tests/test_pico_firmware_payloads.py`:

```python
from firmware.pico2w.payloads import (
    heartbeat_payload,
    heartbeat_topic,
    reading_payload,
    reading_topic,
)


def test_reading_topic_uses_saferoom_contract():
    topic = reading_topic("room-1", "pico-safe-001", "gas")

    assert topic == "saferoom/room-1/pico-safe-001/sensors/gas/reading"


def test_heartbeat_topic_uses_saferoom_status_contract():
    topic = heartbeat_topic("room-1", "pico-safe-001")

    assert topic == "saferoom/room-1/pico-safe-001/status"


def test_reading_payload_contains_collector_fields():
    payload = reading_payload(
        device_id="pico-safe-001",
        zone_id="room-1",
        sensor_id="gas",
        value=320,
        unit="ppm",
        timestamp="2026-06-02T10:00:00+00:00",
        seq=7,
    )

    assert payload == {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "sensor_id": "gas",
        "value": 320,
        "unit": "ppm",
        "timestamp": "2026-06-02T10:00:00+00:00",
        "seq": 7,
    }


def test_heartbeat_payload_contains_backend_fields():
    payload = heartbeat_payload(
        device_id="pico-safe-001",
        zone_id="room-1",
        timestamp="2026-06-02T10:00:00+00:00",
        uptime_ms=12345,
        seq=7,
    )

    assert payload == {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "status": "online",
        "timestamp": "2026-06-02T10:00:00+00:00",
        "uptime_ms": 12345,
        "seq": 7,
    }
```

- [ ] **Step 2: Run the payload tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_pico_firmware_payloads.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'firmware.pico2w.payloads'`.

- [ ] **Step 3: Implement the minimal payload helpers**

Create `firmware/pico2w/payloads.py`:

```python
def reading_topic(zone_id, device_id, sensor_id):
    return "saferoom/{}/{}/sensors/{}/reading".format(zone_id, device_id, sensor_id)


def heartbeat_topic(zone_id, device_id):
    return "saferoom/{}/{}/status".format(zone_id, device_id)


def reading_payload(device_id, zone_id, sensor_id, value, unit, timestamp, seq):
    return {
        "device_id": device_id,
        "zone_id": zone_id,
        "sensor_id": sensor_id,
        "value": value,
        "unit": unit,
        "timestamp": timestamp,
        "seq": seq,
    }


def heartbeat_payload(device_id, zone_id, timestamp, uptime_ms, seq):
    return {
        "device_id": device_id,
        "zone_id": zone_id,
        "status": "online",
        "timestamp": timestamp,
        "uptime_ms": uptime_ms,
        "seq": seq,
    }
```

- [ ] **Step 4: Run the payload tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_pico_firmware_payloads.py -v`

Expected: 4 passed.

- [ ] **Step 5: Pause before commit**

Do not commit automatically. If the user approves a commit, run:

```bash
git add firmware/pico2w/payloads.py tests/test_pico_firmware_payloads.py
git commit -m "feat: add Pico firmware payload helpers"
```

## Task 2: MQTT Device Heartbeat Parser

**Files:**
- Modify: `apps/collector/mqtt_parser.py`
- Modify: `tests/test_mqtt_parser.py`

- [ ] **Step 1: Write the failing heartbeat parser tests**

Append to `tests/test_mqtt_parser.py`:

```python
from apps.collector.mqtt_parser import parse_device_heartbeat_message


def test_parse_device_heartbeat_message_returns_device_heartbeat():
    payload = {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "status": "online",
        "timestamp": datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
        "uptime_ms": 12345,
        "seq": 7,
    }

    heartbeat = parse_device_heartbeat_message(
        "saferoom/room-1/pico-safe-001/status",
        json.dumps(payload).encode(),
    )

    assert heartbeat.device_id == "pico-safe-001"
    assert heartbeat.zone_id == "room-1"
    assert heartbeat.status == "online"
    assert heartbeat.uptime_ms == 12345


def test_parse_device_heartbeat_message_rejects_payload_topic_mismatch():
    payload = {
        "device_id": "pico-safe-999",
        "zone_id": "room-1",
        "status": "online",
        "timestamp": datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
        "uptime_ms": 12345,
    }

    with pytest.raises(MQTTTopicError):
        parse_device_heartbeat_message(
            "saferoom/room-1/pico-safe-001/status",
            json.dumps(payload).encode(),
        )
```

- [ ] **Step 2: Run the heartbeat parser tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_mqtt_parser.py::test_parse_device_heartbeat_message_returns_device_heartbeat tests/test_mqtt_parser.py::test_parse_device_heartbeat_message_rejects_payload_topic_mismatch -v`

Expected: FAIL with `ImportError` or `AttributeError` for `parse_device_heartbeat_message`.

- [ ] **Step 3: Implement status topic parsing**

Modify `apps/collector/mqtt_parser.py`:

```python
from shared.schemas.device_heartbeat import DeviceHeartbeat


def parse_device_heartbeat_message(topic: str, payload: bytes) -> DeviceHeartbeat:
    zone_id, device_id = _parse_status_topic(topic)
    data = json.loads(payload.decode("utf-8"))
    _assert_topic_matches_payload(data, "zone_id", zone_id)
    _assert_topic_matches_payload(data, "device_id", device_id)
    timestamp = data.get("timestamp")
    measured_at = datetime.fromisoformat(timestamp) if timestamp else datetime.now(timezone.utc)
    return DeviceHeartbeat(
        device_id=device_id,
        zone_id=zone_id,
        status=data.get("status", "online"),
        timestamp=measured_at,
        uptime_ms=int(data.get("uptime_ms", 0)),
    )


def _parse_status_topic(topic: str) -> tuple[str, str]:
    parts = topic.split("/")
    if len(parts) != 4:
        raise MQTTTopicError(f"Invalid status topic: {topic}")
    prefix, zone_id, device_id, status_segment = parts
    if prefix != "saferoom" or status_segment != "status":
        raise MQTTTopicError(f"Invalid status topic: {topic}")
    return zone_id, device_id
```

- [ ] **Step 4: Run the MQTT parser tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_mqtt_parser.py -v`

Expected: all MQTT parser tests pass.

- [ ] **Step 5: Pause before commit**

Do not commit automatically. If the user approves a commit, run:

```bash
git add apps/collector/mqtt_parser.py tests/test_mqtt_parser.py
git commit -m "feat: parse Pico MQTT device heartbeats"
```

## Task 3: MQTT Collector Heartbeat Forwarding

**Files:**
- Modify: `apps/collector/mqtt_client.py`
- Create: `tests/test_collector_mqtt_client.py`

- [ ] **Step 1: Write failing collector posting tests**

Create `tests/test_collector_mqtt_client.py`:

```python
import json
from datetime import datetime, timezone

import httpx

from apps.collector import mqtt_client


class RecordingTransport(httpx.BaseTransport):
    def __init__(self):
        self.requests = []

    def handle_request(self, request):
        self.requests.append(request)
        return httpx.Response(201, json={"accepted": True})


def test_post_event_sends_reading_to_internal_events(monkeypatch):
    transport = RecordingTransport()
    monkeypatch.setattr(httpx, "Client", lambda timeout: httpx.Client(transport=transport, timeout=timeout))
    payload = {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "sensor_id": "gas",
        "value": 320,
        "unit": "ppm",
        "timestamp": datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
    }

    mqtt_client.post_event(
        "http://127.0.0.1:8000",
        "saferoom/room-1/pico-safe-001/sensors/gas/reading",
        json.dumps(payload).encode(),
    )

    assert transport.requests[0].url.path == "/internal/events"


def test_post_device_heartbeat_sends_status_to_internal_heartbeats(monkeypatch):
    transport = RecordingTransport()
    monkeypatch.setattr(httpx, "Client", lambda timeout: httpx.Client(transport=transport, timeout=timeout))
    payload = {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "status": "online",
        "timestamp": datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
        "uptime_ms": 12345,
    }

    mqtt_client.post_device_heartbeat(
        "http://127.0.0.1:8000",
        "saferoom/room-1/pico-safe-001/status",
        json.dumps(payload).encode(),
    )

    assert transport.requests[0].url.path == "/internal/heartbeats/device"
```

- [ ] **Step 2: Run collector tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_collector_mqtt_client.py -v`

Expected: one test passes for existing `post_event`; one test fails with `AttributeError` for `post_device_heartbeat`.

- [ ] **Step 3: Implement heartbeat forwarding and topic routing**

Modify imports in `apps/collector/mqtt_client.py`:

```python
from apps.collector.mqtt_parser import (
    MQTTTopicError,
    parse_device_heartbeat_message,
    parse_reading_message,
)
```

Add the heartbeat post function:

```python
def post_device_heartbeat(backend_url: str, topic: str, payload: bytes) -> None:
    heartbeat = parse_device_heartbeat_message(topic, payload)
    with httpx.Client(timeout=5) as client:
        client.post(
            f"{backend_url}/internal/heartbeats/device",
            json=heartbeat.model_dump(mode="json"),
        ).raise_for_status()
```

Use two subscriptions in `on_connect`:

```python
client.subscribe("saferoom/+/+/sensors/+/reading")
client.subscribe("saferoom/+/+/status")
```

Route messages in `on_message`:

```python
if message.topic.endswith("/status"):
    post_device_heartbeat(backend_url, message.topic, message.payload)
else:
    post_event(backend_url, message.topic, message.payload)
```

- [ ] **Step 4: Run collector tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_collector_mqtt_client.py tests/test_mqtt_parser.py -v`

Expected: all collector and MQTT parser tests pass.

- [ ] **Step 5: Pause before commit**

Do not commit automatically. If the user approves a commit, run:

```bash
git add apps/collector/mqtt_client.py tests/test_collector_mqtt_client.py
git commit -m "feat: forward Pico MQTT heartbeats"
```

## Task 4: Sensor Scaling Helpers

**Files:**
- Create: `firmware/pico2w/sensors.py`
- Create: `tests/test_pico_sensor_scaling.py`

- [ ] **Step 1: Write failing sensor scaling tests**

Create `tests/test_pico_sensor_scaling.py`:

```python
from firmware.pico2w.sensors import adc_u16_to_lux, adc_u16_to_ppm, adc_u16_to_percent


def test_adc_u16_to_percent_scales_full_range():
    assert adc_u16_to_percent(0) == 0.0
    assert adc_u16_to_percent(65535) == 100.0


def test_adc_u16_to_ppm_scales_to_default_gas_range():
    assert adc_u16_to_ppm(0) == 0
    assert adc_u16_to_ppm(65535) == 1000


def test_adc_u16_to_lux_scales_to_default_light_range():
    assert adc_u16_to_lux(0) == 0
    assert adc_u16_to_lux(65535) == 1000
```

- [ ] **Step 2: Run sensor scaling tests and verify RED**

Run: `.venv/bin/python -m pytest tests/test_pico_sensor_scaling.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'firmware.pico2w.sensors'`.

- [ ] **Step 3: Implement pure scaling helpers and MicroPython adapters**

Create `firmware/pico2w/sensors.py` with these pure helpers at the top:

```python
def adc_u16_to_percent(raw):
    return round(max(0, min(65535, raw)) * 100 / 65535, 1)


def adc_u16_to_ppm(raw, max_ppm=1000):
    return round(max(0, min(65535, raw)) * max_ppm / 65535)


def adc_u16_to_lux(raw, max_lux=1000):
    return round(max(0, min(65535, raw)) * max_lux / 65535)
```

Add MicroPython adapter functions below the pure helpers:

```python
def read_dht_sensor(sensor):
    sensor.measure()
    return [
        ("temperature", round(sensor.temperature(), 1), "celsius"),
        ("humidity", round(sensor.humidity(), 1), "%"),
    ]


def read_motion(pin):
    return [("motion", bool(pin.value()), "bool")]


def read_gas(adc):
    return [("gas", adc_u16_to_ppm(adc.read_u16()), "ppm")]


def read_light(adc):
    return [("light", adc_u16_to_lux(adc.read_u16()), "lux")]
```

- [ ] **Step 4: Run sensor scaling tests and verify GREEN**

Run: `.venv/bin/python -m pytest tests/test_pico_sensor_scaling.py -v`

Expected: 3 passed.

- [ ] **Step 5: Pause before commit**

Do not commit automatically. If the user approves a commit, run:

```bash
git add firmware/pico2w/sensors.py tests/test_pico_sensor_scaling.py
git commit -m "feat: add Pico real sensor adapters"
```

## Task 5: Real-Sensor Firmware Main Loop

**Files:**
- Modify: `firmware/pico2w/main.py`
- Modify: `firmware/pico2w/config.example.py`
- Modify: `firmware/pico2w/README.md`

- [ ] **Step 1: Update config example**

Modify `firmware/pico2w/config.example.py`:

```python
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"

MQTT_HOST = "192.168.1.10"
MQTT_PORT = 1883

DEVICE_ID = "pico-safe-001"
ZONE_ID = "room-1"

PUBLISH_INTERVAL_SECONDS = 5

PIN_DHT = 16
PIN_MOTION = 17
PIN_GAS_ADC = 26
PIN_LIGHT_ADC = 27

ENABLE_DHT = True
ENABLE_MOTION = True
ENABLE_GAS = True
ENABLE_LIGHT = True
```

- [ ] **Step 2: Replace virtual readings with real sensor reads**

Modify `firmware/pico2w/main.py` so it imports:

```python
from payloads import heartbeat_payload, heartbeat_topic, reading_payload, reading_topic
from sensors import read_all_sensors
```

Remove `virtual_readings(seq)` from `main.py`.

Use this publish body:

```python
def publish_readings(client, seq):
    now = timestamp()
    for sensor_id, value, unit in read_all_sensors():
        payload = reading_payload(DEVICE_ID, ZONE_ID, sensor_id, value, unit, now, seq)
        client.publish(reading_topic(ZONE_ID, DEVICE_ID, sensor_id), json.dumps(payload))
```

Use this heartbeat body:

```python
def publish_heartbeat(client, seq):
    payload = heartbeat_payload(DEVICE_ID, ZONE_ID, timestamp(), time.ticks_ms(), seq)
    client.publish(heartbeat_topic(ZONE_ID, DEVICE_ID), json.dumps(payload))
```

- [ ] **Step 3: Add `read_all_sensors()` to `sensors.py`**

Add a lazy-initialized MicroPython function:

```python
def read_all_sensors():
    from config import ENABLE_DHT, ENABLE_GAS, ENABLE_LIGHT, ENABLE_MOTION
    from config import PIN_DHT, PIN_GAS_ADC, PIN_LIGHT_ADC, PIN_MOTION
    from machine import ADC, Pin

    readings = []
    if ENABLE_DHT:
        import dht

        readings.extend(read_dht_sensor(dht.DHT22(Pin(PIN_DHT))))
    if ENABLE_MOTION:
        readings.extend(read_motion(Pin(PIN_MOTION, Pin.IN)))
    if ENABLE_GAS:
        readings.extend(read_gas(ADC(PIN_GAS_ADC)))
    if ENABLE_LIGHT:
        readings.extend(read_light(ADC(PIN_LIGHT_ADC)))
    return readings
```

- [ ] **Step 4: Update firmware README**

Modify `firmware/pico2w/README.md` setup section to say the files copied to each Pico are:

```text
main.py
payloads.py
sensors.py
config.py
```

Also keep the existing reference to `README.real-sensors.md`.

- [ ] **Step 5: Run host tests for firmware-compatible helpers**

Run: `.venv/bin/python -m pytest tests/test_pico_firmware_payloads.py tests/test_pico_sensor_scaling.py -v`

Expected: all payload and scaling tests pass.

- [ ] **Step 6: Pause before commit**

Do not commit automatically. If the user approves a commit, run:

```bash
git add firmware/pico2w/main.py firmware/pico2w/config.example.py firmware/pico2w/README.md
git commit -m "feat: switch Pico firmware to real sensors"
```

## Task 6: Simulator Separation Guard

**Files:**
- Modify: `tests/test_collector_simulator.py`
- Modify: `tests/test_pico_firmware_payloads.py`

- [ ] **Step 1: Add a simulator contract test**

Append to `tests/test_collector_simulator.py`:

```python
def test_simulator_keeps_mock_protocol():
    events = generate_sensor_events(seq=1)

    assert {event.protocol for event in events} == {"mock"}
```

- [ ] **Step 2: Add a firmware helper import guard test**

Append to `tests/test_pico_firmware_payloads.py`:

```python
def test_payload_helpers_do_not_import_simulator():
    import sys

    assert "apps.collector.simulator" not in sys.modules
```

- [ ] **Step 3: Run separation tests**

Run: `.venv/bin/python -m pytest tests/test_collector_simulator.py tests/test_pico_firmware_payloads.py -v`

Expected: all simulator and payload tests pass.

- [ ] **Step 4: Pause before commit**

Do not commit automatically. If the user approves a commit, run:

```bash
git add tests/test_collector_simulator.py tests/test_pico_firmware_payloads.py
git commit -m "test: guard simulator and firmware separation"
```

## Task 7: Full Validation And Hardware Bring-Up Notes

**Files:**
- Modify: `firmware/pico2w/README.real-sensors.md`

- [ ] **Step 1: Add exact software validation commands to the wiring README**

Add this section to `firmware/pico2w/README.real-sensors.md`:

````markdown
## Software Validation Before Flashing

Run these from the repository root:

```text
.venv/bin/python -m pytest
npm --prefix frontend run build
```

The Python tests verify MQTT parsing, heartbeat forwarding, simulator separation, and host-testable firmware helper behavior. The frontend build verifies the dashboard still compiles.
````

- [ ] **Step 2: Run full backend/collector tests**

Run: `.venv/bin/python -m pytest`

Expected: all Python tests pass.

- [ ] **Step 3: Run frontend build**

Run: `npm --prefix frontend run build`

Expected: TypeScript and Vite build complete without errors.

- [ ] **Step 4: Check generated artifacts and worktree**

Run: `find data -maxdepth 2 -type f -print`

Expected: no `data/saferoom.db` produced by tests.

Run: `find logs -maxdepth 2 -type f -print`

Expected: no `logs/saferoom.log` produced by tests.

Run: `git status --short`

Expected: only intentional source, test, and documentation changes are listed.

- [ ] **Step 5: Pause before final commit**

Do not commit automatically. If the user approves a commit, run:

```bash
git add apps/collector/mqtt_client.py apps/collector/mqtt_parser.py firmware/pico2w tests docs/superpowers
git commit -m "feat: add real Pico sensor firmware path"
```

## Completion Checklist

- [ ] MicroPython remains the chosen firmware language in docs and code.
- [ ] C/C++ is not introduced.
- [ ] `apps/collector/simulator.py` remains host-side simulator code.
- [ ] Pico firmware publishes real sensor readings through `sensors.py`.
- [ ] Pico firmware publishes heartbeats to `saferoom/{zone}/{device}/status`.
- [ ] MQTT collector forwards readings to `/internal/events`.
- [ ] MQTT collector forwards heartbeats to `/internal/heartbeats/device`.
- [ ] Four-device identity mapping is documented.
- [ ] Visual wiring README exists for physical sensor connections.
- [ ] Full Python tests and frontend build pass.
