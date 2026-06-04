import json
from datetime import datetime, timezone

from apps.collector import mqtt_client


class RecordingResponse:
    def raise_for_status(self):
        return None


class RecordingClient:
    requests = []

    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, json):
        self.requests.append({"url": url, "json": json})
        return RecordingResponse()


def test_post_event_sends_reading_to_internal_events(monkeypatch):
    RecordingClient.requests = []
    monkeypatch.setattr(mqtt_client.httpx, "Client", RecordingClient)
    payload = {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "sensor_id": "gas",
        "value": 320,
        "unit": "ppm",
        "timestamp": datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
    }

    mqtt_client.post_event(
        "http://127.0.0.1:8000",
        "saferoom/room-1/pico-safe-001/sensors/gas/reading",
        json.dumps(payload).encode(),
    )

    assert RecordingClient.requests[0]["url"] == "http://127.0.0.1:8000/internal/events"


def test_post_device_heartbeat_sends_status_to_internal_heartbeats(monkeypatch):
    RecordingClient.requests = []
    monkeypatch.setattr(mqtt_client.httpx, "Client", RecordingClient)
    payload = {
        "device_id": "pico-safe-001",
        "zone_id": "room-1",
        "status": "online",
        "timestamp": datetime(2026, 6, 2, 10, 0, tzinfo=timezone.utc).isoformat(),
        "uptime_ms": 12345,
    }

    mqtt_client.post_device_heartbeat(
        "http://127.0.0.1:8000",
        "saferoom/room-1/pico-safe-001/status",
        json.dumps(payload).encode(),
    )

    assert RecordingClient.requests[0]["url"] == "http://127.0.0.1:8000/internal/heartbeats/device"


def test_post_process_heartbeat_sends_collector_status(monkeypatch):
    RecordingClient.requests = []
    monkeypatch.setattr(mqtt_client.httpx, "Client", RecordingClient)

    mqtt_client.post_process_heartbeat("http://127.0.0.1:8000")

    request = RecordingClient.requests[0]
    assert request["url"] == "http://127.0.0.1:8000/internal/heartbeats/process"
    assert request["json"]["process"] == "collector"
    assert request["json"]["status"] == "online"
