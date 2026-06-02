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


def test_payload_helpers_do_not_import_simulator():
    import firmware.pico2w.payloads as payloads

    assert "simulator" not in payloads.__dict__


def test_timestamp_from_localtime_formats_synced_clock():
    import firmware.pico2w.payloads as payloads

    timestamp = payloads.timestamp_from_localtime((2026, 6, 2, 10, 0, 5, 0, 0))

    assert timestamp == "2026-06-02T10:00:05+00:00"


def test_timestamp_from_localtime_returns_none_for_unsynced_pico_clock():
    import firmware.pico2w.payloads as payloads

    timestamp = payloads.timestamp_from_localtime((2021, 1, 1, 0, 0, 32, 0, 0))

    assert timestamp is None
