from __future__ import annotations

import secrets
import os
from pathlib import Path
from typing import Annotated

from fastapi import Body, Cookie, FastAPI, HTTPException, Query, Request, Response, WebSocket, WebSocketDisconnect, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from apps.backend.auth import (
    OAUTH_PROVIDERS,
    OAUTH_STATE_COOKIE_PREFIX,
    SESSION_COOKIE,
    SESSION_MAX_AGE_SECONDS,
    AuthCredentials,
    exchange_oauth_code,
    new_oauth_state,
    social_provider_summaries,
)
from apps.backend.incidents import AlertResponsePayload
from apps.backend.realtime import RealtimeHub
from apps.backend.store import ReadingStore
from shared.schemas.device_heartbeat import DeviceHeartbeat
from shared.schemas.process_heartbeat import ProcessHeartbeat
from shared.schemas.sensor_event import SensorEvent


def create_app(
    db_path: Path | None = None,
    log_path: Path | None = None,
    frontend_dist: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="Pico SafeRoom", version="0.1.0")
    store: ReadingStore | None = None
    realtime = RealtimeHub()
    resolved_frontend_dist = frontend_dist or Path(__file__).resolve().parents[2] / "frontend" / "dist"

    def get_store() -> ReadingStore:
        nonlocal store
        if store is None:
            store = ReadingStore(db_path=db_path, log_path=log_path)
        return store

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        if request.url.path == "/internal/events":
            get_store().add_log("warning", "Invalid event payload rejected")
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid request payload",
                    "details": exc.errors(),
                }
            },
        )

    @app.get("/api/health")
    def health() -> dict:
        return get_store().health()

    @app.get("/api/stats")
    def stats() -> dict:
        return get_store().stats()

    @app.get("/favicon.ico")
    def favicon() -> Response:
        return Response(
            content=(
                '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
                '<rect width="64" height="64" rx="16" fill="#eaf4f8"/>'
                '<circle cx="32" cy="32" r="18" fill="#19a974"/>'
                '<circle cx="32" cy="32" r="9" fill="#f7fbff"/>'
                "</svg>"
            ),
            media_type="image/svg+xml",
        )

    @app.get("/api/readings/latest")
    def latest_readings() -> dict:
        return get_store().latest_readings()

    @app.get("/api/readings/history")
    def reading_history(
        device_id: str | None = None,
        sensor_id: str | None = None,
        limit: Annotated[int, Query(ge=1, le=500)] = 100,
    ) -> dict:
        return get_store().reading_history(device_id=device_id, sensor_id=sensor_id, limit=limit)

    @app.get("/api/devices")
    def devices() -> dict:
        return get_store().devices()

    @app.get("/api/liveness")
    def liveness() -> dict:
        return get_store().liveness()

    @app.get("/api/timeline")
    def timeline(limit: Annotated[int, Query(ge=1, le=100)] = 50) -> dict:
        return get_store().timeline(limit=limit)

    @app.get("/api/logs")
    def logs() -> dict:
        return get_store().logs()

    @app.get("/api/alerts")
    def alerts() -> dict:
        return get_store().alerts()

    @app.get("/api/alerts/guidance/{code}")
    def alert_guidance(code: str) -> dict:
        return get_store().alert_guidance(code)

    @app.get("/api/auth/me")
    def auth_me(saferoom_session: Annotated[str | None, Cookie()] = None) -> dict:
        user = get_store().current_user(saferoom_session)
        return {"authenticated": user is not None, "user": user}

    @app.post("/api/auth/signup", status_code=status.HTTP_201_CREATED)
    def auth_signup(payload: AuthCredentials, response: Response) -> dict:
        user = get_store().signup_with_email(payload.email, payload.password)
        if user is None:
            raise HTTPException(status_code=409, detail="Email already registered")
        _set_session_cookie(response, get_store().create_auth_session(user["user_id"]))
        return {"user": user}

    @app.post("/api/auth/login")
    def auth_login(payload: AuthCredentials, response: Response) -> dict:
        user = get_store().login_with_email(payload.email, payload.password)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        _set_session_cookie(response, get_store().create_auth_session(user["user_id"]))
        return {"user": user}

    @app.post("/api/auth/logout")
    def auth_logout(
        response: Response,
        saferoom_session: Annotated[str | None, Cookie()] = None,
    ) -> dict:
        get_store().logout(saferoom_session)
        response.delete_cookie(SESSION_COOKIE, path="/")
        return {"ok": True}

    @app.get("/api/auth/social/providers")
    def auth_social_providers() -> dict:
        return {"providers": social_provider_summaries()}

    @app.get("/api/auth/social/{provider}/start")
    def auth_social_start(provider: str) -> RedirectResponse:
        oauth_provider = OAUTH_PROVIDERS.get(provider)
        if oauth_provider is None:
            raise HTTPException(status_code=404, detail="Social provider not found")
        if not oauth_provider.configured:
            raise HTTPException(status_code=503, detail=f"{oauth_provider.display_name} OAuth is not configured")
        state = new_oauth_state()
        redirect = RedirectResponse(oauth_provider.authorization_url(state))
        redirect.set_cookie(
            f"{OAUTH_STATE_COOKIE_PREFIX}{provider}",
            state,
            httponly=True,
            samesite="lax",
            max_age=300,
            path="/",
        )
        return redirect

    @app.get("/api/auth/social/{provider}/callback")
    def auth_social_callback(provider: str, request: Request, code: str, state: str) -> RedirectResponse:
        oauth_provider = OAUTH_PROVIDERS.get(provider)
        if oauth_provider is None:
            raise HTTPException(status_code=404, detail="Social provider not found")
        expected_state = request.cookies.get(f"{OAUTH_STATE_COOKIE_PREFIX}{provider}")
        if not expected_state or not secrets.compare_digest(expected_state, state):
            raise HTTPException(status_code=400, detail="Invalid OAuth state")
        if not oauth_provider.configured:
            raise HTTPException(status_code=503, detail=f"{oauth_provider.display_name} OAuth is not configured")

        profile = exchange_oauth_code(oauth_provider, code)
        user = get_store().login_with_social_profile(profile)
        redirect = RedirectResponse("/")
        _set_session_cookie(redirect, get_store().create_auth_session(user["user_id"]))
        redirect.delete_cookie(f"{OAUTH_STATE_COOKIE_PREFIX}{provider}", path="/")
        return redirect

    @app.get("/api/alerts/{alert_id}/replay")
    def alert_replay(alert_id: int) -> dict:
        try:
            return get_store().alert_replay(alert_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Alert not found") from exc

    @app.post("/api/alerts/{alert_id}/ack")
    def ack_alert(alert_id: int, payload: AlertResponsePayload | None = Body(default=None)) -> dict:
        response_payload = payload or AlertResponsePayload()
        try:
            return get_store().ack_alert(
                alert_id,
                checklist=response_payload.checklist,
                note=response_payload.note,
                evidence=response_payload.evidence,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Alert not found") from exc

    @app.websocket("/ws/realtime")
    async def realtime_ws(websocket: WebSocket) -> None:
        await realtime.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            realtime.disconnect(websocket)

    @app.post("/internal/events", status_code=status.HTTP_201_CREATED)
    async def ingest_event(event: SensorEvent) -> dict:
        get_store().add_event(event)
        await realtime.broadcast({"type": "reading.created", "reading": event.model_dump(mode="json")})
        return {"accepted": True, "event_id": event.event_id}

    @app.post("/internal/heartbeats/device", status_code=status.HTTP_201_CREATED)
    def ingest_device_heartbeat(heartbeat: DeviceHeartbeat) -> dict:
        get_store().add_device_heartbeat(heartbeat)
        return {"accepted": True, "device_id": heartbeat.device_id}

    @app.post("/internal/heartbeats/process", status_code=status.HTTP_201_CREATED)
    def ingest_process_heartbeat(heartbeat: ProcessHeartbeat) -> dict:
        get_store().add_process_heartbeat(heartbeat)
        return {"accepted": True, "process": heartbeat.process}

    if (resolved_frontend_dist / "index.html").exists() and (resolved_frontend_dist / "assets").is_dir():
        app.mount("/assets", StaticFiles(directory=resolved_frontend_dist / "assets"), name="assets")

        @app.get("/")
        def dashboard() -> FileResponse:
            return FileResponse(resolved_frontend_dist / "index.html")
    else:

        @app.get("/")
        def dashboard_missing() -> JSONResponse:
            return JSONResponse(
                {
                    "message": "Pico SafeRoom backend is running. Build the dashboard with npm --prefix frontend run build."
                }
            )

    return app


def _set_session_cookie(response: Response, session_token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE,
        session_token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE_SECONDS,
        path="/",
    )


app = create_app()


def server_host() -> str:
    return os.getenv("PICO_BACKEND_HOST", "0.0.0.0")


def server_port() -> int:
    return int(os.getenv("PICO_BACKEND_PORT", "8000"))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.backend.main:app", host=server_host(), port=server_port(), reload=False)
