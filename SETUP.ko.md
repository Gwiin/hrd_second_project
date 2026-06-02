# Pico SafeRoom 설치 및 실행 안내

이 문서는 팀원이 개발 환경을 만들고, backend/dashboard/simulator/MQTT collector를 실행하기 위한 한국어 안내입니다.

## 현재 포함된 기능

- FastAPI backend
- SQLite 저장소
- React/Vite dashboard
- pywebview desktop launcher
- 4개 Pico 2W 장치 ID 등록
- MQTT reading collector
- device heartbeat / process heartbeat
- threshold alert / stale sensor alert
- Pico 2W MicroPython firmware
- 실제 센서 배선 문서와 그림

## Python 가상환경 만들기

이 프로젝트는 Python 3.11을 사용합니다.

macOS/Linux:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install --prefix frontend
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd install --prefix frontend
```

PowerShell에서 `npm.ps1` 실행이 막히면 `npm.cmd`를 사용합니다.

## 검증 명령

macOS/Linux:

```bash
.venv/bin/python -m pytest
npm --prefix frontend run build
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force data | Out-Null
$env:TEMP = (Resolve-Path data).Path
$env:TMP = (Resolve-Path data).Path
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=data\pytest-temp
npm.cmd --prefix frontend run build
```

## Backend와 Simulator 실행

먼저 frontend를 build합니다.

```bash
npm --prefix frontend run build
```

Backend 실행:

```bash
.venv/bin/python -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
```

다른 터미널에서 simulator 실행:

```bash
.venv/bin/python -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
```

브라우저에서 열기:

```text
http://127.0.0.1:8000
```

## MQTT Collector 실행

실제 Pico 2W를 사용할 때는 로컬 MQTT broker를 먼저 실행해야 합니다.

```bash
.venv/bin/python -m apps.collector.mqtt_client --broker-host 127.0.0.1 --broker-port 1883 --backend-url http://127.0.0.1:8000
```

Collector가 구독하는 topic:

```text
saferoom/+/+/sensors/+/reading
saferoom/+/+/status
```

Reading topic은 `/internal/events`로 전달되고, heartbeat topic은 `/internal/heartbeats/device`로 전달됩니다.

## Desktop Launcher 실행

```bash
.venv/bin/python -m apps.desktop.app
```

Launcher는 backend, simulator collector, worker를 별도 process로 시작합니다. GUI 환경이면 pywebview 창이 열리고, 아니면 출력된 local URL을 브라우저에서 열면 됩니다.

## Runtime 파일

| 파일/폴더 | 설명 |
| --- | --- |
| `data/saferoom.db` | SQLite database |
| `logs/saferoom.log` | 개발자용 log file |
| `frontend/dist/` | frontend build output |
| `firmware/pico2w/config.example.py` | Pico 설정 예시 |
| `firmware/pico2w/config.py` | 실제 Pico에 복사할 local 설정 파일 |

`data/`, `logs/`, `frontend/dist/`, `firmware/pico2w/config.py`는 git에 올리지 않습니다.

## Pico 관련 문서

- 기본 펌웨어 안내: [firmware/pico2w/README.md](firmware/pico2w/README.md)
- 실제 센서 배선 안내: [firmware/pico2w/README.real-sensors.md](firmware/pico2w/README.real-sensors.md)
