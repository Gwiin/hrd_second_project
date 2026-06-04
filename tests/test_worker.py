from apps.worker import main as worker_main


class RecordingResponse:
    def raise_for_status(self):
        return None


class RecordingClient:
    requests = []

    def __init__(self, timeout):
        self.timeout = timeout

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def post(self, url, json):
        self.requests.append({"url": url, "json": json})
        return RecordingResponse()


def test_post_process_heartbeat_sends_worker_status(monkeypatch):
    RecordingClient.requests = []
    monkeypatch.setattr(worker_main.httpx, "Client", RecordingClient)

    worker_main.post_process_heartbeat("http://127.0.0.1:8000")

    request = RecordingClient.requests[0]
    assert request["url"] == "http://127.0.0.1:8000/internal/heartbeats/process"
    assert request["json"]["process"] == "worker"
    assert request["json"]["status"] == "online"
