from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps.backend.devices import LEVEL1_DEVICES
from shared.schemas.device_heartbeat import DeviceHeartbeat
from shared.schemas.process_heartbeat import ProcessHeartbeat
from shared.schemas.sensor_event import SensorEvent

DEVICE_OFFLINE_AFTER_SECONDS = 15
SENSOR_STALE_AFTER_SECONDS = 30


class SQLiteRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def add_event(self, event: SensorEvent) -> None:
        received_at = datetime.now(timezone.utc).isoformat()
        reading = event.model_dump(mode="json")
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR IGNORE INTO sensors (device_id, sensor_id, sensor_name, unit)
                VALUES (?, ?, ?, ?)
                """,
                (event.device_id, event.sensor_id, event.sensor_id, event.unit),
            )
            cursor = conn.execute(
                """
                INSERT OR IGNORE INTO sensor_readings (
                    event_id, site_id, zone_id, device_id, sensor_id, protocol, value,
                    unit, quality, measured_at, received_at, payload_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.event_id,
                    event.site_id,
                    event.zone_id,
                    event.device_id,
                    event.sensor_id,
                    event.protocol,
                    event.value,
                    event.unit,
                    event.quality,
                    event.timestamp.isoformat(),
                    received_at,
                    json.dumps(reading, sort_keys=True),
                ),
            )
            if cursor.rowcount:
                conn.execute(
                    """
                    INSERT INTO system_logs (timestamp, level, message)
                    VALUES (?, ?, ?)
                    """,
                    (received_at, "info", f"Reading received from {event.device_id}"),
                )
                alert = _alert_for_event(event, received_at)
                if alert:
                    conn.execute(
                        """
                        INSERT INTO alerts (
                            level, code, message, zone_id, device_id, sensor_id,
                            value, status, created_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            alert["level"],
                            alert["code"],
                            alert["message"],
                            event.zone_id,
                            event.device_id,
                            event.sensor_id,
                            event.value,
                            "open",
                            received_at,
                        ),
                    )

    def latest_readings(self) -> dict[str, Any]:
        query = """
            SELECT sr.payload_json, sr.received_at
            FROM sensor_readings sr
            JOIN (
                SELECT device_id, sensor_id, MAX(reading_id) AS reading_id
                FROM sensor_readings
                GROUP BY device_id, sensor_id
            ) latest ON latest.reading_id = sr.reading_id
            ORDER BY sr.device_id, sr.sensor_id
        """
        readings: dict[str, dict[str, dict[str, Any]]] = {}
        updated_at: str | None = None
        with self._connect() as conn:
            for row in conn.execute(query):
                reading = json.loads(row["payload_json"])
                readings.setdefault(reading["device_id"], {})[reading["sensor_id"]] = reading
                if updated_at is None or row["received_at"] > updated_at:
                    updated_at = row["received_at"]
        return {"readings": readings, "updated_at": updated_at}

    def reading_history(
        self,
        *,
        device_id: str | None = None,
        sensor_id: str | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        clauses: list[str] = []
        params: list[Any] = []
        if device_id:
            clauses.append("device_id = ?")
            params.append(device_id)
        if sensor_id:
            clauses.append("sensor_id = ?")
            params.append(sensor_id)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        params.append(max(1, min(limit, 500)))
        query = f"""
            SELECT payload_json
            FROM sensor_readings
            {where}
            ORDER BY reading_id DESC
            LIMIT ?
        """
        with self._connect() as conn:
            readings = [json.loads(row["payload_json"]) for row in conn.execute(query, params)]
        return {"readings": readings, "count": len(readings)}

    def devices(self) -> dict[str, Any]:
        with self._connect() as conn:
            devices = [dict(row) for row in conn.execute("SELECT * FROM devices ORDER BY device_id")]
        for device in devices:
            device["status"] = _computed_device_status(device["last_seen_at"])
        return {"devices": devices}

    def add_device_heartbeat(self, heartbeat: DeviceHeartbeat) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE devices
                SET zone_id = ?, status = ?, last_seen_at = ?
                WHERE device_id = ?
                """,
                (
                    heartbeat.zone_id,
                    heartbeat.status,
                    heartbeat.timestamp.isoformat(),
                    heartbeat.device_id,
                ),
            )
            conn.execute(
                """
                INSERT INTO system_logs (timestamp, level, message)
                VALUES (?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    "info",
                    f"Heartbeat received from {heartbeat.device_id}",
                ),
            )

    def add_process_heartbeat(self, heartbeat: ProcessHeartbeat) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO process_heartbeats (process, status, last_seen_at, metadata_json)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(process) DO UPDATE SET
                    status = excluded.status,
                    last_seen_at = excluded.last_seen_at,
                    metadata_json = excluded.metadata_json
                """,
                (
                    heartbeat.process,
                    heartbeat.status,
                    heartbeat.timestamp.isoformat(),
                    json.dumps(heartbeat.metadata, sort_keys=True),
                ),
            )

    def process_statuses(self) -> dict[str, str]:
        statuses = {"backend": "online", "collector": "simulated", "worker": "simulated"}
        with self._connect() as conn:
            for row in conn.execute("SELECT process, status FROM process_heartbeats"):
                statuses[row["process"]] = row["status"]
        return statuses

    def logs(self) -> dict[str, Any]:
        with self._connect() as conn:
            logs = [
                dict(row)
                for row in conn.execute(
                    "SELECT timestamp, level, message FROM system_logs ORDER BY log_id DESC LIMIT 25"
                )
            ]
        return {"logs": logs}

    def add_log(self, level: str, message: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO system_logs (timestamp, level, message)
                VALUES (?, ?, ?)
                """,
                (timestamp, level, message),
            )

    def alerts(self) -> dict[str, Any]:
        with self._connect() as conn:
            alerts = [
                dict(row)
                for row in conn.execute(
                    """
                    SELECT alert_id, level, code, message, zone_id, device_id,
                           sensor_id, value, status, created_at, resolved_at
                    FROM alerts
                    ORDER BY alert_id DESC
                    LIMIT 100
                    """
                )
            ]
            alerts.extend(_stale_sensor_alerts(conn))
        return {"alerts": alerts, "count": len(alerts)}

    def ack_alert(self, alert_id: int) -> dict[str, Any]:
        resolved_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                UPDATE alerts
                SET status = 'acknowledged', resolved_at = ?
                WHERE alert_id = ?
                """,
                (resolved_at, alert_id),
            )
            row = conn.execute(
                """
                SELECT alert_id, level, code, message, zone_id, device_id,
                       sensor_id, value, status, created_at, resolved_at
                FROM alerts
                WHERE alert_id = ?
                """,
                (alert_id,),
            ).fetchone()
        if row is None:
            raise KeyError(alert_id)
        return {"alert": dict(row)}

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS devices (
                    device_id TEXT PRIMARY KEY,
                    zone_id TEXT NOT NULL,
                    device_name TEXT NOT NULL,
                    model TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'online',
                    protocol TEXT NOT NULL DEFAULT 'mqtt',
                    enabled INTEGER NOT NULL DEFAULT 1,
                    last_seen_at TEXT
                );

                CREATE TABLE IF NOT EXISTS sensors (
                    device_id TEXT NOT NULL,
                    sensor_id TEXT NOT NULL,
                    sensor_name TEXT NOT NULL,
                    unit TEXT,
                    PRIMARY KEY (device_id, sensor_id)
                );

                CREATE TABLE IF NOT EXISTS sensor_readings (
                    reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    site_id TEXT NOT NULL,
                    zone_id TEXT NOT NULL,
                    device_id TEXT NOT NULL,
                    sensor_id TEXT NOT NULL,
                    protocol TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    quality TEXT NOT NULL,
                    measured_at TEXT NOT NULL,
                    received_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS system_logs (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS alerts (
                    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT NOT NULL,
                    code TEXT NOT NULL,
                    message TEXT NOT NULL,
                    zone_id TEXT,
                    device_id TEXT,
                    sensor_id TEXT,
                    value REAL,
                    status TEXT NOT NULL DEFAULT 'open',
                    created_at TEXT NOT NULL,
                    resolved_at TEXT
                );

                CREATE TABLE IF NOT EXISTS process_heartbeats (
                    process TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );
                """
            )
            conn.executemany(
                """
                INSERT OR IGNORE INTO devices (
                    device_id, zone_id, device_name, model, status, protocol, enabled
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        device["device_id"],
                        device["zone_id"],
                        device["device_name"],
                        device["model"],
                        device["status"],
                        "mqtt",
                        1,
                    )
                    for device in LEVEL1_DEVICES
                ],
            )


def _alert_for_event(event: SensorEvent, created_at: str) -> dict[str, str] | None:
    if event.sensor_id == "gas":
        value = float(event.value)
        if value >= 600:
            return {
                "level": "critical",
                "code": "gas.critical",
                "message": f"Critical gas reading from {event.device_id}: {value} {event.unit}",
            }
        if value >= 300:
            return {
                "level": "warning",
                "code": "gas.warning",
                "message": f"Gas warning from {event.device_id}: {value} {event.unit}",
            }
    if event.sensor_id == "temperature":
        value = float(event.value)
        if value >= 60:
            return {
                "level": "critical",
                "code": "temperature.critical",
                "message": f"Critical temperature from {event.device_id}: {value} {event.unit}",
            }
        if value >= 45:
            return {
                "level": "warning",
                "code": "temperature.warning",
                "message": f"Temperature warning from {event.device_id}: {value} {event.unit}",
            }
    return None


def _computed_device_status(last_seen_at: str | None) -> str:
    if not last_seen_at:
        return "online"
    last_seen = datetime.fromisoformat(last_seen_at)
    if last_seen.tzinfo is None:
        last_seen = last_seen.replace(tzinfo=timezone.utc)
    age_seconds = (datetime.now(timezone.utc) - last_seen).total_seconds()
    return "offline" if age_seconds > DEVICE_OFFLINE_AFTER_SECONDS else "online"


def _stale_sensor_alerts(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    query = """
        SELECT sr.zone_id, sr.device_id, sr.sensor_id, sr.value, sr.measured_at
        FROM sensor_readings sr
        JOIN (
            SELECT device_id, sensor_id, MAX(reading_id) AS reading_id
            FROM sensor_readings
            GROUP BY device_id, sensor_id
        ) latest ON latest.reading_id = sr.reading_id
        ORDER BY sr.device_id, sr.sensor_id
    """
    alerts: list[dict[str, Any]] = []
    now = datetime.now(timezone.utc)
    for row in conn.execute(query):
        measured_at = datetime.fromisoformat(row["measured_at"])
        if measured_at.tzinfo is None:
            measured_at = measured_at.replace(tzinfo=timezone.utc)
        age_seconds = (now - measured_at).total_seconds()
        if age_seconds <= SENSOR_STALE_AFTER_SECONDS:
            continue
        alerts.append(
            {
                "alert_id": None,
                "level": "info",
                "code": "sensor.stale",
                "message": f"Stale {row['sensor_id']} reading from {row['device_id']}",
                "zone_id": row["zone_id"],
                "device_id": row["device_id"],
                "sensor_id": row["sensor_id"],
                "value": row["value"],
                "status": "open",
                "created_at": measured_at.isoformat(),
                "resolved_at": None,
            }
        )
    return alerts
