import importlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

import apps.backend.main as backend_main
from apps.backend.main import create_app


def make_app(tmp_path, *, log_path=None):
    return create_app(
        db_path=tmp_path / "saferoom.db",
        log_path=log_path or tmp_path / "logs" / "saferoom.log",
    )


def make_payload(
    *,
    event_id: str = "test-event-1",
    sensor_id: str = "temperature",
    value: float = 23.6,
) -> dict:
    return {
        "event_id": event_id,
        "site_id": "safe-room-lab",
        "zone_id": "room-1",
        "device_id": "pico-safe-001",
        "sensor_id": sensor_id,
        "protocol": "mock",
        "value": value,
        "unit": "celsius",
        "timestamp": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc).isoformat(),
        "quality": "good",
        "metadata": {"seq": 7},
    }


def make_heartbeat(*, timestamp: datetime | None = None) -> dict:
    return {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "status": "online",
        "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
        "uptime_ms": 123000,
    }


def make_process_heartbeat(*, process: str = "collector", status: str = "online") -> dict:
    return {
        "process": process,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"mode": "mqtt"},
    }


def test_health_reports_level1_processes(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "Pico SafeRoom"
    assert body["status"] == "running"
    assert body["processes"]["backend"] == "online"
    assert body["processes"]["collector"] == "simulated"
    assert body["processes"]["worker"] == "simulated"


def test_devices_api_returns_four_pico_2w_devices(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/devices")

    assert response.status_code == 200
    devices = response.json()["devices"]
    assert [device["device_id"] for device in devices] == [
        "pico-safe-001",
        "pico-safe-002",
        "pico-safe-003",
        "pico-safe-004",
    ]
    assert {device["model"] for device in devices} == {"Raspberry Pi Pico 2W"}
    assert {device["status"] for device in devices} == {"online"}


def test_ingest_event_updates_latest_readings(tmp_path):
    client = TestClient(make_app(tmp_path))
    payload = make_payload()

    ingest_response = client.post("/internal/events", json=payload)
    latest_response = client.get("/api/readings/latest")

    assert ingest_response.status_code == 201
    assert latest_response.status_code == 200
    readings = latest_response.json()["readings"]
    assert readings["pico-safe-001"]["temperature"]["value"] == 23.6
    assert readings["pico-safe-001"]["temperature"]["device_id"] == "pico-safe-001"


def test_ingested_reading_persists_across_app_instances(tmp_path):
    db_path = tmp_path / "saferoom.db"
    first_client = TestClient(create_app(db_path=db_path))
    payload = make_payload(event_id="persisted-event")

    ingest_response = first_client.post("/internal/events", json=payload)
    second_client = TestClient(create_app(db_path=db_path))
    latest_response = second_client.get("/api/readings/latest")

    assert ingest_response.status_code == 201
    assert latest_response.status_code == 200
    readings = latest_response.json()["readings"]
    assert readings["pico-safe-001"]["temperature"]["value"] == 23.6


def test_history_api_returns_persisted_readings(tmp_path):
    client = TestClient(create_app(db_path=tmp_path / "saferoom.db"))
    client.post("/internal/events", json=make_payload(event_id="event-1", value=21.0))
    client.post("/internal/events", json=make_payload(event_id="event-2", value=22.0))

    response = client.get("/api/readings/history?device_id=pico-safe-001&sensor_id=temperature&limit=1")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["readings"][0]["event_id"] == "event-2"
    assert body["readings"][0]["value"] == 22.0


def test_importing_backend_main_does_not_create_default_database():
    default_db_path = Path(__file__).resolve().parents[1] / "data" / "saferoom.db"
    default_db_path.unlink(missing_ok=True)

    importlib.reload(backend_main)

    assert not default_db_path.exists()


def test_alerts_api_returns_threshold_alerts(tmp_path):
    client = TestClient(make_app(tmp_path))

    client.post("/internal/events", json=make_payload(event_id="gas-alert", sensor_id="gas", value=601))
    response = client.get("/api/alerts")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["alerts"][0]["level"] == "critical"
    assert body["alerts"][0]["code"] == "gas.critical"
    assert body["alerts"][0]["status"] == "open"


def test_ack_alert_api_updates_alert_status(tmp_path):
    client = TestClient(make_app(tmp_path))
    client.post(
        "/internal/events",
        json=make_payload(event_id="temperature-alert", sensor_id="temperature", value=61),
    )
    alert_id = client.get("/api/alerts").json()["alerts"][0]["alert_id"]

    response = client.post(f"/api/alerts/{alert_id}/ack")

    assert response.status_code == 200
    alert = response.json()["alert"]
    assert alert["alert_id"] == alert_id
    assert alert["status"] == "acknowledged"


def test_realtime_websocket_receives_reading_created(tmp_path):
    client = TestClient(make_app(tmp_path))

    with client.websocket_connect("/ws/realtime") as websocket:
        ingest_response = client.post(
            "/internal/events",
            json=make_payload(event_id="realtime-event", sensor_id="temperature", value=24.5),
        )
        message = websocket.receive_json()

    assert ingest_response.status_code == 201
    assert message["type"] == "reading.created"
    assert message["reading"]["event_id"] == "realtime-event"
    assert message["reading"]["device_id"] == "pico-safe-001"
    assert message["reading"]["sensor_id"] == "temperature"
    assert message["reading"]["value"] == 24.5


def test_invalid_event_payload_returns_standard_error(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.post("/internal/events", json={"device_id": "pico-safe-001"})

    assert response.status_code == 422
    body = response.json()
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Invalid request payload"
    assert isinstance(body["error"]["details"], list)


def test_invalid_event_payload_is_logged(tmp_path):
    client = TestClient(make_app(tmp_path))

    client.post("/internal/events", json={"device_id": "pico-safe-001"})
    response = client.get("/api/logs")

    assert response.status_code == 200
    logs = response.json()["logs"]
    assert logs[0]["level"] == "warning"
    assert logs[0]["message"] == "Invalid event payload rejected"


def test_device_heartbeat_keeps_device_online(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.post("/internal/heartbeats/device", json=make_heartbeat())
    devices_response = client.get("/api/devices")

    assert response.status_code == 201
    assert response.json() == {"accepted": True, "device_id": "pico-safe-001"}
    device = devices_response.json()["devices"][0]
    assert device["device_id"] == "pico-safe-001"
    assert device["status"] == "online"
    assert device["last_seen_at"] is not None


def test_old_device_heartbeat_marks_device_offline(tmp_path):
    client = TestClient(make_app(tmp_path))
    old_timestamp = datetime(2020, 1, 1, 10, 0, tzinfo=timezone.utc)

    response = client.post("/internal/heartbeats/device", json=make_heartbeat(timestamp=old_timestamp))
    devices_response = client.get("/api/devices")

    assert response.status_code == 201
    device = devices_response.json()["devices"][0]
    assert device["device_id"] == "pico-safe-001"
    assert device["status"] == "offline"


def test_fresh_reading_does_not_create_stale_alert(tmp_path):
    client = TestClient(make_app(tmp_path))

    client.post("/internal/events", json=make_payload(event_id="fresh-reading"))
    response = client.get("/api/alerts")

    assert response.status_code == 200
    assert all(alert["code"] != "sensor.stale" for alert in response.json()["alerts"])


def test_process_heartbeat_updates_health_process_status(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.post("/internal/heartbeats/process", json=make_process_heartbeat(status="degraded"))
    health_response = client.get("/api/health")

    assert response.status_code == 201
    assert response.json() == {"accepted": True, "process": "collector"}
    assert health_response.json()["processes"]["collector"] == "degraded"


def test_invalid_event_payload_writes_developer_file_log(tmp_path):
    log_path = tmp_path / "logs" / "saferoom.log"
    client = TestClient(make_app(tmp_path, log_path=log_path))

    client.post("/internal/events", json={"device_id": "pico-safe-001"})

    assert "warning Invalid event payload rejected" in log_path.read_text()
