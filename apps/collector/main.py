from __future__ import annotations

import argparse
import time

import httpx

from apps.collector.simulator import generate_sensor_events


def post_events(backend_url: str, seq: int) -> None:
    with httpx.Client(timeout=5) as client:
        for event in generate_sensor_events(seq):
            client.post(f"{backend_url}/internal/events", json=event.model_dump(mode="json")).raise_for_status()


def run(backend_url: str, interval_seconds: float) -> None:
    seq = 1
    while True:
        post_events(backend_url, seq)
        seq += 1
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pico SafeRoom Level 1 collector simulator")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000")
    parser.add_argument("--interval", type=float, default=2.0)
    args = parser.parse_args()
    run(args.backend_url, args.interval)


if __name__ == "__main__":
    main()
