# 2차 프로젝트 기술서

## 1. 시스템 개요

본 시스템은 Raspberry Pi Pico 2W 기반 홈 IoT 장치에서 발생하는 센서/액추에이터 데이터를 수집하고, Python 기반 멀티 프로세스 backend와 pywebview dashboard를 통해 로컬 데스크톱 환경에서 관제하는 구조다.

기존 `tcpip_project`의 핵심 흐름은 다음과 같았다.

```text
Pico 2 W 3대
  -> TCP JSON 전송
  -> Python TCP 서버
  -> MySQL 저장
  -> Flask 대시보드
```

이번 기술 구조는 이를 다음처럼 변경한다.

```text
Pico 2W Device
  -> TCP JSON
collector process
  -> local IPC
backend process
  -> SQLite
worker process
  -> alert / aggregation
backend process
  -> HTTP / WebSocket
ui process(pywebview)
```

## 2. 프로세스 아키텍처

### 2.1 process 목록

| Process | 책임 | 구현 후보 |
|---|---|---|
| `collector` | Pico 2W TCP 연결 수신, payload validation, 내부 이벤트 발행 | Python `asyncio.start_server` 또는 `socketserver` |
| `backend` | HTTP API, WebSocket, DB access, service orchestration | FastAPI, Uvicorn |
| `worker` | alert rule, 통계 집계, device heartbeat 검사 | Python multiprocessing process |
| `ui` | pywebview window 실행, dashboard 표시 | pywebview + HTML/CSS/JS 또는 React/Vite |
| `simulator` | Pico 없이 테스트 payload 생성 | Python script |

### 2.2 process 통신

MVP에서는 로컬 TCP를 기본 IPC로 사용한다.

| 구간 | 방식 | 포트 예시 | 비고 |
|---|---|---:|---|
| Pico -> collector | TCP JSON line | 4242 | 이전 프로젝트 구조 계승 |
| collector -> backend | local TCP 또는 pipe | 4250 | normalized event 전달 |
| backend -> ui | HTTP | 8000 | pywebview가 localhost dashboard 로드 |
| backend -> ui | WebSocket | 8000 | 실시간 데이터 push |
| backend -> worker | pipe 또는 multiprocessing Queue | - | alert/aggregation 작업 |

처음에는 local TCP를 추천한다. 제한사항의 TCP/IP stack 기반 통신을 명확히 보여줄 수 있고, 프로세스 분리 검증이 쉽기 때문이다.

## 3. Pico 2W firmware

### 3.1 역할

- Wi-Fi 연결
- TCP server 연결
- 센서값 읽기 또는 테스트값 생성
- JSON line payload 전송
- 연결 실패 시 retry

### 3.2 payload 예시

```json
{
  "device_id": "pico-living-01",
  "seq": 1024,
  "sensors": {
    "temperature": 24.3,
    "humidity": 48.2,
    "light": 410.5
  },
  "actuators": {
    "light": "ON",
    "air_conditioner": "COOLING"
  },
  "timestamp": "2026-06-01T10:00:00+09:00"
}
```

### 3.3 sensor 구성

| Device | 위치 | Sensor | Actuator |
|---|---|---|---|
| `pico-living-01` | 거실 | temperature, humidity, light | light, air_conditioner, curtain |
| `pico-bedroom-01` | 침실 | temperature, humidity | light, air_conditioner |
| `pico-kitchen-01` | 주방 | temperature, motion | light, fan |

## 4. 내부 이벤트 모델

collector는 Pico payload를 backend 저장용 이벤트로 정규화한다.

```json
{
  "event_id": "evt-20260601-000001",
  "device_id": "pico-living-01",
  "sensor_id": "living-temperature",
  "protocol": "tcp-json",
  "value": 24.3,
  "unit": "celsius",
  "timestamp": "2026-06-01T10:00:00+09:00",
  "quality": "good",
  "trace_id": "trc-1024"
}
```

### 4.1 quality 값

| 값 | 의미 |
|---|---|
| `good` | 정상 데이터 |
| `stale` | 수신은 됐지만 timestamp가 오래됨 |
| `invalid` | 타입, 범위, 필수 필드 오류 |
| `unknown_device` | 등록되지 않은 device_id |

## 5. Database 설계

MVP DB는 SQLite를 사용한다. 이전 프로젝트의 `ROOM`, `SENSOR`, `SENSOR_READING`, `ACTUATOR`, `ACTUATOR_STATE_LOG`, `DEVICE` 개념을 유지하되, 로컬 앱에 맞게 단순화한다.

### 5.1 tables

| Table | 목적 |
|---|---|
| `sites` | 설치 장소. MVP에서는 `home` 1개 |
| `rooms` | 거실, 침실, 주방 |
| `devices` | Pico 2W 장치 |
| `sensors` | 장치별 센서 metadata |
| `actuators` | 장치별 액추에이터 metadata |
| `sensor_readings` | 센서 측정 로그 |
| `actuator_state_logs` | 액추에이터 상태 로그 |
| `process_heartbeats` | collector/backend/worker 상태 |
| `system_logs` | 에러 및 운영 로그 |

### 5.2 핵심 schema 초안

```sql
CREATE TABLE devices (
  device_id TEXT PRIMARY KEY,
  room_id TEXT NOT NULL,
  device_name TEXT NOT NULL,
  protocol TEXT NOT NULL DEFAULT 'tcp-json',
  enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE sensor_readings (
  reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
  device_id TEXT NOT NULL,
  sensor_id TEXT NOT NULL,
  value REAL NOT NULL,
  unit TEXT NOT NULL,
  quality TEXT NOT NULL,
  measured_at TEXT NOT NULL,
  received_at TEXT NOT NULL
);
```

## 6. Backend API

### 6.1 HTTP API

| Method | Path | 설명 |
|---|---|---|
| `GET` | `/api/health` | backend와 DB 상태 |
| `GET` | `/api/devices` | 등록 장치 목록 |
| `GET` | `/api/rooms` | 방별 최신 상태 |
| `GET` | `/api/readings/recent` | 최근 센서 로그 |
| `GET` | `/api/logs` | system log 조회 |
| `POST` | `/api/actuators/{actuator_id}/command` | 액추에이터 명령 예약 또는 기록 |

### 6.2 WebSocket

| Path | Event | 설명 |
|---|---|---|
| `/ws/dashboard` | `reading.created` | 새 센서값 |
| `/ws/dashboard` | `actuator.updated` | 액추에이터 상태 변경 |
| `/ws/dashboard` | `alert.created` | 경고 발생 |
| `/ws/dashboard` | `process.heartbeat` | 프로세스 상태 |

## 7. pywebview UI

### 7.1 화면 구성

- 상단 상태바: collector/backend/worker 연결 상태
- 좌측 device list: 방별 Pico 장치
- 중앙 dashboard: 최신 센서값과 차트
- 우측 alert panel: 임계값 경고, device offline
- 하단 system log: 최근 이벤트와 에러

### 7.2 실행 방식

1. launcher가 backend process를 시작한다.
2. launcher가 collector process와 worker process를 시작한다.
3. backend health check가 성공하면 pywebview window를 연다.
4. pywebview는 `http://127.0.0.1:8000`을 로드한다.
5. 종료 시 child process를 정리한다.

## 8. Error handling

| 상황 | 처리 |
|---|---|
| invalid JSON | collector가 reject하고 `system_logs`에 기록 |
| unknown device_id | `quality=unknown_device` 로그 저장 후 dashboard warning 표시 |
| Pico disconnected | heartbeat timeout 후 device offline 표시 |
| collector -> backend 실패 | retry 후 실패 횟수 로그 기록 |
| DB write failure | backend error log와 UI warning 표시 |
| WebSocket disconnected | UI가 자동 재연결 |

## 9. 보안 및 운영

MVP는 로컬 데스크톱 앱이므로 외부 인증은 최소화한다.

- backend는 기본적으로 `127.0.0.1`에만 bind한다.
- Pico collector port는 같은 Wi-Fi 대역에서만 접근하도록 방화벽 규칙을 안내한다.
- `.env` 또는 config 파일에 Wi-Fi 비밀번호를 저장하지 않는다.
- payload와 로그에 민감 정보를 남기지 않는다.
- 액추에이터 명령은 등록된 actuator_id만 허용한다.

## 10. 테스트 전략

### 10.1 단위 테스트

- payload parser
- device registry lookup
- normalization function
- DB repository
- alert rule

### 10.2 통합 테스트

- simulator -> collector -> backend -> SQLite 저장
- backend API 조회
- WebSocket event 수신
- pywebview launcher smoke test

### 10.3 수동 시연 체크

- simulator 3대 실행
- dashboard 최신값 갱신 확인
- collector process 강제 종료 후 offline 표시 확인
- 잘못된 JSON 전송 후 error log 확인

## 11. 기술 스택

| 영역 | 추천 기술 |
|---|---|
| Pico firmware | Pico SDK C, lwIP TCP |
| Collector | Python 3.12, asyncio TCP |
| Backend | FastAPI, Uvicorn, Pydantic |
| UI | pywebview, HTML/CSS/JS 또는 React/Vite |
| DB | SQLite |
| Chart | Chart.js 또는 lightweight chart library |
| Test | pytest 또는 unittest |
| Packaging | PyInstaller, optional |

React/Vite는 화면 상태가 복잡해질 때 추천한다. 단순 MVP라면 HTML/CSS/JS로 시작해도 충분하다.

## 12. 디렉터리 구조 제안

```text
hrd_second_project/
  app/
    launcher.py
    collector/
      server.py
      parser.py
    backend/
      main.py
      api.py
      services.py
      repositories.py
    worker/
      alerts.py
      heartbeat.py
    ui/
      index.html
      styles.css
      app.js
    shared/
      schemas.py
      config.py
      logging.py
  firmware/
    pico_home_client/
  scripts/
    simulate_pico.py
    init_db.py
  data/
    home_iot.sqlite3
  doc/
    2nd_project.md
    project_plan.md
    technical_spec.md
```

## 13. 구현 우선순위

1. `simulator`, `collector`, `backend`, `ui`를 별도 프로세스로 실행한다.
2. TCP JSON 수신과 SQLite 저장을 연결한다.
3. pywebview dashboard에서 최신값을 표시한다.
4. WebSocket으로 실시간 갱신을 추가한다.
5. Pico 2W firmware를 연결한다.
6. MQTT adapter와 device registry를 확장한다.

## 14. 선택이 필요한 항목

현재 단계에서는 사용자 선택 없이 다음 기본안을 추천한다.

- DB: SQLite
- backend: FastAPI
- UI: HTML/CSS/JS로 MVP 시작, 필요 시 React/Vite 전환
- IPC: collector -> backend local TCP
- protocol: MVP는 TCP JSON, 확장 옵션은 MQTT

팀에서 프론트엔드 비중을 높이고 싶다면 React/Vite를 선택하는 것이 좋다. 반대로 하드웨어와 프로세스 구조 시연이 핵심이면 HTML/CSS/JS가 더 빠르다.
