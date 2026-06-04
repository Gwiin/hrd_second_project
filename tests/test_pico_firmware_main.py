import importlib
import sys
from types import SimpleNamespace


class FakeWLAN:
    def __init__(self, connected=False):
        self.connected = connected
        self.active_calls = []
        self.connect_calls = []

    def active(self, enabled):
        self.active_calls.append(enabled)

    def connect(self, ssid, password):
        self.connect_calls.append((ssid, password))
        self.connected = True

    def isconnected(self):
        return self.connected


class FakeMQTTClient:
    instances = []

    def __init__(self, client_id, host, port):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.connected = False
        self.published = []
        FakeMQTTClient.instances.append(self)

    def connect(self):
        self.connected = True

    def publish(self, topic, payload):
        self.published.append((topic, payload))


def import_firmware_main(monkeypatch, *, wlan=None):
    fake_config = SimpleNamespace(
        DEVICE_ID="pico-safe-001",
        MQTT_HOST="163.152.213.111",
        MQTT_PORT=1883,
        PUBLISH_INTERVAL_SECONDS=5,
        WIFI_PASSWORD="password",
        WIFI_SSID="ssid",
        ZONE_ID="room-1",
    )
    fake_network = SimpleNamespace(STA_IF=0, WLAN=lambda _: wlan or FakeWLAN())
    fake_umqtt_simple = SimpleNamespace(MQTTClient=FakeMQTTClient)
    fake_payloads = SimpleNamespace(
        heartbeat_payload=lambda *args: {"heartbeat": args},
        heartbeat_topic=lambda zone_id, device_id: f"saferoom/{zone_id}/{device_id}/status",
        reading_payload=lambda *args: {"reading": args},
        reading_topic=lambda zone_id, device_id, sensor_id: f"saferoom/{zone_id}/{device_id}/sensors/{sensor_id}/reading",
        timestamp_from_localtime=lambda _: "2026-06-04T10:00:00+00:00",
    )
    fake_sensors = SimpleNamespace(read_all_sensors=lambda: [("temperature", 25, "celsius")])

    monkeypatch.setitem(sys.modules, "config", fake_config)
    monkeypatch.setitem(sys.modules, "network", fake_network)
    monkeypatch.setitem(sys.modules, "umqtt", SimpleNamespace(simple=fake_umqtt_simple))
    monkeypatch.setitem(sys.modules, "umqtt.simple", fake_umqtt_simple)
    monkeypatch.setitem(sys.modules, "payloads", fake_payloads)
    monkeypatch.setitem(sys.modules, "sensors", fake_sensors)
    sys.modules.pop("firmware.pico2w.main", None)
    return importlib.import_module("firmware.pico2w.main")


def test_importing_firmware_main_does_not_start_loop(monkeypatch):
    module = import_firmware_main(monkeypatch)

    assert hasattr(module, "run_forever")


def test_connect_wifi_activates_and_connects_when_disconnected(monkeypatch):
    wlan = FakeWLAN(connected=False)
    module = import_firmware_main(monkeypatch, wlan=wlan)

    returned = module.connect_wifi()

    assert returned is wlan
    assert wlan.active_calls == [True]
    assert wlan.connect_calls == [("ssid", "password")]


def test_mqtt_client_connects_with_configured_host(monkeypatch):
    FakeMQTTClient.instances = []
    module = import_firmware_main(monkeypatch)

    client = module.mqtt_client()

    assert client.connected is True
    assert client.host == "163.152.213.111"
    assert client.port == 1883
