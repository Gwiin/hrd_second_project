# Pico SafeRoom 설치 및 실행 안내

이 문서는 로컬 개발 환경을 만들고 backend, dashboard, MQTT collector, desktop launcher를 실행하기 위한 안내입니다.

## 현재 포함된 기능

- FastAPI backend
- SQLite 저장소
- React/Vite dashboard
- pywebview desktop launcher
- 4개 Pico 2W 장치 ID 등록
- MQTT reading collector
- device heartbeat / process heartbeat
- threshold alert / stale sensor alert
- email 회원가입 및 로그인
- Google / Kakao social login callback 경로
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

PowerShell에서 `npm.ps1` 실행이 막혀 있으면 `npm.cmd`를 사용합니다.

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

## Backend와 Dashboard 실행

먼저 frontend를 build합니다.

macOS/Linux:

```bash
npm --prefix frontend run build
```

Windows PowerShell:

```powershell
npm.cmd --prefix frontend run build
```

Backend 실행:

macOS/Linux:

```bash
.venv/bin/python -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
```

브라우저에서 열기:

```text
http://127.0.0.1:8000
```

## 로그인 설정

일반 회원가입과 로그인은 email/password로 바로 사용할 수 있습니다. 비밀번호는 SQLite에 plain text로 저장하지 않고 hash로 저장합니다.

Google, Kakao social login은 각 provider console에서 client ID/secret과 redirect URL을 발급받아 환경변수로 넣습니다. 로컬 개발 기준 redirect URL은 아래 값을 등록합니다.

```text
http://127.0.0.1:8000/api/auth/social/google/callback
http://127.0.0.1:8000/api/auth/social/kakao/callback
```

프로젝트 루트에 `.env` 파일을 만들고 아래 형식으로 값을 넣습니다.

```dotenv
PICO_AUTH_REDIRECT_BASE_URL="http://127.0.0.1:8000"
PICO_AUTH_GOOGLE_CLIENT_ID="your-google-client-id"
PICO_AUTH_GOOGLE_CLIENT_SECRET="your-google-client-secret"
PICO_AUTH_KAKAO_CLIENT_ID="your-kakao-client-id"
PICO_AUTH_KAKAO_CLIENT_SECRET="your-kakao-client-secret"
```

실제 secret 값은 git에 올리지 않습니다. `.env`는 `.gitignore`에 포함되어 있고, 공유용 예시는 `.env.example`을 사용합니다.

## MQTT Collector 실행

실제 Pico 2W를 사용할 때는 로컬 MQTT broker를 먼저 실행해야 합니다.

macOS/Linux:

```bash
.venv/bin/python -m apps.collector.mqtt_client --broker-host 127.0.0.1 --broker-port 1883 --backend-url http://127.0.0.1:8000
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.collector.mqtt_client --broker-host 127.0.0.1 --broker-port 1883 --backend-url http://127.0.0.1:8000
```

Collector가 구독하는 topic:

```text
saferoom/+/+/sensors/+/reading
saferoom/+/+/status
```

Reading topic은 `/internal/events`로 전달하고, heartbeat topic은 `/internal/heartbeats/device`로 전달합니다.

## Desktop Launcher 실행

기본 실행은 실제 Pico 2W + MQTT collector 모드입니다. Simulator는 자동으로 실행하지 않습니다.

pywebview로 열기:

macOS/Linux:

```bash
.venv/bin/python -m apps.desktop.app
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.desktop.app
```

브라우저로 열기:

macOS/Linux:

```bash
.venv/bin/python -m apps.desktop.app --open browser
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.desktop.app --open browser
```

Launcher는 backend, MQTT collector, worker를 별도 process로 시작합니다. GUI 환경이면 pywebview 창이 열리고, `--open browser`를 사용하면 같은 dashboard를 브라우저에서 엽니다.

## Simulator 실행

Simulator는 개발/테스트 전용이며 실제 Pico 2W 실행 경로와 분리되어 있습니다. 실제 보드 발표나 데모에서는 실행하지 않습니다.

macOS/Linux:

```bash
.venv/bin/python -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
```

## Runtime 파일

| 파일/폴더 | 설명 |
| --- | --- |
| `data/saferoom.db` | SQLite database |
| `logs/saferoom.log` | 개발용 log file |
| `frontend/dist/` | frontend build output |
| `firmware/pico2w/config.py` | 실제 Pico에 복사할 local 설정 파일 |

`data/`, `logs/`, `frontend/dist/`, `.env`, `firmware/pico2w/config.py`는 git에 올리지 않습니다.

## Pico 관련 문서

- 기본 펌웨어 안내: [firmware/pico2w/README.md](firmware/pico2w/README.md)
- 실제 센서 배선 안내: [firmware/pico2w/README.real-sensors.md](firmware/pico2w/README.real-sensors.md)
