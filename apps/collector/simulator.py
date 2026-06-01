from __future__ import annotations

import math
from datetime import datetime, timezone

from apps.backend.devices import LEVEL1_DEVICES, LEVEL1_DEVICE_IDS
from shared.schemas.sensor_event import SensorEvent

LEVEL1_SENSOR_IDS = ("temperature", "humidity", "light", "motion", "gas")


def generate_sensor_events(seq: int, now: datetime | None = None) -> list[SensorEvent]:
    measured_at = now or datetime.now(timezone.utc)
    events: list[SensorEvent] = []
    for device_index, device in enumerate(LEVEL1_DEVICES):
        phase = seq + device_index
        values = {
            "temperature": (round(23.2 + math.sin(phase / 4) * 1.4, 1), "celsius"),
            "humidity": (round(45 + math.sin(phase / 5) * 4.5, 1), "%"),
            "light": (round(320 + math.sin(phase / 3) * 180), "lux"),
            "motion": (phase % 17 == 0, "bool"),
            "gas": (round(0.32 + math.sin(phase / 6) * 0.08, 2), "ppm"),
        }
        for sensor_id, (value, unit) in values.items():
            events.append(
                SensorEvent(
                    site_id="safe-room-lab",
                    zone_id=device["zone_id"],
                    device_id=device["device_id"],
                    sensor_id=sensor_id,
                    protocol="mock",
                    value=value,
                    unit=unit,
                    timestamp=measured_at,
                    quality="good",
                    metadata={"seq": seq},
                )
            )
    return events
