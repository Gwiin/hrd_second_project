from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "requirements.txt"


def test_runtime_dependencies_include_websocket_server_support():
    requirements = {
        line.strip().lower()
        for line in REQUIREMENTS.read_text().splitlines()
        if line.strip() and not line.strip().startswith("#")
    }

    assert "websockets" in requirements or "wsproto" in requirements or "uvicorn[standard]" in requirements
