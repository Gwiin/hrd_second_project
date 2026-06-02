from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import httpx
from pydantic import BaseModel, Field

from apps.backend.env import load_dotenv


load_dotenv()

SESSION_COOKIE = "saferoom_session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 7
OAUTH_STATE_COOKIE_PREFIX = "saferoom_oauth_state_"
PASSWORD_ITERATIONS = 210_000
SOCIAL_PROVIDERS = ("google", "kakao")


class AuthCredentials(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=8, max_length=128)


@dataclass(frozen=True)
class OAuthProvider:
    provider: str
    display_name: str
    authorize_url: str
    token_url: str
    userinfo_url: str | None
    scope: str

    @property
    def client_id_env(self) -> str:
        return f"PICO_AUTH_{self.provider.upper()}_CLIENT_ID"

    @property
    def client_secret_env(self) -> str:
        return f"PICO_AUTH_{self.provider.upper()}_CLIENT_SECRET"

    @property
    def client_id(self) -> str | None:
        return os.getenv(self.client_id_env)

    @property
    def client_secret(self) -> str | None:
        return os.getenv(self.client_secret_env)

    @property
    def configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def redirect_uri(self) -> str:
        base_url = os.getenv("PICO_AUTH_REDIRECT_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        return f"{base_url}/api/auth/social/{self.provider}/callback"

    def authorization_url(self, state: str) -> str:
        if not self.client_id:
            raise RuntimeError(f"{self.display_name} OAuth client id is not configured")
        query = urlencode(
            {
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri(),
                "response_type": "code",
                "scope": self.scope,
                "state": state,
            }
        )
        return f"{self.authorize_url}?{query}"


@dataclass(frozen=True)
class OAuthProfile:
    provider: str
    subject: str
    email: str
    display_name: str


OAUTH_PROVIDERS = {
    "google": OAuthProvider(
        provider="google",
        display_name="Google",
        authorize_url="https://accounts.google.com/o/oauth2/v2/auth",
        token_url="https://oauth2.googleapis.com/token",
        userinfo_url="https://openidconnect.googleapis.com/v1/userinfo",
        scope="openid email profile",
    ),
    "kakao": OAuthProvider(
        provider="kakao",
        display_name="Kakao",
        authorize_url="https://kauth.kakao.com/oauth/authorize",
        token_url="https://kauth.kakao.com/oauth/token",
        userinfo_url="https://kapi.kakao.com/v2/user/me",
        scope="profile_nickname account_email",
    ),
}


def normalize_email(email: str) -> str:
    return email.strip().lower()


def display_name_from_email(email: str) -> str:
    return normalize_email(email).split("@", 1)[0]


def exchange_oauth_code(provider: OAuthProvider, code: str) -> OAuthProfile:
    if not provider.client_id or not provider.client_secret:
        raise RuntimeError(f"{provider.display_name} OAuth is not configured")

    with httpx.Client(timeout=5) as client:
        token_response = client.post(
            provider.token_url,
            data={
                "grant_type": "authorization_code",
                "code": code,
                "client_id": provider.client_id,
                "client_secret": provider.client_secret,
                "redirect_uri": provider.redirect_uri(),
            },
        )
        token_response.raise_for_status()
        token_payload = token_response.json()

        access_token = token_payload["access_token"]
        if not provider.userinfo_url:
            raise RuntimeError(f"{provider.display_name} userinfo endpoint is not configured")
        profile_response = client.get(provider.userinfo_url, headers={"Authorization": f"Bearer {access_token}"})
        profile_response.raise_for_status()
        profile_payload = profile_response.json()

    if provider.provider == "google":
        return _google_profile(provider, profile_payload)
    if provider.provider == "kakao":
        return _kakao_profile(provider, profile_payload)
    raise RuntimeError(f"Unsupported OAuth provider: {provider.provider}")


def _google_profile(provider: OAuthProvider, payload: dict) -> OAuthProfile:
    email = normalize_email(payload["email"])
    return OAuthProfile(
        provider=provider.provider,
        subject=str(payload["sub"]),
        email=email,
        display_name=payload.get("name") or display_name_from_email(email),
    )


def _kakao_profile(provider: OAuthProvider, payload: dict) -> OAuthProfile:
    account = payload.get("kakao_account", {})
    email = normalize_email(account["email"])
    properties = payload.get("properties", {})
    return OAuthProfile(
        provider=provider.provider,
        subject=str(payload["id"]),
        email=email,
        display_name=properties.get("nickname") or display_name_from_email(email),
    )


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PASSWORD_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PASSWORD_ITERATIONS,
        base64.b64encode(salt).decode(),
        base64.b64encode(digest).decode(),
    )


def verify_password(password: str, encoded: str | None) -> bool:
    if not encoded:
        return False
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
    except ValueError:
        return False
    if algorithm != "pbkdf2_sha256":
        return False
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        base64.b64decode(salt),
        int(iterations),
    )
    return hmac.compare_digest(base64.b64encode(digest).decode(), expected)


def new_session_token() -> str:
    return secrets.token_urlsafe(32)


def new_oauth_state() -> str:
    return secrets.token_urlsafe(24)


def session_expires_at() -> str:
    return (datetime.now(timezone.utc) + timedelta(seconds=SESSION_MAX_AGE_SECONDS)).isoformat()


def public_user(user: dict) -> dict:
    return {
        "user_id": user["user_id"],
        "email": user["email"],
        "display_name": user["display_name"],
        "provider": user["primary_provider"],
    }


def social_provider_summaries() -> list[dict]:
    return [
        {
            "provider": provider.provider,
            "display_name": provider.display_name,
            "configured": provider.configured,
        }
        for provider in OAUTH_PROVIDERS.values()
    ]
