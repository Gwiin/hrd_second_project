from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from shared.schemas.sensor_event import SensorEvent


class MQTTTopicError(ValueError):
    pass


def parse_reading_message(topic: str, payload: bytes) -> SensorEvent:
    zone_id, device_id, sensor_id = _parse_reading_topic(topic)
    data = json.loads(payload.decode("utf-8"))
    _assert_topic_matches_payload(data, "zone_id", zone_id)
    _assert_topic_matches_payload(data, "device_id", device_id)
    _assert_topic_matches_payload(data, "sensor_id", sensor_id)
    timestamp = data.get("timestamp")
    measured_at = datetime.fromisoformat(timestamp) if timestamp else datetime.now(timezone.utc)
    metadata = {"topic": topic}
    if "seq" in data:
        metadata["seq"] = data["seq"]
    return SensorEvent(
        site_id="safe-room-lab",
        zone_id=zone_id,
        device_id=device_id,
        sensor_id=sensor_id,
        protocol="mqtt",
        value=data["value"],
        unit=data["unit"],
        timestamp=measured_at,
        quality="good",
        metadata=metadata,
    )


def _parse_reading_topic(topic: str) -> tuple[str, str, str]:
    parts = topic.split("/")
    if len(parts) != 6:
        raise MQTTTopicError(f"Invalid reading topic: {topic}")
    prefix, zone_id, device_id, sensors_segment, sensor_id, reading_segment = parts
    if prefix != "saferoom" or sensors_segment != "sensors" or reading_segment != "reading":
        raise MQTTTopicError(f"Invalid reading topic: {topic}")
    return zone_id, device_id, sensor_id


def _assert_topic_matches_payload(data: dict[str, Any], key: str, expected: str) -> None:
    if key in data and data[key] != expected:
        raise MQTTTopicError(f"Payload {key} does not match topic")
