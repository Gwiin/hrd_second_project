from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps.backend.incidents import clean_response_text, guidance_for_code
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
        statuses = {"backend": "online", "collector": "offline", "worker": "offline"}
        with self._connect() as conn:
            for row in conn.execute("SELECT process, status FROM process_heartbeats"):
                statuses[row["process"]] = row["status"]
        return statuses

    def liveness(self) -> dict[str, Any]:
        devices = self.devices()["devices"]
        for device in devices:
            device["kind"] = "device"

        processes = {
            "backend": {"kind": "process", "process": "backend", "status": "online", "last_seen_at": None, "metadata": {}},
            "collector": {
                "kind": "process",
                "process": "collector",
                "status": "offline",
                "last_seen_at": None,
                "metadata": {},
            },
            "worker": {"kind": "process", "process": "worker", "status": "offline", "last_seen_at": None, "metadata": {}},
        }
        with self._connect() as conn:
            for row in conn.execute("SELECT process, status, last_seen_at, metadata_json FROM process_heartbeats"):
                processes[row["process"]] = {
                    "kind": "process",
                    "process": row["process"],
                    "status": row["status"],
                    "last_seen_at": row["last_seen_at"],
                    "metadata": json.loads(row["metadata_json"]),
                }
        return {"devices": devices, "processes": list(processes.values())}

    def timeline(self, *, limit: int = 50) -> dict[str, Any]:
        limit = max(1, min(limit, 100))
        events: list[dict[str, Any]] = []
        with self._connect() as conn:
            events.extend(_reading_timeline_events(conn, limit))
            events.extend(_alert_timeline_events(conn, limit))
            events.extend(_log_timeline_events(conn, limit))
            events.extend(_device_heartbeat_timeline_events(conn))
            events.extend(_process_heartbeat_timeline_events(conn))
        events.sort(key=lambda event: event["timestamp"], reverse=True)
        events = events[:limit]
        return {"events": events, "count": len(events)}

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

    def ack_alert(
        self,
        alert_id: int,
        *,
        checklist: list[str] | None = None,
        note: str = "",
        evidence: str = "",
    ) -> dict[str, Any]:
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
            if row is not None and (checklist is not None or note or evidence):
                conn.execute(
                    """
                    INSERT INTO incident_responses (
                        alert_id, checklist_json, note, evidence, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(alert_id) DO UPDATE SET
                        checklist_json = excluded.checklist_json,
                        note = excluded.note,
                        evidence = excluded.evidence,
                        updated_at = excluded.updated_at
                    """,
                    (
                        alert_id,
                        json.dumps(checklist or [], sort_keys=True),
                        clean_response_text(note),
                        clean_response_text(evidence),
                        resolved_at,
                        resolved_at,
                    ),
                )
        if row is None:
            raise KeyError(alert_id)
        response = self._incident_response(alert_id)
        result: dict[str, Any] = {"alert": dict(row)}
        if response is not None:
            result["response"] = response
        return result

    def alert_replay(self, alert_id: int) -> dict[str, Any]:
        with self._connect() as conn:
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
            alert = dict(row)
            events = []
            events.extend(_reading_timeline_events(conn, 25))
            events.extend(_alert_timeline_events(conn, 25))
            events.extend(_log_timeline_events(conn, 25))
            events.extend(_device_heartbeat_timeline_events(conn))
            events.extend(_process_heartbeat_timeline_events(conn))
        events.sort(key=lambda event: event["timestamp"], reverse=True)
        return {
            "alert": alert,
            "guidance": guidance_for_code(alert["code"]),
            "response": self._incident_response(alert_id),
            "related_events": events[:25],
        }

    def get_user_by_email(self, email: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT user_id, email, display_name, password_hash, primary_provider, created_at
                FROM users
                WHERE email = ?
                """,
                (email,),
            ).fetchone()
        return dict(row) if row else None

    def create_email_user(self, email: str, display_name: str, password_hash: str) -> dict[str, Any]:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users (email, display_name, password_hash, primary_provider, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (email, display_name, password_hash, "email", created_at),
            )
            user_id = cursor.lastrowid
            row = conn.execute(
                """
                SELECT user_id, email, display_name, password_hash, primary_provider, created_at
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        return dict(row)

    def create_auth_session(self, user_id: int, session_token: str, expires_at: str) -> None:
        created_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO auth_sessions (session_token, user_id, created_at, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (session_token, user_id, created_at, expires_at),
            )

    def get_user_by_session(self, session_token: str) -> dict[str, Any] | None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT u.user_id, u.email, u.display_name, u.password_hash, u.primary_provider, u.created_at
                FROM auth_sessions s
                JOIN users u ON u.user_id = s.user_id
                WHERE s.session_token = ? AND s.expires_at > ?
                """,
                (session_token, now),
            ).fetchone()
        return dict(row) if row else None

    def delete_auth_session(self, session_token: str) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM auth_sessions WHERE session_token = ?", (session_token,))

    def _incident_response(self, alert_id: int) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT checklist_json, note, evidence
                FROM incident_responses
                WHERE alert_id = ?
                """,
                (alert_id,),
            ).fetchone()
        if row is None:
            return None
        return {
            "checklist": json.loads(row["checklist_json"]),
            "note": row["note"],
            "evidence": row["evidence"],
        }

    def get_or_create_social_user(
        self,
        *,
        provider: str,
        provider_subject: str,
        email: str,
        display_name: str,
    ) -> dict[str, Any]:
        linked_at = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT u.user_id, u.email, u.display_name, u.password_hash, u.primary_provider, u.created_at
                FROM auth_accounts a
                JOIN users u ON u.user_id = a.user_id
                WHERE a.provider = ? AND a.provider_subject = ?
                """,
                (provider, provider_subject),
            ).fetchone()
            if row:
                return dict(row)

            user_row = conn.execute(
                """
                SELECT user_id, email, display_name, password_hash, primary_provider, created_at
                FROM users
                WHERE email = ?
                """,
                (email,),
            ).fetchone()
            if user_row:
                user_id = user_row["user_id"]
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO users (email, display_name, password_hash, primary_provider, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (email, display_name, None, provider, linked_at),
                )
                user_id = cursor.lastrowid

            conn.execute(
                """
                INSERT OR IGNORE INTO auth_accounts (provider, provider_subject, user_id, email, linked_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (provider, provider_subject, user_id, email, linked_at),
            )
            linked_user = conn.execute(
                """
                SELECT user_id, email, display_name, password_hash, primary_provider, created_at
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()
        return dict(linked_user)

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

                CREATE TABLE IF NOT EXISTS incident_responses (
                    alert_id INTEGER PRIMARY KEY,
                    checklist_json TEXT NOT NULL,
                    note TEXT NOT NULL,
                    evidence TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (alert_id) REFERENCES alerts(alert_id)
                );

                CREATE TABLE IF NOT EXISTS process_heartbeats (
                    process TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    metadata_json TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL UNIQUE,
                    display_name TEXT NOT NULL,
                    password_hash TEXT,
                    primary_provider TEXT NOT NULL DEFAULT 'email',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS auth_accounts (
                    provider TEXT NOT NULL,
                    provider_subject TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    email TEXT,
                    linked_at TEXT NOT NULL,
                    PRIMARY KEY (provider, provider_subject),
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                );

                CREATE TABLE IF NOT EXISTS auth_sessions (
                    session_token TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
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
        return "offline"
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


def _reading_timeline_events(conn: sqlite3.Connection, limit: int) -> list[dict[str, Any]]:
    query = """
        SELECT reading_id, device_id, zone_id, sensor_id, value, unit, quality,
               measured_at, received_at, payload_json
        FROM sensor_readings
        ORDER BY reading_id DESC
        LIMIT ?
    """
    events = []
    for row in conn.execute(query, (limit,)):
        reading = json.loads(row["payload_json"])
        events.append(
            {
                "id": f"reading-{row['reading_id']}",
                "type": "reading",
                "timestamp": row["received_at"],
                "title": f"{row['sensor_id']} reading",
                "message": f"{row['device_id']} {row['sensor_id']}: {row['value']} {row['unit']}",
                "tone": _quality_tone(row["quality"]),
                "zone_id": row["zone_id"],
                "device_id": row["device_id"],
                "sensor_id": row["sensor_id"],
                "value": reading["value"],
                "unit": row["unit"],
                "quality": row["quality"],
                "measured_at": row["measured_at"],
            }
        )
    return events


def _alert_timeline_events(conn: sqlite3.Connection, limit: int) -> list[dict[str, Any]]:
    query = """
        SELECT alert_id, level, code, message, zone_id, device_id, sensor_id,
               value, status, created_at, resolved_at
        FROM alerts
        ORDER BY alert_id DESC
        LIMIT ?
    """
    events = []
    for row in conn.execute(query, (limit,)):
        events.append(
            {
                "id": f"alert-{row['alert_id']}",
                "type": "alert",
                "timestamp": row["created_at"],
                "title": row["code"],
                "message": row["message"],
                "tone": row["level"],
                "zone_id": row["zone_id"],
                "device_id": row["device_id"],
                "sensor_id": row["sensor_id"],
                "value": row["value"],
                "status": row["status"],
                "resolved_at": row["resolved_at"],
            }
        )
    return events


def _log_timeline_events(conn: sqlite3.Connection, limit: int) -> list[dict[str, Any]]:
    query = """
        SELECT log_id, timestamp, level, message
        FROM system_logs
        ORDER BY log_id DESC
        LIMIT ?
    """
    return [
        {
            "id": f"log-{row['log_id']}",
            "type": "log",
            "timestamp": row["timestamp"],
            "title": row["level"],
            "message": row["message"],
            "tone": _log_tone(row["level"]),
        }
        for row in conn.execute(query, (limit,))
    ]


def _device_heartbeat_timeline_events(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    query = """
        SELECT device_id, zone_id, status, last_seen_at
        FROM devices
        WHERE last_seen_at IS NOT NULL
        ORDER BY last_seen_at DESC
    """
    return [
        {
            "id": f"device-heartbeat-{row['device_id']}",
            "type": "device_heartbeat",
            "timestamp": row["last_seen_at"],
            "title": "device heartbeat",
            "message": f"{row['device_id']} reported {row['status']}",
            "tone": "safe" if _computed_device_status(row["last_seen_at"]) == "online" else "critical",
            "zone_id": row["zone_id"],
            "device_id": row["device_id"],
            "status": _computed_device_status(row["last_seen_at"]),
        }
        for row in conn.execute(query)
    ]


def _process_heartbeat_timeline_events(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    query = """
        SELECT process, status, last_seen_at, metadata_json
        FROM process_heartbeats
        ORDER BY last_seen_at DESC
    """
    return [
        {
            "id": f"process-heartbeat-{row['process']}",
            "type": "process_heartbeat",
            "timestamp": row["last_seen_at"],
            "title": "process heartbeat",
            "message": f"{row['process']} reported {row['status']}",
            "tone": _process_tone(row["status"]),
            "process": row["process"],
            "status": row["status"],
            "metadata": json.loads(row["metadata_json"]),
        }
        for row in conn.execute(query)
    ]


def _quality_tone(quality: str) -> str:
    if quality in {"bad", "missing"}:
        return "critical"
    if quality in {"uncertain", "stale"}:
        return "warning"
    return "safe"


def _log_tone(level: str) -> str:
    if level in {"error", "critical"}:
        return "critical"
    if level == "warning":
        return "warning"
    return "safe"


def _process_tone(status: str) -> str:
    if status == "offline":
        return "critical"
    if status in {"degraded", "simulated"}:
        return "warning"
    return "safe"
