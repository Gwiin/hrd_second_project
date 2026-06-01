from datetime import datetime, timezone

from fastapi.testclient import TestClient

from apps.backend.main import create_app


def test_health_reports_level1_processes():
    client = TestClient(create_app())

    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert body["app"] == "Pico SafeRoom"
    assert body["status"] == "running"
    assert body["processes"]["backend"] == "online"
    assert body["processes"]["collector"] == "simulated"
    assert body["processes"]["worker"] == "simulated"


def test_devices_api_returns_four_pico_2w_devices():
    client = TestClient(create_app())

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


def test_ingest_event_updates_latest_readings():
    client = TestClient(create_app())
    payload = {
        "site_id": "safe-room-lab",
        "zone_id": "room-1",
        "device_id": "pico-safe-001",
        "sensor_id": "temperature",
        "protocol": "mock",
        "value": 23.6,
        "unit": "celsius",
        "timestamp": datetime(2026, 6, 1, 10, 0, tzinfo=timezone.utc).isoformat(),
        "quality": "good",
        "metadata": {"seq": 7},
    }

    ingest_response = client.post("/internal/events", json=payload)
    latest_response = client.get("/api/readings/latest")

    assert ingest_response.status_code == 201
    assert latest_response.status_code == 200
    readings = latest_response.json()["readings"]
    assert readings["pico-safe-001"]["temperature"]["value"] == 23.6
    assert readings["pico-safe-001"]["temperature"]["device_id"] == "pico-safe-001"
