import sys
from types import SimpleNamespace

from firmware.pico2w import sensors


class FakeDHTSensor:
    def __init__(self, pin, temperature, humidity):
        self.pin = pin
        self._temperature = temperature
        self._humidity = humidity

    def measure(self):
        pass

    def temperature(self):
        return self._temperature

    def humidity(self):
        return self._humidity


def install_fake_modules(monkeypatch, sensor_type):
    fake_config = SimpleNamespace(
        ENABLE_DHT=True,
        ENABLE_MOTION=False,
        ENABLE_GAS=False,
        ENABLE_LIGHT=False,
        PIN_DHT=16,
        PIN_MOTION=17,
        PIN_GAS_ADC=26,
        PIN_LIGHT_ADC=27,
        DHT_SENSOR_TYPE=sensor_type,
    )
    fake_machine = SimpleNamespace(
        ADC=lambda pin: None,
        Pin=lambda pin, mode=None: ("pin", pin, mode),
    )
    fake_dht = SimpleNamespace(
        DHT11=lambda pin: FakeDHTSensor(pin, 26, 56),
        DHT22=lambda pin: FakeDHTSensor(pin, 666.2, 1382.4),
    )

    monkeypatch.setitem(sys.modules, "config", fake_config)
    monkeypatch.setitem(sys.modules, "machine", fake_machine)
    monkeypatch.setitem(sys.modules, "dht", fake_dht)


def test_read_all_sensors_uses_configured_dht11_driver(monkeypatch):
    install_fake_modules(monkeypatch, "DHT11")

    readings = sensors.read_all_sensors()

    assert readings == [
        ("temperature", 26, "celsius"),
        ("humidity", 56, "%"),
    ]


def test_read_all_sensors_uses_configured_dht22_driver(monkeypatch):
    install_fake_modules(monkeypatch, "DHT22")

    readings = sensors.read_all_sensors()

    assert readings == [
        ("temperature", 666.2, "celsius"),
        ("humidity", 1382.4, "%"),
    ]
