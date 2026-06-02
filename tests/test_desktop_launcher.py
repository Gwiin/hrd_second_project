import sys

from apps.desktop import app as desktop_app


def test_default_processes_use_real_mqtt_collector(monkeypatch):
    commands = []

    class RecordingProcess:
        def __init__(self, command):
            self.command = command
            commands.append(command)

    monkeypatch.setattr(desktop_app.subprocess, "Popen", RecordingProcess)

    processes = desktop_app.start_processes()

    assert len(processes) == 3
    assert commands == [
        [sys.executable, "-m", "apps.backend.main"],
        [
            sys.executable,
            "-m",
            "apps.collector.mqtt_client",
            "--backend-url",
            desktop_app.BACKEND_URL,
        ],
        [sys.executable, "-m", "apps.worker.main"],
    ]
    assert all("apps.collector.main" not in command for command in commands)


def test_browser_launch_mode_opens_local_dashboard(monkeypatch):
    opened_urls = []

    monkeypatch.setattr(desktop_app.webbrowser, "open", lambda url: opened_urls.append(url))

    desktop_app.open_dashboard("http://127.0.0.1:8000", mode="browser")

    assert opened_urls == ["http://127.0.0.1:8000"]
