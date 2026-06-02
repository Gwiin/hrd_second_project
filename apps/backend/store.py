from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps.backend.db.sqlite_repository import SQLiteRepository
from shared.schemas.device_heartbeat import DeviceHeartbeat
from shared.schemas.process_heartbeat import ProcessHeartbeat
from shared.schemas.sensor_event import SensorEvent


class ReadingStore:
    def __init__(self, db_path: Path | None = None, log_path: Path | None = None) -> None:
        self._started_at = datetime.now(timezone.utc)
        default_db_path = Path(__file__).resolve().parents[2] / "data" / "saferoom.db"
        self._log_path = log_path or Path(__file__).resolve().parents[2] / "logs" / "saferoom.log"
        self._repository = SQLiteRepository(db_path or default_db_path)

    def add_event(self, event: SensorEvent) -> None:
        self._repository.add_event(event)

    def latest_readings(self) -> dict[str, Any]:
        return self._repository.latest_readings()

    def reading_history(
        self,
        *,
        device_id: str | None = None,
        sensor_id: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        return self._repository.reading_history(device_id=device_id, sensor_id=sensor_id, limit=limit)

    def health(self) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        uptime_seconds = int((now - self._started_at).total_seconds())
        latest = self.latest_readings()
        return {
            "app": "Pico SafeRoom",
            "status": "running",
            "safety_state": self._safety_state(),
            "uptime_seconds": uptime_seconds,
            "last_update": latest["updated_at"],
            "processes": self._repository.process_statuses(),
        }

    def devices(self) -> dict[str, Any]:
        return self._repository.devices()

    def liveness(self) -> dict[str, Any]:
        return self._repository.liveness()

    def timeline(self, *, limit: int = 50) -> dict[str, Any]:
        return self._repository.timeline(limit=limit)

    def add_device_heartbeat(self, heartbeat: DeviceHeartbeat) -> None:
        self._repository.add_device_heartbeat(heartbeat)

    def add_process_heartbeat(self, heartbeat: ProcessHeartbeat) -> None:
        self._repository.add_process_heartbeat(heartbeat)

    def logs(self) -> dict[str, Any]:
        return self._repository.logs()

    def add_log(self, level: str, message: str) -> None:
        self._repository.add_log(level, message)
        self._append_file_log(level, message)

    def alerts(self) -> dict[str, Any]:
        return self._repository.alerts()

    def ack_alert(self, alert_id: int) -> dict[str, Any]:
        return self._repository.ack_alert(alert_id)

    def _append_file_log(self, level: str, message: str) -> None:
        self._log_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._log_path.open("a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamp} {level} {message}\n")

    def _safety_state(self) -> str:
        for device_readings in self.latest_readings()["readings"].values():
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
