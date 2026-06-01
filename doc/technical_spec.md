# 스마트 실내 환경 안전 관제 시스템 기술서

## 1. 기술 개요

본 시스템은 Raspberry Pi Pico 2W 센서 노드, MQTT collector, FastAPI backend, worker process, pywebview dashboard로 구성된다. 목표는 실내 환경 안전 데이터를 실시간으로 수집, 저장, 분석, 표시하는 것이다.

핵심 구조는 다음과 같다.

```text
Pico 2W
  -> MQTT Broker
  -> Collector Process
  -> Backend Process
  -> SQLite
  -> Worker Process
  -> WebSocket
  -> pywebview UI
```

## 2. 프로세스 구성

| Process | 책임 | 주요 기술 |
| --- | --- | --- |
| `collector` | MQTT subscribe, payload validation, SensorEvent 생성 | Python, paho-mqtt, Pydantic |
| `backend` | REST API, WebSocket, DB 저장/조회 | FastAPI, Uvicorn, SQLAlchemy |
| `worker` | alert rule, heartbeat timeout, stale data 검사 | Python multiprocessing |
| `ui` | pywebview desktop shell, dashboard 표시 | pywebview, React/Vite |
| `broker` | MQTT message broker | Eclipse Mosquitto |
| `simulator` | Pico 없이 테스트 데이터 생성 | Python script |

최소 구현에서는 `collector`, `backend`, `ui`를 반드시 분리한다. `worker`는 MVP에서도 별도 process로 두는 것을 추천한다. 그래야 micro-architecture 요구사항을 더 명확히 만족한다.

## 3. 통신 구조

### 3.1 Pico 2W -> MQTT broker

Pico 2W는 센서값과 heartbeat를 MQTT topic으로 publish한다.

```text
saferoom/{zone_id}/{device_id}/sensors/{sensor_id}/reading
saferoom/{zone_id}/{device_id}/status
```

예시:

```text
saferoom/room-1/pico-safe-001/sensors/gas/reading
saferoom/room-1/pico-safe-001/status
```

### 3.2 Collector -> Backend

MVP에서는 backend 내부 HTTP ingest API를 사용한다.

```text
POST /internal/events
```

확장 단계에서는 ZeroMQ PUB/SUB 또는 TCP localhost JSON line으로 변경할 수 있다.

### 3.3 Backend -> UI

Backend는 REST API와 WebSocket을 제공한다.

```text
GET /api/health
GET /api/devices
GET /api/zones
GET /api/readings/latest
GET /api/alerts
GET /api/logs
WS  /ws/realtime
```

pywebview는 `http://127.0.0.1:{port}` 또는 build된 frontend 파일을 로드한다.

## 4. Pico 2W firmware

### 4.1 권장 구현

Pico 2W firmware는 MicroPython으로 구현한다.

사용 모듈:

- `network`: Wi-Fi 연결
- `machine`: GPIO/ADC 센서 입력
- `time`: 주기 처리
- `json`: payload 생성
- `umqtt.simple`: MQTT publish

### 4.2 센서 구성

| Sensor | 목적 | 예시 값 | Unit |
| --- | --- | --- | --- |
| temperature | 과열/화재 위험 감지 | `28.5` | `celsius` |
| humidity | 실내 환경 상태 | `52.0` | `%` |
| light | 조도 상태 | `430` | `lux` |
| motion | 움직임 감지 | `true` | `bool` |
| gas | 가스/연기 위험 감지 | `320` | `ppm` |

실제 센서가 없는 경우 Pico에서 가상값을 생성한다. 단, payload schema는 실제 센서와 동일하게 유지한다.

### 4.3 MQTT payload

```json
{
  "device_id": "pico-safe-001",
  "zone_id": "room-1",
  "sensor_id": "gas",
  "value": 320,
  "unit": "ppm",
  "timestamp": "2026-06-01T10:00:00+09:00",
  "seq": 1024
}
```

Heartbeat payload:

```json
{
  "device_id": "pico-safe-001",
  "zone_id": "room-1",
  "status": "online",
  "timestamp": "2026-06-01T10:00:00+09:00",
  "uptime_ms": 123000
}
```

## 5. SensorEvent schema

Collector는 모든 입력을 다음 내부 schema로 정규화한다.

```json
{
  "event_id": "uuid",
  "site_id": "safe-room-lab",
  "zone_id": "room-1",
  "device_id": "pico-safe-001",
  "sensor_id": "gas",
  "protocol": "mqtt",
  "value": 320,
  "unit": "ppm",
  "timestamp": "2026-06-01T10:00:00+09:00",
  "quality": "good",
  "trace_id": "trace-uuid",
  "metadata": {
    "topic": "saferoom/room-1/pico-safe-001/sensors/gas/reading",
    "seq": 1024
  }
}
```

`quality` 값:

| 값 | 의미 |
| --- | --- |
| `good` | 정상 데이터 |
| `uncertain` | 값은 수신했지만 검증이 불충분함 |
| `bad` | 범위 또는 형식 오류 |
| `stale` | 오래된 timestamp |
| `missing` | 일정 시간 데이터 없음 |

## 6. Database 설계

MVP는 SQLite를 사용한다.

### 6.1 주요 테이블

| Table | 설명 |
| --- | --- |
| `sites` | 설치 장소 |
| `zones` | 방/구역 |
| `devices` | Pico 2W 장치 registry |
| `sensors` | 센서 metadata |
| `sensor_readings` | 센서 측정값 이력 |
| `device_status` | 장치 online/offline/heartbeat |
| `alerts` | 경고 이력 |
| `system_logs` | 시스템 로그 |
| `process_heartbeats` | collector/backend/worker 상태 |

### 6.2 schema 초안

```sql
CREATE TABLE devices (
  device_id TEXT PRIMARY KEY,
  zone_id TEXT NOT NULL,
  device_name TEXT NOT NULL,
  protocol TEXT NOT NULL DEFAULT 'mqtt',
  enabled INTEGER NOT NULL DEFAULT 1,
  last_seen_at TEXT
);

CREATE TABLE sensors (
  sensor_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  sensor_name TEXT NOT NULL,
  unit TEXT,
  min_value REAL,
  max_value REAL,
  PRIMARY KEY (device_id, sensor_id)
);

CREATE TABLE sensor_readings (
  reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL UNIQUE,
  zone_id TEXT NOT NULL,
  device_id TEXT NOT NULL,
  sensor_id TEXT NOT NULL,
  value REAL NOT NULL,
  unit TEXT,
  quality TEXT NOT NULL,
  measured_at TEXT NOT NULL,
  received_at TEXT NOT NULL
);

CREATE TABLE alerts (
  alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
  level TEXT NOT NULL,
  code TEXT NOT NULL,
  message TEXT NOT NULL,
  zone_id TEXT,
  device_id TEXT,
  sensor_id TEXT,
  value REAL,
  status TEXT NOT NULL DEFAULT 'open',
  created_at TEXT NOT NULL,
  resolved_at TEXT
);
```

## 7. Backend API

### 7.1 Public API

| Method | Path | 설명 |
| --- | --- | --- |
| `GET` | `/api/health` | backend, DB, process 상태 |
| `GET` | `/api/devices` | 장치 목록 |
| `GET` | `/api/zones` | 구역별 상태 |
| `GET` | `/api/readings/latest` | 최신 센서값 |
| `GET` | `/api/readings/history` | 기간별 센서 이력 |
| `GET` | `/api/alerts` | 경고 목록 |
| `POST` | `/api/alerts/{alert_id}/ack` | 경고 확인 처리 |
| `GET` | `/api/logs` | 시스템 로그 |

### 7.2 Internal API

| Method | Path | 설명 |
| --- | --- | --- |
| `POST` | `/internal/events` | collector가 SensorEvent를 전달 |
| `POST` | `/internal/heartbeats/device` | 장치 heartbeat 전달 |
| `POST` | `/internal/heartbeats/process` | 프로세스 heartbeat 전달 |

### 7.3 WebSocket events

| Event | 설명 |
| --- | --- |
| `reading.created` | 새 센서값 |
| `alert.created` | 새 경고 |
| `alert.updated` | 경고 확인/해제 |
| `device.online` | 장치 online |
| `device.offline` | 장치 offline |
| `process.heartbeat` | 프로세스 상태 |
| `system.log` | UI 표시용 로그 |

## 8. Worker rule

Worker는 주기적으로 DB 또는 backend service에서 최신 상태를 읽어 경고를 판단한다.

### 8.1 기본 임계값

| Rule | 조건 | Alert level |
| --- | --- | --- |
| high temperature | temperature >= 45 | `warning` |
| critical temperature | temperature >= 60 | `critical` |
| high gas | gas >= 300 | `warning` |
| critical gas | gas >= 600 | `critical` |
| motion at restricted time | motion == true and restricted_time | `warning` |
| device offline | last_seen_at > 15초 | `warning` |
| sensor stale | latest reading > 30초 | `info` |

임계값은 `config/app.yaml` 또는 DB settings로 분리한다.

## 9. pywebview Dashboard

### 9.1 화면 구성

- 상단: 전체 안전 상태, 현재 시간, process status
- 좌측: zone/device list
- 중앙: 최신 센서 카드와 차트
- 우측: alert panel
- 하단: system log panel
- 설정: MQTT broker, threshold, device registry

### 9.2 UI 상태

| 상태 | 표시 |
| --- | --- |
| 정상 | green |
| 주의 | yellow |
| 위험 | red |
| offline | gray |
| backend disconnected | top bar warning |

## 10. Launcher 동작

`apps/desktop/app.py`가 전체 실행을 관리한다.

1. 설정 파일을 읽는다.
2. Mosquitto 실행 여부를 확인한다. MVP에서는 외부 실행을 전제로 하고, simulator fallback을 제공한다.
3. backend process를 시작한다.
4. collector process를 시작한다.
5. worker process를 시작한다.
6. backend `/api/health`가 정상 응답하면 pywebview window를 연다.
7. 앱 종료 시 child process를 정리한다.

## 11. 디렉터리 구조 제안

```text
hrd_second_project/
  apps/
    desktop/
      app.py
    backend/
      main.py
      api/
      services/
      repositories/
      db/
    collector/
      main.py
      adapters/
        mqtt_adapter.py
    worker/
      main.py
      rules.py
  frontend/
    package.json
    src/
  firmware/
    micropython/
      main.py
      config.example.py
  shared/
    schemas/
      sensor_event.py
  config/
    app.example.yaml
  data/
  logs/
  scripts/
    simulate_sensor.py
  doc/
    2nd_project.md
    project_plan.md
    technical_spec.md
```

## 12. 에러 처리

공통 에러 포맷:

```json
{
  "error": {
    "code": "INVALID_SENSOR_EVENT",
    "message": "Sensor payload validation failed",
    "detail": {
      "device_id": "pico-safe-001"
    },
    "recoverable": true,
    "trace_id": "trace-uuid"
  }
}
```

주요 에러 코드:

- `MQTT_CONNECT_FAILED`
- `INVALID_SENSOR_EVENT`
- `UNKNOWN_DEVICE`
- `DEVICE_OFFLINE`
- `SENSOR_STALE`
- `DB_WRITE_FAILED`
- `WORKER_RULE_FAILED`
- `WS_DISCONNECTED`
- `CONFIG_ERROR`

## 13. 보안 기준

- backend는 기본적으로 `127.0.0.1`에 bind한다.
- MQTT broker는 로컬 또는 같은 실습망에서만 접근하도록 제한한다.
- Wi-Fi 비밀번호와 broker 인증 정보는 repository에 commit하지 않는다.
- `.env`, `config.local.yaml`은 `.gitignore`에 포함한다.
- 로그에 password, token, 개인 정보를 남기지 않는다.
- 장치 제어 명령은 MVP에서는 비활성화하고, 확장 시 allowlist를 둔다.

## 14. 테스트 계획

### 14.1 단위 테스트

- MQTT payload parser
- SensorEvent schema validation
- threshold rule
- heartbeat timeout rule
- DB repository

### 14.2 통합 테스트

- simulator -> MQTT broker -> collector -> backend -> SQLite
- backend REST API 조회
- WebSocket event 수신
- worker alert 생성

### 14.3 수동 시연 테스트

- 정상 센서값 송신
- gas warning 발생
- gas critical 발생
- Pico heartbeat 중단 후 offline 표시
- invalid payload 송신 후 system log 확인

## 15. 확장 기술 검토

| 확장 | 도입 조건 | 구현 방향 |
| --- | --- | --- |
| ZeroMQ | 프로세스 간 event bus를 더 명확히 보여주고 싶을 때 | collector가 PUB, backend/worker가 SUB |
| PostgreSQL/TimescaleDB | 장기 이력/대량 데이터가 필요할 때 | SQLite repository interface 유지 후 DB 교체 |
| Matter | 상용 스마트홈 센서와 연동할 때 | Matter bridge -> MQTT/REST -> SensorEvent |
| Mobius/oneM2M | 표준 IoT 플랫폼 연계가 목표일 때 | Mobius notification adapter 추가 |
| C++ core | 고속 필터링 또는 제어 명령이 필요할 때 | stdin/stdout JSON line 또는 TCP localhost |
| RTOS | Pico 센서 주기/제어 주기가 엄격할 때 | MicroPython 이후 FreeRTOS 기반 firmware로 확장 |

## 16. 구현 우선순위

1. simulator와 dashboard mock으로 end-to-end 흐름을 먼저 만든다.
2. SQLite schema와 FastAPI API를 작성한다.
3. MQTT collector를 붙인다.
4. Pico 2W MicroPython firmware를 붙인다.
5. WebSocket 실시간 갱신을 추가한다.
6. worker alert와 heartbeat를 완성한다.
7. 로그, 테스트, 발표 시나리오를 정리한다.

## 17. 완료 기준

- `collector`, `backend`, `worker`, `ui`가 분리되어 실행된다.
- Pico 2W 또는 simulator 데이터가 dashboard까지 표시된다.
- SQLite에 센서값과 경고가 저장된다.
- WebSocket으로 최신 상태가 갱신된다.
- 위험 조건에서 alert가 생성된다.
- device offline 상태가 감지된다.
- README 또는 발표 문서에 실행 순서와 시연 방법이 정리된다.
