# Pico SafeRoom Setup

Current implementation target: Level 5D from `docs/superpowers`.

`README.md` is intentionally not updated for this pass. All next-level setup notes and change notes live here.

## What Changed In This Pass

- Confirmed the existing code implements the `docs/superpowers` Level 1 through Level 5D plans.
- Updated the frontend build script to run `vite build --configLoader runner`; this avoids Vite 7/esbuild scanning unreadable parent directories in the Windows sandbox.
- Updated this setup document from the old Level 1-only state to the current Level 5D runtime.

## Current Scope

Included:

- FastAPI backend with normalized `SensorEvent` ingest.
- SQLite persistence for readings, history, system logs, alerts, devices, and process heartbeats.
- Four registered Raspberry Pi Pico 2W device identities:
  - `pico-safe-001`
  - `pico-safe-002`
  - `pico-safe-003`
  - `pico-safe-004`
- Threshold alerts, alert acknowledgement, stale sensor detection, and safety state reporting.
- Device heartbeat API with offline status computation.
- Process heartbeat API with persisted backend, collector, and worker status.
- UI-facing logs through `/api/logs` and developer file logs at `logs/saferoom.log`.
- MQTT reading parser and MQTT collector runtime.
- Pico 2W MicroPython firmware scaffold under `firmware/pico2w/`.
- WebSocket realtime reading updates at `/ws/realtime`.
- React/Vite dashboard served by the backend after frontend build.
- pywebview desktop launcher that starts backend, simulator collector, and worker processes.

Deferred:

- Full process supervisor.
- Log rotation.
- WebSocket process heartbeat events.
- External observability tools.
- Production MQTT broker provisioning.
- Real secrets in firmware config.

## Setup

Use Python 3.11.15 through the repo-local virtual environment.

PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd install --prefix frontend
```

POSIX shell:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install --prefix frontend
```

If PowerShell blocks `npm.ps1`, use `npm.cmd`.

## Validate

PowerShell:

```powershell
New-Item -ItemType Directory -Force data | Out-Null
$env:TEMP = (Resolve-Path data).Path
$env:TMP = (Resolve-Path data).Path
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=data\pytest-temp
npm.cmd --prefix frontend run build
```

POSIX shell:

```bash
.venv/bin/python -m pytest
npm --prefix frontend run build
```

The PowerShell pytest command uses a repo-local temp directory because this Codex workspace cannot access the default Windows pytest temp directory.

## Run Backend And Simulator

Build the dashboard first so FastAPI can serve `frontend/dist`.

PowerShell:

```powershell
npm.cmd --prefix frontend run build
.\.venv\Scripts\python.exe -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
```

In another terminal:

```powershell
.\.venv\Scripts\python.exe -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
```

Open:

```text
http://127.0.0.1:8000
```

## Run MQTT Collector

Start a local MQTT broker separately, then run:

```powershell
.\.venv\Scripts\python.exe -m apps.collector.mqtt_client --broker-host 127.0.0.1 --broker-port 1883 --backend-url http://127.0.0.1:8000
```

The collector subscribes to:

```text
saferoom/+/+/sensors/+/reading
```

## Run Desktop Launcher

```powershell
.\.venv\Scripts\python.exe -m apps.desktop.app
```

The launcher starts backend, simulator collector, and worker as separate processes. It opens pywebview when a GUI session is available; otherwise use the printed local URL.

## Runtime Data

- SQLite database: `data/saferoom.db`
- Developer log file: `logs/saferoom.log`
- Frontend build output: `frontend/dist`
- Pico firmware example config: `firmware/pico2w/config.example.py`
- Real firmware config, if created locally: `firmware/pico2w/config.py`

`data/`, `logs/`, `frontend/dist/`, and `firmware/pico2w/config.py` are ignored by git.
