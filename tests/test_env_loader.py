import os

from apps.backend.env import load_dotenv


def test_load_dotenv_reads_key_value_pairs(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                'PICO_AUTH_REDIRECT_BASE_URL="http://127.0.0.1:8000"',
                "PICO_AUTH_GOOGLE_CLIENT_ID=google-client",
                "PICO_AUTH_GOOGLE_CLIENT_SECRET=google-secret",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("PICO_AUTH_REDIRECT_BASE_URL", raising=False)
    monkeypatch.delenv("PICO_AUTH_GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("PICO_AUTH_GOOGLE_CLIENT_SECRET", raising=False)

    load_dotenv(env_path)

    assert os.environ["PICO_AUTH_REDIRECT_BASE_URL"] == "http://127.0.0.1:8000"
    assert os.environ["PICO_AUTH_GOOGLE_CLIENT_ID"] == "google-client"
    assert os.environ["PICO_AUTH_GOOGLE_CLIENT_SECRET"] == "google-secret"


def test_load_dotenv_does_not_override_existing_env(tmp_path, monkeypatch):
    env_path = tmp_path / ".env"
    env_path.write_text("PICO_AUTH_GOOGLE_CLIENT_ID=file-client\n", encoding="utf-8")
    monkeypatch.setenv("PICO_AUTH_GOOGLE_CLIENT_ID", "shell-client")

    load_dotenv(env_path)

    assert os.environ["PICO_AUTH_GOOGLE_CLIENT_ID"] == "shell-client"
