from __future__ import annotations

import time
from datetime import datetime, timezone


def run(interval_seconds: float = 5.0) -> None:
    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        print(f"[worker] heartbeat {timestamp}", flush=True)
        time.sleep(interval_seconds)


if __name__ == "__main__":
    run()
