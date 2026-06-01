# 2nd Project Guide

이 문서는 `raw_2nd_project.md`의 아이디어를 실제 팀 프로젝트 계획서로 바꿀 때 사용할 기준 자료이다. 핵심 방향은 처음부터 최종 플랫폼의 뼈대를 유지하되, 각 단계에서는 구현 깊이만 조절하는 것이다.

## 1. 프로젝트 핵심 정의

### 1.1 목표

Raspberry Pi Pico 2W 기반 IoT 장치에서 센서 데이터를 수집하고, pywebview 데스크톱 대시보드에서 실시간 상태를 확인하며, collector/backend/core/worker/ui가 분리된 micro-architecture를 경험한다.

### 1.2 필수 제약

다음 3가지는 프로젝트 필수 조건으로 고정한다.

1. Raspberry Pi Pico 2W 기반 장치 구현
   - 실제 또는 가상 센서 입력을 Pico 2W 중심으로 설계한다.
   - Wi-Fi, UART, MQTT, HTTP 중 하나 이상으로 외부 시스템과 데이터를 주고받는다.
   - 다른 보드(ESP32, Raspberry Pi, Arduino)는 보조 장치 또는 확장 옵션으로만 사용한다.

2. pywebview 기반 데스크톱 대시보드 구현
   - 사용자 화면은 웹 브라우저 단독 실행이 아니라 pywebview 데스크톱 앱 형태로 제공한다.
   - 프론트엔드는 HTML/CSS/JavaScript 또는 React/Vite/TypeScript 조합을 사용할 수 있다.
   - pywebview는 Python backend와 UI를 묶는 desktop shell 역할을 한다.

3. Micro-architecture 기반 멀티 프로세스 구조
   - 전체 시스템을 단일 프로세스 하나로 만들지 않는다.
   - 최소한 collector, backend, ui는 역할이 분리되어야 한다.
   - core, worker, ai, twin 등은 프로젝트 수준에 따라 mock 또는 실제 프로세스로 확장한다.
   - 프로세스 간 통신은 pipe, TCP localhost, WebSocket, ZeroMQ 중 하나 이상으로 명시한다.

## 2. 기준 아키텍처

처음부터 다음 구조를 기준으로 잡는다. 낮은 단계에서는 일부 모듈이 mock이어도 되지만, 디렉터리와 메시지 흐름은 유지한다.

```text
Pico 2W / Sensor Simulator
        |
        | MQTT / HTTP / Serial / Mock
        v
Device Adapter Layer
        |
        v
Collector Process
        |
        | ZeroMQ / pipe / TCP localhost / in-memory queue
        v
Backend Process (FastAPI)
        |
        | REST API / WebSocket
        v
pywebview Desktop Dashboard

Optional:
Core Process       : C++/Python 고성능 처리, 장치 명령 처리
Worker Process     : 알림, 로그, 배치 분석
AI Process         : RAG, 운영 assistant
Digital Twin Layer : 2D/3D asset map, replay
```

권장 디렉터리 구조:

```text
iot-dashboard/
  apps/
    desktop/
      app.py
    backend/
      main.py
      api/
      services/
      db/
      schemas/
    collector/
      main.py
      adapters/
    core/
      CMakeLists.txt
      src/
    worker/
  frontend/
    package.json
    src/
  shared/
    schemas/
      sensor_event.schema.json
      command.schema.json
  config/
    app.yaml
  data/
  logs/
  scripts/
```

## 3. 공통 데이터 모델

센서가 어떤 프로토콜로 들어오더라도 내부에서는 하나의 표준 이벤트로 변환한다. 이 모델을 초기에 고정하면 MQTT, Serial, Modbus, Matter, Mobius 등을 나중에 붙여도 backend와 dashboard를 다시 만들 필요가 줄어든다.

### 3.1 SensorEvent

```json
{
  "event_id": "uuid",
  "site_id": "factory-a",
  "zone_id": "line-1",
  "asset_id": "pump-01",
  "device_id": "pico-001",
  "sensor_id": "temperature",
  "protocol": "mqtt",
  "value": 26.4,
  "unit": "celsius",
  "timestamp": "2026-06-01T10:00:00+09:00",
  "quality": "good",
  "metadata": {
    "gateway_id": "gateway-01",
    "raw_topic": "factory-a/line-1/pico-001/temperature"
  }
}
```

### 3.2 CommandMessage

```json
{
  "id": "cmd-001",
  "trace_id": "trace-abc",
  "type": "command",
  "source": "dashboard",
  "target": "core",
  "device_id": "pico-001",
  "action": "set_interval",
  "payload": {
    "interval_ms": 1000
  },
  "timestamp": "2026-06-01T10:00:00+09:00"
}
```

### 3.3 상태 모델

시스템 상태:

- `INIT`
- `STARTING`
- `RUNNING`
- `DEGRADED`
- `STOPPING`
- `STOPPED`
- `ERROR`

센서 품질:

- `good`
- `uncertain`
- `bad`
- `stale`
- `missing`

## 4. 필수 구성요소별 역할과 라이브러리

### 4.1 Pico 2W firmware

역할:

- 센서값 읽기
- Wi-Fi 연결
- MQTT 또는 HTTP publish
- 장치 상태 heartbeat 전송

선택 기술:

| 옵션 | 용도 | 라이브러리/도구 |
| --- | --- | --- |
| MicroPython | 교육용, 빠른 구현 | `network`, `machine`, `umqtt.simple`, `urequests` |
| C/C++ Pico SDK | 성능/제어 중심 | Raspberry Pi Pico SDK, `pico_cyw43_arch_lwip_threadsafe_background` |
| CircuitPython | 센서 라이브러리 활용 | `adafruit-circuitpython-*` |

권장 시작점은 MicroPython이다. 수업 프로젝트에서는 구현 속도와 디버깅 난이도가 중요하고, Pico 2W의 Wi-Fi와 센서 입력을 빠르게 검증할 수 있다.

### 4.2 Collector process

역할:

- 프로토콜별 adapter 실행
- 외부 센서 데이터를 `SensorEvent`로 정규화
- backend로 publish
- retry, heartbeat, offline 감지

선택 기술:

| 입력 방식 | 권장 라이브러리 | 비고 |
| --- | --- | --- |
| MQTT | `paho-mqtt`, `gmqtt`, `asyncio-mqtt` | 기본 추천은 `paho-mqtt` |
| Serial/UART | `pyserial` | Pico USB serial, Arduino, 센서 보드 |
| HTTP polling | `httpx`, `aiohttp` | REST 장치 또는 테스트용 |
| Modbus | `pymodbus` | PLC, 계측기 |
| OPC-UA | `asyncua`, `opcua` | 산업 자동화 장치 |
| BLE | `bleak` | 근거리 센서 |
| CAN | `python-can` | 차량/배터리/산업 장치 |
| File/CSV | Python `csv`, `watchdog`, `pandas` | 로그 기반 실습 |

### 4.3 Backend process

역할:

- REST API 제공
- WebSocket 실시간 전송
- DB 저장/조회
- collector/core/worker 프로세스 조율
- schema validation과 에러 응답 표준화

권장 라이브러리:

- API: `FastAPI`
- ASGI server: `uvicorn`
- WebSocket: FastAPI WebSocket, `websockets`
- validation: `pydantic`
- DB ORM: `SQLAlchemy`
- migration: `Alembic`
- settings: `pydantic-settings`, `python-dotenv`
- HTTP client: `httpx`
- test: `pytest`, `pytest-asyncio`, `httpx.AsyncClient`

권장 API:

```text
GET  /api/health
GET  /api/devices
GET  /api/devices/{device_id}
GET  /api/sensors/latest
GET  /api/readings?device_id=&sensor_id=&from=&to=
POST /api/devices/{device_id}/commands
WS   /ws/realtime
```

### 4.4 pywebview desktop app

역할:

- desktop shell 실행
- backend process 시작/종료 관리
- frontend build 파일 로드
- 필요 시 JavaScript-Python bridge 제공

권장 라이브러리:

- Desktop shell: `pywebview`
- Process control: Python `subprocess`, `multiprocessing`
- Packaging: `PyInstaller`, `Nuitka`
- Config: `PyYAML`, `tomli`, `pydantic-settings`

주의:

- pywebview는 UI 렌더링 껍데기이고, business logic은 backend/service 계층에 둔다.
- 개발 중에는 Vite dev server를 띄우고 pywebview가 해당 URL을 열게 할 수 있다.
- 배포 시에는 frontend build 결과물을 pywebview에서 로컬 파일 또는 내장 HTTP server로 제공한다.

### 4.5 Frontend

역할:

- 장치 목록
- 센서 차트
- 실시간 상태
- 알림/로그
- 설정
- 진단 화면
- optional: AI chat, 2D/3D twin viewer

권장 라이브러리:

| 영역 | 옵션 |
| --- | --- |
| Framework | `React`, `Vue`, `Svelte` |
| Build | `Vite` |
| Language | `TypeScript` |
| Chart | `Apache ECharts`, `Chart.js`, `Recharts`, `uPlot` |
| State | `Zustand`, `TanStack Query`, `Pinia` |
| UI | `Tailwind CSS`, `shadcn/ui`, `Radix UI`, `Mantine`, `MUI` |
| Realtime | browser `WebSocket`, `socket.io-client` |
| 2D map | `Konva`, `PixiJS`, SVG |
| 3D twin | `Three.js`, `React Three Fiber`, Unity WebGL |

수업 프로젝트의 기본 조합은 `React + Vite + TypeScript + ECharts + WebSocket`을 추천한다.

### 4.6 Database

역할:

- device registry
- sensor registry
- sensor reading 저장
- protocol message 저장
- system log 저장
- user/settings 저장

선택지:

| 목적 | DB | Python 라이브러리 |
| --- | --- | --- |
| 빠른 MVP/로컬 실습 | SQLite | Python `sqlite3`, `SQLAlchemy`, `aiosqlite` |
| 일반 운영 DB | PostgreSQL | `psycopg`, `asyncpg`, `SQLAlchemy` |
| 시계열 데이터 | TimescaleDB | PostgreSQL driver + TimescaleDB hypertable |
| 시계열/대시보드 특화 | InfluxDB | `influxdb-client`, `influxdb3-python` |
| 캐시/상태/pub-sub | Redis | `redis-py` |

권장 테이블:

```text
sites
zones
assets
devices
sensors
sensor_readings
device_status
device_protocols
device_adapters
protocol_messages
commands
command_results
alerts
system_logs
users
roles
permissions
audit_logs
```

## 5. 프로세스 간 통신 옵션

| 옵션 | 장점 | 단점 | 권장 사용 단계 |
| --- | --- | --- | --- |
| Python `queue.Queue` / `asyncio.Queue` | 가장 단순 | 단일 프로세스 중심 | Level 1 |
| `multiprocessing.Queue` | Python 프로세스 분리 쉬움 | Python 내부에 묶임 | Level 2 |
| stdin/stdout pipe | C++ core 연동 쉬움 | 메시지 framing 필요 | Level 3 |
| TCP localhost | 언어 독립적 | 포트 관리 필요 | Level 3-4 |
| ZeroMQ / `pyzmq` | PUB/SUB, PUSH/PULL 패턴에 강함 | 패턴 설계 필요 | Level 5-6 |
| Redis Pub/Sub | 상태 공유와 pub/sub 가능 | Redis 의존성 | Level 6+ |
| NATS | 경량 메시징, 확장성 | 별도 broker 필요 | Level 7+ |
| RabbitMQ | 안정적 queue, routing | 운영 복잡도 | Level 7+ |
| Kafka/Redpanda | 대용량 event streaming | 수업 프로젝트에는 과함 | Level 9+ |

기본 추천:

- MVP: `asyncio.Queue` 또는 `multiprocessing.Queue`
- 멀티 프로세스 학습: `pyzmq`
- C++ core 연동: stdin/stdout JSON line 또는 TCP localhost

## 6. 프로토콜 확장 옵션

### 6.1 MQTT

용도:

- IoT 센서 publish/subscribe 기본 프로토콜
- Pico 2W와 collector 간 데이터 수집
- broker를 사이에 두고 여러 sensor/device를 쉽게 연결

권장 라이브러리/도구:

- Broker: `Eclipse Mosquitto`, `EMQX`, `HiveMQ CE`, `RabbitMQ MQTT plugin`
- Python client: `paho-mqtt`, `gmqtt`, `asyncio-mqtt`
- Pico MicroPython: `umqtt.simple`, `umqtt.robust`

권장 topic:

```text
sites/{site_id}/zones/{zone_id}/devices/{device_id}/sensors/{sensor_id}/reading
sites/{site_id}/devices/{device_id}/status
sites/{site_id}/devices/{device_id}/commands
```

### 6.2 Matter

Matter는 raw sensor stream의 기본 수집 프로토콜이라기보다, 상용 스마트홈/상용 IoT 장치를 플랫폼에 연결하는 integration layer로 보는 것이 적절하다.

연동 위치:

```text
Matter Device
  -> Matter Controller / Bridge
  -> Matter Adapter
  -> SensorEvent
  -> Collector Gateway
```

선택 라이브러리/도구:

- `matter.js`
- `CHIP SDK` / `connectedhomeip`
- `chip-tool`
- Home Assistant Matter Server
- Matter to MQTT bridge

권장 접근:

1. 직접 Matter stack을 처음부터 구현하지 않는다.
2. Home Assistant 또는 matter.js 기반 controller를 사용한다.
3. 내부 시스템으로는 MQTT/REST/WebSocket 중 하나로 변환한 뒤 `SensorEvent`로 정규화한다.

### 6.3 Mobius / oneM2M

Mobius는 oneM2M 기반 IoT 플랫폼 연동 옵션이다. 공공/표준 IoT 플랫폼과 연결하는 확장 단계에서 사용한다.

연동 위치:

```text
oneM2M Device / TAS
  -> Mobius Server
  -> Subscription / Notification / REST API
  -> Mobius Adapter
  -> SensorEvent
```

검토 항목:

- AE, container, contentInstance 구조를 내부 `site/asset/device/sensor` 모델로 매핑한다.
- Mobius notification을 collector 입력으로 받아 정규화한다.
- oneM2M resource id와 내부 device id의 매핑 테이블을 둔다.

선택 라이브러리/도구:

- HTTP client: `httpx`, `requests`
- Schema validation: `pydantic`
- Mobius server, KETI TAS
- oneM2M resource model 문서

### 6.4 산업용 프로토콜

| 프로토콜 | 적용 대상 | 라이브러리 |
| --- | --- | --- |
| Modbus TCP/RTU | PLC, 전력량계, 산업 센서 | `pymodbus` |
| OPC-UA | PLC/SCADA/산업 자동화 표준 | `asyncua`, `opcua`, `node-opcua` |
| Serial | 교육용 센서, 간단 장치 | `pyserial` |
| BLE | 근거리 센서, beacon | `bleak` |
| CAN | 차량, 배터리, 산업 장치 | `python-can` |
| LoRaWAN | 저전력 장거리 센서 | The Things Stack MQTT API, `paho-mqtt` |

## 7. 단계별 구현 로드맵

중요한 원칙은 "단계별로 구조를 갈아엎지 않는다"는 것이다. 각 레벨은 같은 구조를 유지하고, adapter와 서비스의 구현 깊이만 높인다.

### Level 1. Architecture Skeleton

목표:

- 최종 구조의 디렉터리와 프로세스 경계를 만든다.
- mock sensor event가 dashboard까지 흐른다.

구현:

- Collector: `random.uniform()`으로 mock sensor 생성
- Backend: FastAPI `/api/health`, `/api/sensors/latest`
- Frontend: pywebview에서 단일 dashboard 화면 표시
- DB: SQLite 또는 메모리 저장
- Auth/AI/Twin: placeholder

산출물:

- 실행 가능한 desktop app
- mock sensor chart
- architecture diagram

### Level 2. Data Persistence

목표:

- 센서 데이터와 장치 metadata를 저장한다.

구현:

- SQLite + SQLAlchemy
- `devices`, `sensors`, `sensor_readings` 테이블
- Alembic migration
- CSV export/import 옵션

산출물:

- device list
- historical readings API
- DB schema 문서

### Level 3. Pico 2W Sensor Integration

목표:

- Pico 2W에서 실제 또는 가상 센서값을 전송한다.

구현:

- MicroPython firmware
- MQTT 또는 HTTP publish
- collector adapter에서 `SensorEvent` 변환
- 장치 heartbeat

라이브러리:

- Pico: `umqtt.simple`, `network`, `machine`
- Collector: `paho-mqtt` 또는 `httpx`
- Broker: `Eclipse Mosquitto`

산출물:

- Pico 2W 데이터 수집 demo
- topic/API 명세

### Level 4. Realtime Dashboard

목표:

- backend가 WebSocket으로 최신 데이터를 UI에 push한다.

구현:

- FastAPI WebSocket endpoint
- frontend WebSocket client
- 실시간 chart, status panel, log panel
- 연결 끊김/reconnect 표시

라이브러리:

- `FastAPI`, `websockets`
- `ECharts`, browser `WebSocket`

산출물:

- 실시간 대시보드
- offline/degraded 상태 표시

### Level 5. Multi-process Runtime

목표:

- collector와 backend를 실제 별도 프로세스로 분리한다.

구현:

- `subprocess` 또는 `multiprocessing`
- ZeroMQ PUB/SUB 또는 TCP localhost
- process heartbeat
- graceful shutdown

라이브러리:

- `pyzmq`
- Python `multiprocessing`, `subprocess`, `signal`
- logging: `structlog`, `loguru`, Python `logging`

산출물:

- 프로세스 상태 화면
- 장애 재현 및 복구 demo

### Level 6. Protocol Adapter Expansion

목표:

- 하나 이상의 추가 프로토콜을 adapter로 붙인다.

선택:

- Serial: `pyserial`
- Modbus: `pymodbus`
- OPC-UA: `asyncua`
- BLE: `bleak`
- CAN: `python-can`

산출물:

- `SensorAdapter` interface
- protocol별 adapter 문서

### Level 7. Auth, RBAC, Audit

목표:

- 다중 사용자 운영 구조를 준비한다.

구현:

- mock login 또는 JWT login
- role: Admin, Operator, Engineer, Viewer
- command 실행 권한 체크
- audit log 저장

라이브러리:

- `python-jose`, `PyJWT`
- `passlib`, `bcrypt`
- `Authlib`
- OAuth 옵션: Google OAuth, GitHub OAuth

산출물:

- 권한별 화면/명령 제한
- audit log table

### Level 8. Operations Portal

목표:

- 단순 모니터링을 넘어 운영 업무 기능을 추가한다.

구현:

- alarm acknowledgement
- 작업 메모/게시판
- 첨부 파일
- notification
- scheduler/worker

라이브러리:

- Worker: `Celery`, `RQ`, `APScheduler`, `arq`
- Notification: SMTP, Slack webhook, Discord webhook
- File: FastAPI `UploadFile`

산출물:

- alarm workflow
- operations log

### Level 9. AI Assistant

목표:

- 운영 문서와 센서 이력을 바탕으로 질의응답/요약을 제공한다.

구현:

- chat UI
- RAG pipeline
- sensor anomaly summary
- manual/document search

라이브러리:

- LLM API: OpenAI API
- RAG: `LlamaIndex`, `LangChain`
- Vector DB: `pgvector`, `Chroma`, `Qdrant`, `FAISS`
- Embedding storage: PostgreSQL + `pgvector`
- Document parsing: `pypdf`, `python-docx`, `unstructured`

산출물:

- "Pump-01 최근 경고 원인 분석"
- "지난 24시간 이상 상태 요약"
- "장치별 점검 절차 검색"

### Level 10. Digital Twin Platform

목표:

- 장치/센서/asset을 2D 또는 3D 공간에 매핑한다.

구현:

- asset hierarchy
- 2D facility map 또는 3D viewer
- 실시간 상태 색상 표시
- timeline replay

라이브러리:

- 2D: SVG, `Konva`, `PixiJS`
- 3D web: `Three.js`, `React Three Fiber`
- Game engine: Unity, Unreal
- Timeline: `ECharts`, `vis-timeline`

산출물:

- asset map
- sensor 상태 연동
- historical replay

## 8. Adapter Interface 기준

모든 프로토콜 adapter는 같은 interface를 따른다.

```python
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

class SensorAdapter(ABC):
    @abstractmethod
    async def connect(self) -> None:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def subscribe(self) -> AsyncIterator["SensorEvent"]:
        ...
```

Pydantic schema 예시:

```python
from datetime import datetime
from pydantic import BaseModel, Field

class SensorEvent(BaseModel):
    event_id: str
    site_id: str
    zone_id: str | None = None
    asset_id: str | None = None
    device_id: str
    sensor_id: str
    protocol: str
    value: float | int | str | bool
    unit: str | None = None
    timestamp: datetime
    quality: str = Field(default="good")
    metadata: dict = Field(default_factory=dict)
```

## 9. 에러 처리와 로깅 기준

공통 에러 응답:

```json
{
  "error": {
    "code": "CORE_TIMEOUT",
    "message": "Core process response timeout",
    "detail": {},
    "recoverable": true,
    "trace_id": "trace-abc"
  }
}
```

권장 에러 코드:

- `DEVICE_OFFLINE`
- `SENSOR_STALE`
- `INVALID_SENSOR_EVENT`
- `CORE_TIMEOUT`
- `DB_CONNECTION_ERROR`
- `INVALID_COMMAND`
- `IPC_BROKEN_PIPE`
- `WS_DISCONNECTED`
- `CONFIG_ERROR`
- `AUTH_REQUIRED`
- `PERMISSION_DENIED`

로그 기준:

- 로그는 JSON line 형태를 우선한다.
- 모든 request/event/command에 `trace_id`를 붙인다.
- UI용 event log와 개발자용 file log를 분리한다.
- 민감 정보(token, password, OAuth code)는 저장하지 않는다.

권장 라이브러리:

- Python 기본 `logging`
- `structlog`
- `loguru`
- OpenTelemetry 옵션: `opentelemetry-sdk`, `opentelemetry-instrumentation-fastapi`

## 10. 보안과 운영 기준

MVP에서도 다음 기준은 문서화한다.

- local backend port는 `127.0.0.1`에 bind한다.
- command API는 allowlist를 둔다.
- 장치 명령은 role/permission을 확인한다.
- config 파일에 secret을 직접 commit하지 않는다.
- `.env` 또는 OS keyring을 사용한다.
- 로그에 token, password, 개인 정보, API key를 남기지 않는다.
- 배포 패키지는 실행 파일, config template, migration, sample data를 분리한다.

권장 라이브러리:

- Secret/config: `python-dotenv`, `pydantic-settings`, `keyring`
- Auth: `PyJWT`, `python-jose`, `Authlib`
- Password: `passlib`, `bcrypt`
- Packaging: `PyInstaller`, `Nuitka`

## 11. 팀 역할 분리 예시

10명 내외 팀 기준:

| 역할 | 인원 | 책임 |
| --- | --- | --- |
| PM/Architect | 1 | 요구사항, 일정, architecture decision |
| IoT/Device | 2 | Pico firmware, MQTT/HTTP/Serial |
| Backend | 2-3 | FastAPI, DB, WebSocket, process manager |
| Frontend | 2 | pywebview dashboard, chart, UX |
| Data/AI | 1-2 | sensor analytics, RAG, anomaly summary |
| Twin/Visualization | 1 | 2D/3D asset map |
| QA/DevOps | 1 | packaging, test, logging, release |

소규모 팀이면 AI/Twin은 placeholder로 두고, Pico + collector + backend + dashboard의 완성도를 우선한다.

## 12. 프로젝트 계획서 작성 체크리스트

계획서를 만들 때 다음 질문에 답해야 한다.

1. 필수 조건 3가지(Pico 2W, pywebview, multi-process)를 어떻게 만족하는가?
2. 센서 입력은 mock, Pico, MQTT, Serial, Modbus 중 어디까지 구현하는가?
3. 내부 표준 메시지 `SensorEvent` schema는 무엇인가?
4. collector와 backend는 어떤 IPC로 연결되는가?
5. DB는 SQLite/PostgreSQL/TimescaleDB/InfluxDB 중 무엇을 쓰는가?
6. dashboard에서 보여줄 핵심 화면은 무엇인가?
7. 실시간성은 polling, WebSocket, MQTT bridge 중 무엇으로 구현하는가?
8. 에러/로그/장치 offline은 어떻게 표시하는가?
9. 팀원별 담당 모듈과 산출물은 무엇인가?
10. 최종 발표 demo scenario는 무엇인가?

## 13. 추천 기본 스택

수업 프로젝트 기본 추천:

```text
Pico firmware : MicroPython
Sensor protocol: MQTT
MQTT broker    : Eclipse Mosquitto
Collector      : Python + paho-mqtt + pydantic
IPC            : pyzmq 또는 multiprocessing.Queue
Backend        : FastAPI + uvicorn + SQLAlchemy + Alembic
DB             : SQLite -> PostgreSQL/TimescaleDB 확장
Realtime       : FastAPI WebSocket
Desktop        : pywebview
Frontend       : React + Vite + TypeScript + ECharts
Packaging      : PyInstaller
Logging        : structlog 또는 logging
Testing        : pytest + pytest-asyncio
```

확장 스택:

```text
Industrial     : pymodbus, asyncua, pyserial, bleak, python-can
Queue/Broker   : ZeroMQ, Redis, NATS, RabbitMQ
AI             : OpenAI API, LlamaIndex, LangChain, pgvector, Chroma, Qdrant
Digital Twin   : Three.js, React Three Fiber, Unity, Unreal
Monitoring     : OpenTelemetry, Prometheus, Grafana
```

## 14. 검증된 참고 자료

아래 자료를 기준으로 라이브러리와 기술 옵션 이름을 확인했다.

- pywebview 공식 문서: https://pywebview.flowrl.com/guide/
- FastAPI WebSocket 공식 문서: https://fastapi.tiangolo.com/advanced/websockets/
- Eclipse Mosquitto 공식 문서: https://mosquitto.org/documentation/
- Eclipse Paho MQTT Python client 문서: https://eclipse.dev/paho/files/paho.mqtt.python/html/index.html
- SQLAlchemy 2.0 공식 문서: https://docs.sqlalchemy.org/20/
- Pydantic 공식 문서: https://pydantic.dev/
- ZeroMQ 공식 문서: https://zeromq.org/get-started/
- TimescaleDB hypertable 문서: https://docs.timescale.com/use-timescale/latest/hypertables/
- InfluxDB Python client 문서: https://docs.influxdata.com/influxdb/v2/api-guide/client-libraries/python/
- matter.js project: https://github.com/matter-js/matter.js

## 15. 최종 정리

이 프로젝트는 기능을 하나씩 덧붙이는 방식보다, 처음부터 최종 플랫폼 구조를 작게 만들어 놓고 각 단계에서 구현 깊이를 높이는 방식이 적합하다. Level 1에서도 collector/backend/frontend/database/auth/ai/twin의 위치는 존재해야 한다. 다만 Level 1에서는 대부분 mock이고, Level 10으로 갈수록 실제 adapter, 실제 DB, 실제 권한, 실제 AI, 실제 twin으로 대체된다.

최소 성공 기준은 다음과 같다.

1. Pico 2W 또는 mock sensor에서 데이터가 발생한다.
2. Collector가 데이터를 표준 `SensorEvent`로 정규화한다.
3. Backend가 데이터를 저장하고 API/WebSocket으로 제공한다.
4. pywebview dashboard가 실시간 상태를 표시한다.
5. 프로세스 경계와 메시지 schema가 문서화되어 있다.

확장 성공 기준은 다음과 같다.

1. MQTT 외에 하나 이상의 adapter를 추가한다.
2. ZeroMQ 또는 TCP 기반 IPC로 collector/backend를 분리한다.
3. 장치 offline, error, retry, heartbeat를 처리한다.
4. 권한, audit log, 운영 화면을 붙인다.
5. AI assistant 또는 digital twin 중 하나를 실제 demo 수준으로 구현한다.