from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from shared.schemas.sensor_event import SensorEvent


def test_sensor_event_accepts_valid_reading():
    event = SensorEvent(
        site_id="safe-room-lab",
        zone_id="room-1",
        device_id="pico-safe-001",
        sensor_id="gas",
        protocol="mock",
        value=320,
        unit="ppm",
        timestamp=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
        quality="good",
        metadata={"seq": 1},
    )

    assert event.event_id
    assert event.trace_id
    assert event.value == 320
    assert event.quality == "good"


def test_sensor_event_rejects_unknown_quality():
    with pytest.raises(ValidationError):
        SensorEvent(
            site_id="safe-room-lab",
            zone_id="room-1",
            device_id="pico-safe-001",
            sensor_id="gas",
            protocol="mock",
            value=320,
            unit="ppm",
            timestamp=datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc),
            quality="excellent",
            metadata={},
        )
