def adc_u16_to_percent(raw):
    return round(max(0, min(65535, raw)) * 100 / 65535, 1)


def adc_u16_to_ppm(raw, max_ppm=1000):
    return round(max(0, min(65535, raw)) * max_ppm / 65535)


def adc_u16_to_lux(raw, max_lux=1000):
    return round(max(0, min(65535, raw)) * max_lux / 65535)


def read_dht_sensor(sensor):
    sensor.measure()
    return [
        ("temperature", round(sensor.temperature(), 1), "celsius"),
        ("humidity", round(sensor.humidity(), 1), "%"),
    ]


def read_motion(pin):
    return [("motion", bool(pin.value()), "bool")]


def read_gas(adc):
    return [("gas", adc_u16_to_ppm(adc.read_u16()), "ppm")]


def read_light(adc):
    return [("light", adc_u16_to_lux(adc.read_u16()), "lux")]


def read_all_sensors():
    from config import ENABLE_DHT, ENABLE_GAS, ENABLE_LIGHT, ENABLE_MOTION
    from config import PIN_DHT, PIN_GAS_ADC, PIN_LIGHT_ADC, PIN_MOTION
    from machine import ADC, Pin

    readings = []
    if ENABLE_DHT:
        import dht

        readings.extend(_read_or_empty(lambda: read_dht_sensor(dht.DHT22(Pin(PIN_DHT)))))
    if ENABLE_MOTION:
        readings.extend(_read_or_empty(lambda: read_motion(Pin(PIN_MOTION, Pin.IN))))
    if ENABLE_GAS:
        readings.extend(_read_or_empty(lambda: read_gas(ADC(PIN_GAS_ADC))))
    if ENABLE_LIGHT:
        readings.extend(_read_or_empty(lambda: read_light(ADC(PIN_LIGHT_ADC))))
    return readings


def _read_or_empty(read_sensor):
    try:
        return read_sensor()
    except Exception:
        return []
