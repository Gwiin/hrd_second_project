from datetime import datetime, timezone

from apps.backend.db.sqlite_repository import SQLiteRepository
from shared.schemas.sensor_event import SensorEvent


def make_event(
    *,
    event_id: str = "event-1",
    device_id: str = "pico-safe-001",
    sensor_id: str = "temperature",
    value: float = 23.6,
    timestamp: datetime | None = None,
) -> SensorEvent:
    return SensorEvent(
        event_id=event_id,
        site_id="safe-room-lab",
        zone_id="room-1",
        device_id=device_id,
        sensor_id=sensor_id,
        protocol="mock",
        value=value,
        unit="celsius",
        timestamp=timestamp or datetime.now(timezone.utc),
        quality="good",
        metadata={"seq": 7},
    )


def test_repository_persists_latest_reading_across_instances(tmp_path):
    db_path = tmp_path / "saferoom.db"
    first_repo = SQLiteRepository(db_path)
    first_repo.add_event(make_event())

    second_repo = SQLiteRepository(db_path)

    latest = second_repo.latest_readings()
    assert latest["readings"]["pico-safe-001"]["temperature"]["value"] == 23.6
    assert latest["readings"]["pico-safe-001"]["temperature"]["device_id"] == "pico-safe-001"
    assert latest["updated_at"] is not None


def test_repository_ignores_duplicate_event_ids(tmp_path):
    db_path = tmp_path / "saferoom.db"
    repo = SQLiteRepository(db_path)

    repo.add_event(make_event(event_id="same-event", value=23.6))
    repo.add_event(make_event(event_id="same-event", value=99.9))

    history = repo.reading_history()
    assert history["count"] == 1
    assert history["readings"][0]["value"] == 23.6


def test_repository_preserves_level1_device_shape(tmp_path):
    repo = SQLiteRepository(tmp_path / "saferoom.db")

    devices = repo.devices()["devices"]

    assert [device["device_id"] for device in devices] == [
        "pico-safe-001",
        "pico-safe-002",
        "pico-safe-003",
        "pico-safe-004",
    ]
    assert {device["status"] for device in devices} == {"online"}


def test_repository_creates_alert_for_gas_warning(tmp_path):
    repo = SQLiteRepository(tmp_path / "saferoom.db")

    repo.add_event(make_event(sensor_id="gas", value=320))

    alerts = repo.alerts()
    assert alerts["count"] == 1
    assert alerts["alerts"][0]["level"] == "warning"
    assert alerts["alerts"][0]["code"] == "gas.warning"
    assert alerts["alerts"][0]["status"] == "open"


def test_repository_acknowledges_alert(tmp_path):
    repo = SQLiteRepository(tmp_path / "saferoom.db")
    repo.add_event(make_event(sensor_id="temperature", value=61))
    alert_id = repo.alerts()["alerts"][0]["alert_id"]

    updated = repo.ack_alert(alert_id)

    assert updated["alert"]["alert_id"] == alert_id
    assert updated["alert"]["status"] == "acknowledged"
    assert updated["alert"]["resolved_at"] is not None


def test_incident_response_persists_across_repository_instances(tmp_path):
    db_path = tmp_path / "saferoom.db"
    first_repo = SQLiteRepository(db_path)
    first_repo.add_event(make_event(sensor_id="gas", value=601))
    alert_id = first_repo.alerts()["alerts"][0]["alert_id"]

    first_repo.ack_alert(
        alert_id,
        checklist=["evacuate", "ventilate", "inspect_sensor"],
        note="Operator opened the window.",
        evidence="Ventilation confirmed.",
    )
    second_repo = SQLiteRepository(db_path)

    replay = second_repo.alert_replay(alert_id)

    assert replay["response"] == {
        "checklist": ["evacuate", "ventilate", "inspect_sensor"],
        "note": "Operator opened the window.",
        "evidence": "Ventilation confirmed.",
    }


def test_incident_response_reack_updates_existing_row(tmp_path):
    repo = SQLiteRepository(tmp_path / "saferoom.db")
    repo.add_event(make_event(sensor_id="gas", value=601))
    alert_id = repo.alerts()["alerts"][0]["alert_id"]

    repo.ack_alert(alert_id, checklist=["evacuate"], note="First note", evidence="First evidence")
    repo.ack_alert(alert_id, checklist=["ventilate"], note="Updated note", evidence="Updated evidence")

    replay = repo.alert_replay(alert_id)

    assert replay["response"] == {
        "checklist": ["ventilate"],
        "note": "Updated note",
        "evidence": "Updated evidence",
    }


def test_repository_reports_stale_sensor_alert(tmp_path):
    repo = SQLiteRepository(tmp_path / "saferoom.db")
    old_timestamp = datetime(2020, 1, 1, 10, 0, tzinfo=timezone.utc)

    repo.add_event(make_event(event_id="old-reading", timestamp=old_timestamp))

    alerts = repo.alerts()["alerts"]
    stale_alert = next(alert for alert in alerts if alert["code"] == "sensor.stale")
    assert stale_alert["level"] == "info"
    assert stale_alert["device_id"] == "pico-safe-001"
    assert stale_alert["sensor_id"] == "temperature"
