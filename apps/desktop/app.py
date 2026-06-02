from __future__ import annotations

import argparse
import subprocess
import sys
import time
import urllib.request
import webbrowser
from contextlib import suppress


BACKEND_URL = "http://127.0.0.1:8000"


def wait_for_backend(url: str = BACKEND_URL, timeout_seconds: float = 15.0) -> bool:
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        with suppress(Exception):
            with urllib.request.urlopen(f"{url}/api/health", timeout=1) as response:
                return response.status == 200
        time.sleep(0.25)
    return False


def start_processes() -> list[subprocess.Popen]:
    commands = [
        [sys.executable, "-m", "apps.backend.main"],
        [sys.executable, "-m", "apps.collector.mqtt_client", "--backend-url", BACKEND_URL],
        [sys.executable, "-m", "apps.worker.main"],
    ]
    return [subprocess.Popen(command) for command in commands]


def open_dashboard(url: str = BACKEND_URL, *, mode: str = "pywebview") -> None:
    if mode == "browser":
        webbrowser.open(url)
        return

    try:
        import webview
    except ImportError:
        print(f"pywebview is not installed. Opening {url} in a browser.", flush=True)
        webbrowser.open(url)
        return

    webview.create_window("Pico SafeRoom", url, width=1440, height=900)
    webview.start()


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Pico SafeRoom desktop launcher")
    parser.add_argument("--open", choices=("pywebview", "browser"), default="pywebview")
    args = parser.parse_args(argv)

    processes = start_processes()
    try:
        if not wait_for_backend():
            print(f"Backend did not become ready. Try opening {BACKEND_URL} after checking logs.", flush=True)
            return
        open_dashboard(mode=args.open)
    finally:
        for process in processes:
            process.terminate()
        for process in processes:
            with suppress(Exception):
                process.wait(timeout=5)


if __name__ == "__main__":
    main()
