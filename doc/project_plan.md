# 스마트 실내 환경 안전 관제 시스템 계획서

## 1. 프로젝트 개요

### 1.1 프로젝트명

**Pico SafeRoom: 스마트 실내 환경 안전 관제 시스템**

Raspberry Pi Pico 2W 기반 센서 노드가 실내의 온도, 습도, 조도, 움직임, 가스/연기 등 안전 관련 데이터를 수집하고, pywebview 데스크톱 대시보드에서 실시간 상태와 경고를 확인하는 로컬 IoT 관제 시스템이다.

### 1.2 선정 이유

이 주제는 2차 프로젝트의 필수 제한사항을 자연스럽게 만족한다.

- Pico 2W가 실제 센서 노드 역할을 한다.
- pywebview 대시보드에서 실시간 관제 화면을 제공한다.
- collector, backend, worker, ui를 분리해 micro-architecture를 명확히 보여줄 수 있다.
- MQTT, WebSocket, SQLite, device registry, heartbeat, alert, system log 같은 선택사항을 충분히 활용할 수 있다.

## 2. 프로젝트 목표

### 2.1 핵심 목표

- Pico 2W가 실내 환경 센서 데이터를 주기적으로 전송한다.
- Collector process가 MQTT 메시지를 수신하고 표준 `SensorEvent`로 정규화한다.
- Backend process가 데이터를 저장하고 REST API/WebSocket으로 제공한다.
- Worker process가 임계값 경고, 장치 offline, 센서 stale 상태를 판단한다.
- pywebview Dashboard가 실시간 상태, 차트, 경고, 로그를 데스크톱 앱으로 표시한다.

### 2.2 최종 시연 목표

1. Pico 2W 또는 sensor simulator에서 실내 센서값을 전송한다.
2. 대시보드에서 방별 안전 상태가 실시간 갱신된다.
3. 가스/연기 수치 또는 온도가 임계값을 넘으면 경고가 발생한다.
4. Pico 2W heartbeat가 끊기면 장치 offline 상태가 표시된다.
5. 최근 센서값, 경고 이력, 시스템 로그를 조회할 수 있다.

## 3. 필수 제한사항 반영

| 필수 제한사항 | 반영 방식 |
| --- | --- |
| Raspberry Pi Pico 2W 기반 장치 구현 | Pico 2W를 센서 노드로 사용한다. 실제 센서가 부족한 경우에도 Pico 2W 내부 가상값 또는 simulator를 사용해 동일 payload를 전송한다. |
| pywebview 기반 데스크톱 대시보드 | Python launcher가 backend와 pywebview를 실행하고, pywebview 창에서 React/Vite dashboard를 로드한다. |
| Micro-architecture 기반 멀티 프로세스 | collector, backend, worker, ui를 별도 역할로 분리한다. 프로세스 간 통신은 MQTT, local queue, WebSocket을 조합한다. |

## 4. 권장 기술 스택

| 영역 | 채택 기술 | 이유 |
| --- | --- | --- |
| Pico firmware | MicroPython | 수업 프로젝트에서 구현과 디버깅이 빠르다. |
| Sensor protocol | MQTT | Pico 2W 센서 publish 구조에 적합하고 IoT 주제와 잘 맞는다. |
| MQTT broker | Eclipse Mosquitto | 경량이고 로컬 개발 환경에 적합하다. |
| Collector | Python + paho-mqtt + Pydantic | MQTT 수신과 schema validation을 단순하게 구현할 수 있다. |
| Backend | FastAPI + Uvicorn | REST API와 WebSocket을 한 구조에서 제공하기 쉽다. |
| DB | SQLite + SQLAlchemy | 로컬 데스크톱 MVP에 적합하고 설치 부담이 낮다. |
| Realtime | FastAPI WebSocket | 경고와 센서값을 UI에 즉시 반영할 수 있다. |
| Desktop | pywebview | 필수 제한사항을 만족하는 데스크톱 shell이다. |
| Frontend | React + Vite + TypeScript + ECharts | 상태 화면과 차트를 만들기 좋다. |
| Test | pytest | parser, alert rule, API 테스트에 적합하다. |

선택이 필요한 부분은 현재 없다. 구현 난도를 줄여야 한다면 React/Vite 대신 HTML/CSS/JavaScript로 시작할 수 있지만, 대시보드 확장성을 고려하면 React/Vite를 추천한다.

## 5. 시스템 아키텍처

```text
Pico 2W Sensor Node
  -> MQTT publish
Mosquitto Broker
  -> subscribe
Collector Process
  -> SensorEvent normalization
Backend Process
  -> SQLite 저장
Worker Process
  -> alert / heartbeat / stale check
Backend Process
  -> REST API / WebSocket
pywebview Dashboard
```

## 6. 주요 기능

### 6.1 센서 수집

- 온도: 과열 감지
- 습도: 실내 환경 상태 확인
- 조도: 조명/야간 상태 확인
- 움직임: 재실 또는 침입 상황 감지
- 가스/연기: 안전 경고 핵심 센서

실제 센서가 부족할 경우 Pico 2W에서 가상 센서값을 생성한다. 이 경우에도 데이터 흐름은 실제 센서와 동일하게 유지한다.

### 6.2 실시간 관제

- 방/구역별 현재 상태 표시
- 센서별 최신값 카드
- 시간대별 센서 차트
- 장치 online/offline 표시
- 위험 상태 색상 표시

### 6.3 경고 처리

- 온도 임계값 초과
- 가스/연기 수치 초과
- 움직임 감지 시간대 조건
- 장치 heartbeat timeout
- 센서값 stale 상태

### 6.4 로그와 진단

- 센서 수신 로그
- 경고 발생 로그
- 장치 연결 상태 로그
- collector/backend/worker 프로세스 상태
- invalid payload 로그

## 7. 데이터 모델

모든 센서 입력은 내부에서 표준 `SensorEvent`로 변환한다.

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
  "metadata": {
    "topic": "saferoom/room-1/pico-safe-001/gas"
  }
}
```

## 8. MVP 범위

- Pico 2W 1대 이상 또는 Pico simulator
- MQTT publish/subscribe
- collector/backend/ui/worker 역할 분리
- SQLite 저장
- pywebview dashboard
- 실시간 센서값 표시
- 기본 경고 규칙 3개 이상
- 최근 로그 조회

## 9. 확장 옵션

| 옵션 | 적용 단계 | 설명 |
| --- | --- | --- |
| device registry | MVP | 장치, 센서, 구역 정보를 DB에 등록한다. |
| WebSocket | MVP | 실시간 대시보드 갱신에 사용한다. |
| ZeroMQ | 2차 확장 | collector/backend/worker 간 event bus로 사용할 수 있다. |
| PostgreSQL/TimescaleDB | 운영 확장 | 장기 센서 이력 저장 시 전환한다. |
| Matter | 후순위 | 상용 스마트홈 센서를 연결할 때 bridge 계층으로 검토한다. |
| Mobius/oneM2M | 후순위 | 표준 IoT 플랫폼 연계가 필요할 때 검토한다. |
| C++ core | 후순위 | 고속 필터링 또는 장치 제어 명령 처리 시 별도 프로세스로 둔다. |
| RTOS | 후순위 | 센서 주기와 제어 반응성이 엄격해질 때 검토한다. |

## 10. 단계별 개발 계획

### Level 1. 구조 골격

- 프로젝트 디렉터리 구성
- collector/backend/worker/ui 프로세스 실행 구조 작성
- sensor simulator로 mock event 생성
- pywebview에서 기본 dashboard 실행

### Level 2. 데이터 저장

- SQLite schema 작성
- `devices`, `sensors`, `sensor_readings`, `alerts`, `system_logs` 저장
- backend API 제공

### Level 3. Pico 2W 연동

- MicroPython firmware 작성
- MQTT topic 설계
- Pico heartbeat 전송
- collector에서 `SensorEvent` 변환

### Level 4. 실시간 대시보드

- WebSocket 연결
- 최신 센서값 자동 갱신
- 차트와 alert panel 구성
- offline/degraded 상태 표시

### Level 5. 품질 강화

- invalid payload 처리
- 에러 포맷 표준화
- 로그 파일과 UI 로그 분리
- 단위/통합 테스트 작성

## 11. 역할 분담 예시

| 역할 | 담당 |
| --- | --- |
| Device | Pico 2W firmware, sensor wiring, MQTT publish |
| Collector | MQTT subscribe, schema validation, SensorEvent 변환 |
| Backend | FastAPI, DB, WebSocket, API |
| Worker | alert rule, heartbeat, stale check |
| Frontend | pywebview dashboard, chart, log panel |
| QA/Docs | test scenario, 발표 자료, 설치 문서 |

## 12. 발표 시나리오

1. pywebview 앱을 실행한다.
2. Pico 2W 또는 simulator가 MQTT로 센서값을 전송한다.
3. dashboard에서 실시간 센서값과 차트가 갱신된다.
4. 가스/연기 수치를 임계값 이상으로 올려 경고를 발생시킨다.
5. Pico heartbeat를 중단해 offline 상태를 보여준다.
6. 시스템 로그와 경고 이력을 조회한다.

## 13. 기대 효과

- IoT device, protocol, backend, desktop dashboard를 한 프로젝트에서 연결한다.
- 필수 제한사항을 형식적으로만 만족하지 않고 실제 구조로 보여준다.
- MQTT, WebSocket, DB, alert, log 등 선택사항을 발표 가능한 기능으로 만든다.
- Matter, Mobius, RTOS, C++ core 같은 고급 옵션은 구조 안에 확장 여지를 남긴다.
