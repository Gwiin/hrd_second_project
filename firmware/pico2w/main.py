import json
import time

import network
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
from payloads import heartbeat_payload, heartbeat_topic, reading_payload, reading_topic
from sensors import read_all_sensors


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


def publish_readings(client, seq):
    now = timestamp()
    for sensor_id, value, unit in read_all_sensors():
        payload = reading_payload(DEVICE_ID, ZONE_ID, sensor_id, value, unit, now, seq)
        client.publish(reading_topic(ZONE_ID, DEVICE_ID, sensor_id), json.dumps(payload))


def publish_heartbeat(client, seq):
    payload = heartbeat_payload(DEVICE_ID, ZONE_ID, timestamp(), time.ticks_ms(), seq)
    client.publish(heartbeat_topic(ZONE_ID, DEVICE_ID), json.dumps(payload))


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
