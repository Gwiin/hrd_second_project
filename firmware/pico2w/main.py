import json
import time

import network
from machine import ADC
from umqtt.simple import MQTTClient

from config import (
    DEVICE_ID,
    MQTT_HOST,
    MQTT_PORT,
    PUBLISH_INTERVAL_SECONDS,
    WIFI_PASSWORD,
    WIFI_SSID,
    ZONE_ID,
)


SENSORS = {
    "temperature": "celsius",
    "humidity": "%",
    "light": "lux",
    "motion": "bool",
    "gas": "ppm",
}


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)
    return wlan


def mqtt_client():
    client = MQTTClient(DEVICE_ID, MQTT_HOST, port=MQTT_PORT)
    client.connect()
    return client


def reading_topic(sensor_id):
    return "saferoom/{}/{}/sensors/{}/reading".format(ZONE_ID, DEVICE_ID, sensor_id)


def heartbeat_topic():
    return "saferoom/{}/{}/status".format(ZONE_ID, DEVICE_ID)


def timestamp():
    year, month, day, hour, minute, second, _, _ = time.localtime()
    return "{:04d}-{:02d}-{:02d}T{:02d}:{:02d}:{:02d}+00:00".format(
        year,
        month,
        day,
        hour,
        minute,
        second,
    )


def virtual_readings(seq):
    adc_value = ADC(4).read_u16()
    temperature = 20 + (adc_value / 65535) * 15
    return {
        "temperature": round(temperature, 1),
        "humidity": 45 + (seq % 10),
        "light": 250 + (seq % 20) * 15,
        "motion": seq % 17 == 0,
        "gas": round(0.25 + (seq % 8) * 0.03, 2),
    }


def publish_readings(client, seq):
    now = timestamp()
    for sensor_id, value in virtual_readings(seq).items():
        payload = {
            "device_id": DEVICE_ID,
            "zone_id": ZONE_ID,
            "sensor_id": sensor_id,
            "value": value,
            "unit": SENSORS[sensor_id],
            "timestamp": now,
            "seq": seq,
        }
        client.publish(reading_topic(sensor_id), json.dumps(payload))


def publish_heartbeat(client, seq):
    payload = {
        "device_id": DEVICE_ID,
        "zone_id": ZONE_ID,
        "status": "online",
        "timestamp": timestamp(),
        "uptime_ms": time.ticks_ms(),
        "seq": seq,
    }
    client.publish(heartbeat_topic(), json.dumps(payload))


def main():
    connect_wifi()
    client = mqtt_client()
    seq = 1
    while True:
        publish_readings(client, seq)
        publish_heartbeat(client, seq)
        seq += 1
        time.sleep(PUBLISH_INTERVAL_SECONDS)


main()
