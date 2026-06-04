from __future__ import annotations

import argparse
import time
from datetime import datetime, timezone

import httpx


def post_process_heartbeat(backend_url: str) -> None:
    payload = {
        "process": "worker",
        "status": "online",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": {},
    }
    with httpx.Client(timeout=5) as client:
        client.post(f"{backend_url}/internal/heartbeats/process", json=payload).raise_for_status()


def run(*, backend_url: str = "http://127.0.0.1:8000", interval_seconds: float = 5.0) -> None:
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        try:
            post_process_heartbeat(backend_url)
        except httpx.HTTPError as exc:
            print(f"[worker] heartbeat post failed: {exc}", flush=True)
        print(f"[worker] heartbeat {timestamp}", flush=True)
        time.sleep(interval_seconds)


def main() -> None:
    parser = argparse.ArgumentParser(description="Pico SafeRoom worker")
    parser.add_argument("--backend-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    run(backend_url=args.backend_url)


if __name__ == "__main__":
    main()
