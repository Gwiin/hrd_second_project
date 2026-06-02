from __future__ import annotations

from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, Request, WebSocket, WebSocketDisconnect, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from apps.backend.realtime import RealtimeHub
from apps.backend.store import ReadingStore
from shared.schemas.device_heartbeat import DeviceHeartbeat
from shared.schemas.process_heartbeat import ProcessHeartbeat
from shared.schemas.sensor_event import SensorEvent


def create_app(db_path: Path | None = None, log_path: Path | None = None) -> FastAPI:
    app = FastAPI(title="Pico SafeRoom", version="0.1.0")
    store: ReadingStore | None = None
    realtime = RealtimeHub()
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"

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

    @app.post("/api/alerts/{alert_id}/ack")
    def ack_alert(alert_id: int) -> dict:
        try:
            return get_store().ack_alert(alert_id)
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

    if frontend_dist.exists():
        app.mount("/assets", StaticFiles(directory=frontend_dist / "assets"), name="assets")

        @app.get("/")
        def dashboard() -> FileResponse:
            return FileResponse(frontend_dist / "index.html")
    else:

        @app.get("/")
        def dashboard_missing() -> JSONResponse:
            return JSONResponse(
                {
                    "message": "Pico SafeRoom backend is running. Build the dashboard with npm --prefix frontend run build."
                }
            )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("apps.backend.main:app", host="127.0.0.1", port=8000, reload=False)
