from apps.collector.simulator import LEVEL1_DEVICE_IDS, LEVEL1_SENSOR_IDS, generate_sensor_events
from shared.schemas.sensor_event import SensorEvent


def test_generate_sensor_events_includes_all_level1_sensors():
    events = generate_sensor_events(seq=1)

    assert {event.sensor_id for event in events} == set(LEVEL1_SENSOR_IDS)
    assert {event.device_id for event in events} == set(LEVEL1_DEVICE_IDS)
    assert len(events) == len(LEVEL1_DEVICE_IDS) * len(LEVEL1_SENSOR_IDS)
    assert all(isinstance(event, SensorEvent) for event in events)


def test_generated_events_use_pico_saferoom_identity():
    event = generate_sensor_events(seq=3)[0]

    assert event.site_id == "safe-room-lab"
    assert event.zone_id == "room-1"
    assert event.device_id == "pico-safe-001"
    assert event.protocol == "mock"
    assert event.metadata["seq"] == 3


def test_simulator_keeps_mock_protocol():
    events = generate_sensor_events(seq=1)

    assert {event.protocol for event in events} == {"mock"}
