from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, status
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from apps.backend.store import ReadingStore
from shared.schemas.sensor_event import SensorEvent


def create_app() -> FastAPI:
    app = FastAPI(title="Pico SafeRoom", version="0.1.0")
    store = ReadingStore()
    frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"

    @app.get("/api/health")
    def health() -> dict:
        return store.health()

    @app.get("/api/readings/latest")
    def latest_readings() -> dict:
        return store.latest_readings()

    @app.get("/api/devices")
    def devices() -> dict:
        return store.devices()

    @app.get("/api/logs")
    def logs() -> dict:
        return store.logs()

    @app.post("/internal/events", status_code=status.HTTP_201_CREATED)
    def ingest_event(event: SensorEvent) -> dict:
        store.add_event(event)
        return {"accepted": True, "event_id": event.event_id}

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
