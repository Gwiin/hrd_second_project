from __future__ import annotations

import argparse

import httpx
import paho.mqtt.client as mqtt

from apps.collector.mqtt_parser import MQTTTopicError, parse_reading_message


def post_event(backend_url: str, topic: str, payload: bytes) -> None:
    event = parse_reading_message(topic, payload)
    with httpx.Client(timeout=5) as client:
        client.post(f"{backend_url}/internal/events", json=event.model_dump(mode="json")).raise_for_status()


def run(
    *,
    broker_host: str,
    broker_port: int,
    backend_url: str,
    topic_filter: str = "saferoom/+/+/sensors/+/reading",
) -> None:
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    def on_connect(client: mqtt.Client, userdata: object, flags: object, reason_code: object, properties: object) -> None:
        client.subscribe(topic_filter)

    def on_message(client: mqtt.Client, userdata: object, message: mqtt.MQTTMessage) -> None:
        try:
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
