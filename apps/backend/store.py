from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apps.backend.devices import LEVEL1_DEVICES
from shared.schemas.sensor_event import SensorEvent


class ReadingStore:
    def __init__(self) -> None:
        self._readings: dict[str, dict[str, dict[str, Any]]] = {}
        self._logs: list[dict[str, str]] = []
        self._started_at = datetime.now(timezone.utc)
        self._last_update: datetime | None = None

    def add_event(self, event: SensorEvent) -> None:
        reading = event.model_dump(mode="json")
        device_readings = self._readings.setdefault(event.device_id, {})
        device_readings[event.sensor_id] = reading
        self._last_update = datetime.now(timezone.utc)
        self._logs.insert(
            0,
            {
                "timestamp": self._last_update.isoformat(),
                "level": "info",
                "message": f"Reading received from {event.device_id}",
            },
        )
        self._logs = self._logs[:25]

    def latest_readings(self) -> dict[str, Any]:
        return {
            "readings": self._readings,
            "updated_at": self._last_update.isoformat() if self._last_update else None,
        }

    def health(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        uptime_seconds = int((now - self._started_at).total_seconds())
        return {
            "app": "Pico SafeRoom",
            "status": "running",
            "safety_state": self._safety_state(),
            "uptime_seconds": uptime_seconds,
            "last_update": self._last_update.isoformat() if self._last_update else None,
            "processes": {
                "backend": "online",
                "collector": "simulated",
                "worker": "simulated",
            },
        }

    def devices(self) -> dict[str, Any]:
        return {"devices": LEVEL1_DEVICES}

    def logs(self) -> dict[str, Any]:
        return {"logs": self._logs}

    def _safety_state(self) -> str:
        for device_readings in self._readings.values():
            gas = device_readings.get("gas")
            temperature = device_readings.get("temperature")
            if gas and float(gas["value"]) >= 600:
                return "critical"
            if temperature and float(temperature["value"]) >= 60:
                return "critical"
            if gas and float(gas["value"]) >= 300:
                return "warning"
            if temperature and float(temperature["value"]) >= 45:
                return "warning"
        return "safe"
