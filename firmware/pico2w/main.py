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
from payloads import heartbeat_payload, heartbeat_topic, reading_payload, reading_topic, timestamp_from_localtime
from sensors import read_all_sensors


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print("wifi connecting to {}".format(WIFI_SSID))
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(0.5)
    print("wifi connected")
    return wlan


def mqtt_client():
    print("mqtt connecting to {}:{}".format(MQTT_HOST, MQTT_PORT))
    client = MQTTClient(DEVICE_ID, MQTT_HOST, port=MQTT_PORT)
    client.connect()
    print("mqtt connected as {}".format(DEVICE_ID))
    return client


def timestamp():
    return timestamp_from_localtime(time.localtime())


def ticks_ms():
    if hasattr(time, "ticks_ms"):
        return time.ticks_ms()
    return int(time.time() * 1000)


def publish_readings(client, seq):
    now = timestamp()
    for sensor_id, value, unit in read_all_sensors():
        payload = reading_payload(DEVICE_ID, ZONE_ID, sensor_id, value, unit, now, seq)
        client.publish(reading_topic(ZONE_ID, DEVICE_ID, sensor_id), json.dumps(payload))


def publish_heartbeat(client, seq):
    payload = heartbeat_payload(DEVICE_ID, ZONE_ID, timestamp(), ticks_ms(), seq)
    client.publish(heartbeat_topic(ZONE_ID, DEVICE_ID), json.dumps(payload))


def publish_cycle(client, seq):
    publish_readings(client, seq)
    publish_heartbeat(client, seq)


def run_forever():
    wlan = None
    client = None
    seq = 1
    while True:
        try:
            if wlan is None or not wlan.isconnected():
                wlan = connect_wifi()
                client = None
            if client is None:
                client = mqtt_client()
            publish_cycle(client, seq)
            print("published seq {}".format(seq))
            seq += 1
            time.sleep(PUBLISH_INTERVAL_SECONDS)
        except Exception as exc:
            print("runtime error: {}".format(exc))
            client = None
            time.sleep(2)


if __name__ in ("__main__", "main"):
    run_forever()
