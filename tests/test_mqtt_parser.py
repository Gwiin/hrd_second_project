import json
from datetime import datetime, timezone

import pytest

from apps.collector.mqtt_parser import MQTTTopicError, parse_device_heartbeat_message, parse_reading_message


def test_parse_reading_message_returns_sensor_event():
    payload = {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "sensor_id": "gas",
        "value": 320,
        "unit": "ppm",
        "timestamp": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc).isoformat(),
        "seq": 1024,
    }

    event = parse_reading_message(
        "saferoom/room-1/pico-safe-001/sensors/gas/reading",
        json.dumps(payload).encode(),
    )

    assert event.site_id == "safe-room-lab"
    assert event.zone_id == "room-1"
    assert event.device_id == "pico-safe-001"
    assert event.sensor_id == "gas"
    assert event.protocol == "mqtt"
    assert event.value == 320
    assert event.unit == "ppm"
    assert event.quality == "good"
    assert event.metadata["topic"] == "saferoom/room-1/pico-safe-001/sensors/gas/reading"
    assert event.metadata["seq"] == 1024


def test_parse_reading_message_rejects_invalid_topic():
    payload = {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "sensor_id": "gas",
        "value": 320,
        "unit": "ppm",
        "timestamp": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc).isoformat(),
    }

    with pytest.raises(MQTTTopicError):
        parse_reading_message("saferoom/room-1/pico-safe-001/gas", json.dumps(payload).encode())


def test_parse_reading_message_rejects_payload_topic_mismatch():
    payload = {
        "device_id": "pico-safe-999",
        "zone_id": "room-1",
        "sensor_id": "gas",
        "value": 320,
        "unit": "ppm",
        "timestamp": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc).isoformat(),
    }

    with pytest.raises(MQTTTopicError):
        parse_reading_message(
            "saferoom/room-1/pico-safe-001/sensors/gas/reading",
            json.dumps(payload).encode(),
        )


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
