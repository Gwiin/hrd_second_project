from __future__ import annotations

import argparse
import threading
import time
from datetime import datetime, timezone

import httpx

from apps.collector.mqtt_parser import MQTTTopicError, parse_device_heartbeat_message, parse_reading_message


def post_event(backend_url: str, topic: str, payload: bytes) -> None:
    event = parse_reading_message(topic, payload)
    with httpx.Client(timeout=5) as client:
        client.post(f"{backend_url}/internal/events", json=event.model_dump(mode="json")).raise_for_status()


def post_device_heartbeat(backend_url: str, topic: str, payload: bytes) -> None:
    heartbeat = parse_device_heartbeat_message(topic, payload)
    with httpx.Client(timeout=5) as client:
        client.post(
            f"{backend_url}/internal/heartbeats/device",
            json=heartbeat.model_dump(mode="json"),
        ).raise_for_status()


def post_process_heartbeat(backend_url: str) -> None:
    payload = {
        "process": "collector",
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {"mode": "mqtt"},
    }
    with httpx.Client(timeout=5) as client:
        client.post(f"{backend_url}/internal/heartbeats/process", json=payload).raise_for_status()


def start_process_heartbeat_loop(backend_url: str, interval_seconds: float = 5.0) -> None:
    def heartbeat_loop() -> None:
        while True:
            try:
                post_process_heartbeat(backend_url)
            except httpx.HTTPError as exc:
                print(f"MQTT collector heartbeat failed: {exc}", flush=True)
            time.sleep(interval_seconds)

    threading.Thread(target=heartbeat_loop, daemon=True).start()


def run(
    *,
    broker_host: str,
    broker_port: int,
    backend_url: str,
    topic_filter: str = "saferoom/+/+/sensors/+/reading",
    status_topic_filter: str = "saferoom/+/+/status",
) -> None:
    import paho.mqtt.client as mqtt

    start_process_heartbeat_loop(backend_url)
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(client: mqtt.Client, userdata: object, flags: object, reason_code: object, properties: object) -> None:
        client.subscribe(topic_filter)
        client.subscribe(status_topic_filter)

    def on_message(client: mqtt.Client, userdata: object, message: mqtt.MQTTMessage) -> None:
        try:
            if message.topic.endswith("/status"):
                post_device_heartbeat(backend_url, message.topic, message.payload)
            else:
                post_event(backend_url, message.topic, message.payload)
        except (httpx.HTTPError, KeyError, MQTTTopicError, ValueError) as exc:
            print(f"MQTT collector skipped message on {message.topic}: {exc}", flush=True)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_host, broker_port)
    client.loop_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Pico SafeRoom MQTT collector")
    parser.add_argument("--broker-host", default="127.0.0.1")
    parser.add_argument("--broker-port", type=int, default=1883)
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    run(broker_host=args.broker_host, broker_port=args.broker_port, backend_url=args.backend_url)


if __name__ == "__main__":
    main()
