import importlib
from datetime import datetime, timezone
from pathlib import Path

from fastapi.testclient import TestClient

import apps.backend.auth as backend_auth
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
    timestamp: datetime | None = None,
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
        "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
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
    assert body["processes"]["collector"] == "offline"
    assert body["processes"]["worker"] == "offline"


def test_favicon_route_prevents_browser_404(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.get("/favicon.ico")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("image/svg+xml")


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
    assert {device["status"] for device in devices} == {"offline"}


def test_liveness_marks_never_seen_devices_offline(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/liveness")

    assert response.status_code == 200
    devices = response.json()["devices"]
    assert {device["device_id"] for device in devices} == {
        "pico-safe-001",
        "pico-safe-002",
        "pico-safe-003",
        "pico-safe-004",
    }
    assert {device["status"] for device in devices} == {"offline"}


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


def test_backend_server_defaults_to_lan_access(monkeypatch):
    monkeypatch.delenv("PICO_BACKEND_HOST", raising=False)
    monkeypatch.delenv("PICO_BACKEND_PORT", raising=False)

    assert backend_main.server_host() == "0.0.0.0"
    assert backend_main.server_port() == 8000


def test_backend_server_bind_can_be_overridden(monkeypatch):
    monkeypatch.setenv("PICO_BACKEND_HOST", "127.0.0.1")
    monkeypatch.setenv("PICO_BACKEND_PORT", "9000")

    assert backend_main.server_host() == "127.0.0.1"
    assert backend_main.server_port() == 9000


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


def test_gas_critical_alert_includes_response_guidance(tmp_path):
    client = TestClient(make_app(tmp_path))
    client.post("/internal/events", json=make_payload(event_id="gas-guidance", sensor_id="gas", value=601))

    response = client.get("/api/alerts/1/replay")

    assert response.status_code == 200
    guidance = response.json()["guidance"]
    assert guidance["summary"] == "Critical gas level detected"
    assert guidance["recommended_action"] == "Evacuate, ventilate the room, and inspect the gas sensor before re-entry."
    assert [item["id"] for item in guidance["checklist"]] == ["evacuate", "ventilate", "inspect_sensor"]


def test_unknown_alert_code_uses_safe_guidance_fallback(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/alerts/guidance/unknown.code")

    assert response.status_code == 200
    guidance = response.json()["guidance"]
    assert guidance["summary"] == "Investigate alert"
    assert [item["id"] for item in guidance["checklist"]] == ["inspect_area", "check_sensor"]


def test_ack_alert_api_accepts_response_evidence(tmp_path):
    client = TestClient(make_app(tmp_path))
    client.post("/internal/events", json=make_payload(event_id="gas-response", sensor_id="gas", value=601))

    response = client.post(
        "/api/alerts/1/ack",
        json={
            "checklist": ["evacuate", "ventilate"],
            "note": "Operator opened the window.",
            "evidence": "Ventilation confirmed.",
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["alert"]["status"] == "acknowledged"
    assert body["response"] == {
        "checklist": ["evacuate", "ventilate"],
        "note": "Operator opened the window.",
        "evidence": "Ventilation confirmed.",
    }


def test_alert_replay_returns_incident_bundle(tmp_path):
    client = TestClient(make_app(tmp_path))
    client.post("/internal/events", json=make_payload(event_id="gas-replay", sensor_id="gas", value=601))

    response = client.get("/api/alerts/1/replay")

    assert response.status_code == 200
    body = response.json()
    assert body["alert"]["code"] == "gas.critical"
    assert body["guidance"]["summary"] == "Critical gas level detected"
    assert body["response"] is None
    assert {event["type"] for event in body["related_events"]} >= {"alert", "reading", "log"}


def test_alert_replay_unknown_alert_returns_404(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/alerts/999/replay")

    assert response.status_code == 404
    assert response.json()["detail"] == "Alert not found"


def test_ack_alert_rejects_too_long_response_note(tmp_path):
    client = TestClient(make_app(tmp_path))
    client.post("/internal/events", json=make_payload(event_id="gas-long-note", sensor_id="gas", value=601))

    response = client.post(
        "/api/alerts/1/ack",
        json={"checklist": ["evacuate"], "note": "x" * 501, "evidence": "short"},
    )

    assert response.status_code == 422


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


def test_liveness_api_separates_devices_and_processes(tmp_path):
    client = TestClient(make_app(tmp_path))

    client.post("/internal/heartbeats/device", json=make_heartbeat())
    client.post("/internal/heartbeats/process", json=make_process_heartbeat(status="degraded"))
    response = client.get("/api/liveness")

    assert response.status_code == 200
    body = response.json()
    assert body["devices"][0]["kind"] == "device"
    assert body["devices"][0]["device_id"] == "pico-safe-001"
    assert body["devices"][0]["status"] == "online"
    collector = next(process for process in body["processes"] if process["process"] == "collector")
    assert collector["kind"] == "process"
    assert collector["status"] == "degraded"
    assert collector["last_seen_at"] is not None


def test_timeline_api_returns_blackbox_events(tmp_path):
    client = TestClient(make_app(tmp_path))

    client.post("/internal/heartbeats/device", json=make_heartbeat())
    client.post("/internal/heartbeats/process", json=make_process_heartbeat(process="collector", status="online"))
    client.post("/internal/events", json=make_payload(event_id="gas-critical", sensor_id="gas", value=601))
    response = client.get("/api/timeline?limit=20")

    assert response.status_code == 200
    body = response.json()
    assert body["count"] >= 4
    event_types = {entry["type"] for entry in body["events"]}
    assert {"reading", "alert", "device_heartbeat", "process_heartbeat", "log"} <= event_types
    alert = next(entry for entry in body["events"] if entry["type"] == "alert")
    assert alert["tone"] == "critical"
    assert alert["device_id"] == "pico-safe-001"
    assert alert["sensor_id"] == "gas"


def test_invalid_event_payload_writes_developer_file_log(tmp_path):
    log_path = tmp_path / "logs" / "saferoom.log"
    client = TestClient(make_app(tmp_path, log_path=log_path))

    client.post("/internal/events", json={"device_id": "pico-safe-001"})

    assert "warning Invalid event payload rejected" in log_path.read_text()


def test_email_signup_creates_session_and_me_returns_user(tmp_path):
    client = TestClient(make_app(tmp_path))

    response = client.post(
        "/api/auth/signup",
        json={"email": "team@example.com", "password": "safe-password-123"},
    )
    me_response = client.get("/api/auth/me")

    assert response.status_code == 201
    assert "saferoom_session" in response.headers["set-cookie"]
    assert response.json()["user"] == {
        "user_id": 1,
        "email": "team@example.com",
        "display_name": "team",
        "provider": "email",
    }
    assert me_response.status_code == 200
    assert me_response.json()["authenticated"] is True
    assert me_response.json()["user"]["email"] == "team@example.com"


def test_email_login_rejects_wrong_password_and_accepts_correct_password(tmp_path):
    client = TestClient(make_app(tmp_path))
    client.post(
        "/api/auth/signup",
        json={"email": "team@example.com", "password": "safe-password-123"},
    )
    client.post("/api/auth/logout")

    wrong_response = client.post(
        "/api/auth/login",
        json={"email": "team@example.com", "password": "wrong-password"},
    )
    login_response = client.post(
        "/api/auth/login",
        json={"email": "team@example.com", "password": "safe-password-123"},
    )

    assert wrong_response.status_code == 401
    assert login_response.status_code == 200
    assert login_response.json()["user"]["email"] == "team@example.com"


def test_logout_clears_authenticated_session(tmp_path):
    client = TestClient(make_app(tmp_path))
    client.post(
        "/api/auth/signup",
        json={"email": "team@example.com", "password": "safe-password-123"},
    )

    response = client.post("/api/auth/logout")
    me_response = client.get("/api/auth/me")

    assert response.status_code == 200
    assert "saferoom_session=\"\"" in response.headers["set-cookie"]
    assert me_response.status_code == 200
    assert me_response.json() == {"authenticated": False, "user": None}


def test_duplicate_email_signup_is_rejected(tmp_path):
    client = TestClient(make_app(tmp_path))
    payload = {"email": "team@example.com", "password": "safe-password-123"}

    first_response = client.post("/api/auth/signup", json=payload)
    duplicate_response = client.post("/api/auth/signup", json=payload)

    assert first_response.status_code == 201
    assert duplicate_response.status_code == 409
    assert duplicate_response.json()["detail"] == "Email already registered"


def test_social_auth_providers_include_google_and_kakao(monkeypatch, tmp_path):
    for provider in ("GOOGLE", "KAKAO"):
        monkeypatch.delenv(f"PICO_AUTH_{provider}_CLIENT_ID", raising=False)
        monkeypatch.delenv(f"PICO_AUTH_{provider}_CLIENT_SECRET", raising=False)
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/auth/social/providers")

    assert response.status_code == 200
    body = response.json()
    assert [provider["provider"] for provider in body["providers"]] == ["google", "kakao"]
    assert {provider["configured"] for provider in body["providers"]} == {False}


def test_configured_social_provider_start_redirects(monkeypatch, tmp_path):
    monkeypatch.setenv("PICO_AUTH_GOOGLE_CLIENT_ID", "google-client")
    monkeypatch.setenv("PICO_AUTH_GOOGLE_CLIENT_SECRET", "google-secret")
    monkeypatch.setenv("PICO_AUTH_REDIRECT_BASE_URL", "http://127.0.0.1:8000")
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/auth/social/google/start", follow_redirects=False)

    assert response.status_code == 307
    assert "accounts.google.com" in response.headers["location"]
    assert "client_id=google-client" in response.headers["location"]
    assert "saferoom_oauth_state_google" in response.headers["set-cookie"]


def test_kakao_social_provider_does_not_request_account_email(monkeypatch, tmp_path):
    monkeypatch.setenv("PICO_AUTH_KAKAO_CLIENT_ID", "kakao-client")
    monkeypatch.setenv("PICO_AUTH_KAKAO_CLIENT_SECRET", "kakao-secret")
    client = TestClient(make_app(tmp_path))

    response = client.get("/api/auth/social/kakao/start", follow_redirects=False)

    assert response.status_code == 307
    assert "kauth.kakao.com" in response.headers["location"]
    assert "scope=profile_nickname" in response.headers["location"]
    assert "account_email" not in response.headers["location"]


def test_social_callback_rejects_state_mismatch(monkeypatch, tmp_path):
    monkeypatch.setenv("PICO_AUTH_GOOGLE_CLIENT_ID", "google-client")
    monkeypatch.setenv("PICO_AUTH_GOOGLE_CLIENT_SECRET", "google-secret")
    client = TestClient(make_app(tmp_path))
    client.cookies.set("saferoom_oauth_state_google", "expected-state")

    response = client.get("/api/auth/social/google/callback?code=oauth-code&state=wrong-state")

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid OAuth state"


def test_google_social_callback_creates_session(monkeypatch, tmp_path):
    monkeypatch.setenv("PICO_AUTH_GOOGLE_CLIENT_ID", "google-client")
    monkeypatch.setenv("PICO_AUTH_GOOGLE_CLIENT_SECRET", "google-secret")
    calls = []

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def post(self, url, data):
            calls.append(("post", url, data))
            return FakeResponse({"access_token": "google-access-token"})

        def get(self, url, headers):
            calls.append(("get", url, headers))
            return FakeResponse(
                {
                    "sub": "google-subject-1",
                    "email": "google-user@example.com",
                    "name": "Google User",
                }
            )

    monkeypatch.setattr(backend_auth, "httpx", type("FakeHttpx", (), {"Client": FakeClient}), raising=False)
    client = TestClient(make_app(tmp_path))
    client.cookies.set("saferoom_oauth_state_google", "expected-state")

    response = client.get(
        "/api/auth/social/google/callback?code=oauth-code&state=expected-state",
        follow_redirects=False,
    )
    me_response = client.get("/api/auth/me")

    assert response.status_code == 307
    assert response.headers["location"] == "/"
    assert "saferoom_session" in response.headers["set-cookie"]
    assert me_response.json()["authenticated"] is True
    assert me_response.json()["user"] == {
        "user_id": 1,
        "email": "google-user@example.com",
        "display_name": "Google User",
        "provider": "google",
    }
    assert calls[0][0] == "post"
    assert calls[0][1] == "https://oauth2.googleapis.com/token"
    assert calls[1] == (
        "get",
        "https://openidconnect.googleapis.com/v1/userinfo",
        {"Authorization": "Bearer google-access-token"},
    )


def test_kakao_social_callback_maps_kakao_profile(monkeypatch, tmp_path):
    monkeypatch.setenv("PICO_AUTH_KAKAO_CLIENT_ID", "kakao-client")
    monkeypatch.setenv("PICO_AUTH_KAKAO_CLIENT_SECRET", "kakao-secret")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def post(self, url, data):
            return FakeResponse({"access_token": "kakao-access-token"})

        def get(self, url, headers):
            return FakeResponse(
                {
                    "id": 12345,
                    "properties": {"nickname": "Kakao User"},
                    "kakao_account": {"email": "kakao-user@example.com"},
                }
            )

    monkeypatch.setattr(backend_auth, "httpx", type("FakeHttpx", (), {"Client": FakeClient}), raising=False)
    client = TestClient(make_app(tmp_path))
    client.cookies.set("saferoom_oauth_state_kakao", "expected-state")

    response = client.get(
        "/api/auth/social/kakao/callback?code=oauth-code&state=expected-state",
        follow_redirects=False,
    )
    me_response = client.get("/api/auth/me")

    assert response.status_code == 307
    assert me_response.json()["user"] == {
        "user_id": 1,
        "email": "kakao-user@example.com",
        "display_name": "Kakao User",
        "provider": "kakao",
    }


def test_kakao_social_callback_uses_placeholder_email_without_account_email(monkeypatch, tmp_path):
    monkeypatch.setenv("PICO_AUTH_KAKAO_CLIENT_ID", "kakao-client")
    monkeypatch.setenv("PICO_AUTH_KAKAO_CLIENT_SECRET", "kakao-secret")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    class FakeClient:
        def __init__(self, timeout):
            self.timeout = timeout

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return None

        def post(self, url, data):
            return FakeResponse({"access_token": "kakao-access-token"})

        def get(self, url, headers):
            return FakeResponse({"id": 12345, "properties": {"nickname": "Kakao User"}})

    monkeypatch.setattr(backend_auth, "httpx", type("FakeHttpx", (), {"Client": FakeClient}), raising=False)
    client = TestClient(make_app(tmp_path))
    client.cookies.set("saferoom_oauth_state_kakao", "expected-state")

    response = client.get(
        "/api/auth/social/kakao/callback?code=oauth-code&state=expected-state",
        follow_redirects=False,
    )
    me_response = client.get("/api/auth/me")

    assert response.status_code == 307
    assert me_response.json()["user"] == {
        "user_id": 1,
        "email": "kakao-12345@kakao.local",
        "display_name": "Kakao User",
        "provider": "kakao",
    }
