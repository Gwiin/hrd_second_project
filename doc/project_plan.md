# 2차 프로젝트 계획서

## 1. 프로젝트명

**Pico Home IoT Desktop Control Hub**

Raspberry Pi Pico 2W 기반 홈 IoT 센서/액추에이터 데이터를 수집하고, pywebview 데스크톱 대시보드에서 방별 상태를 관제하는 멀티 프로세스 IoT 시스템이다.

## 2. 기획 배경

이전 홈 IoT 프로젝트(`Gwiin/tcpip_project`)는 Pico 2W 3대가 방별 센서값과 액추에이터 상태를 TCP JSON으로 전송하고, Python TCP 서버가 MySQL에 저장한 뒤 Flask 대시보드에 표시하는 구조였다.

이번 프로젝트는 그 구조를 그대로 반복하지 않고, 2차 프로젝트 제한사항에 맞춰 다음 방향으로 개선한다.

- 웹 브라우저 대시보드가 아니라 **pywebview 기반 데스크톱 앱**으로 제공한다.
- 단일 Flask/TCP 서버 중심이 아니라 **collector, backend, worker, ui 프로세스**로 분리한다.
- Pico 2W의 TCP JSON 전송 경험은 유지하되, 내부 데이터 모델과 프로세스 경계를 명확히 한다.

## 3. 목표

### 3.1 핵심 목표

- Pico 2W에서 온도, 습도, 조도, 움직임 등 센서 데이터를 주기적으로 전송한다.
- PC의 collector process가 Pico 2W 데이터를 TCP로 수신한다.
- backend process가 수신 데이터를 정규화하고 저장한다.
- worker process가 경고 조건, 장치 상태, 통계 데이터를 처리한다.
- pywebview dashboard가 현재 상태, 그래프, 로그, 경고를 데스크톱 앱 형태로 표시한다.

### 3.2 성공 기준

- Pico 2W 또는 simulator에서 보낸 JSON 데이터가 collector에 정상 수신된다.
- collector와 backend가 별도 프로세스로 실행된다.
- backend와 pywebview dashboard가 별도 프로세스로 실행된다.
- 대시보드에서 방별 최신 센서값, 액추에이터 상태, 최근 로그를 확인할 수 있다.
- 네트워크 단절, 잘못된 JSON, 미등록 device_id에 대한 에러 로그가 남는다.

## 4. 필수 제한사항 반영

| 제한사항 | 반영 방식 |
|---|---|
| Raspberry Pi Pico 2W 기반 기기 구현 | Pico 2W firmware가 센서값과 액추에이터 상태를 TCP JSON으로 전송한다. 실제 Pico 연결 전에는 simulator로 동일 payload를 보낸다. |
| pywebview 기반 대시보드 | FastAPI backend를 localhost에서 실행하고, pywebview window가 React/Vite 또는 HTML dashboard를 로드한다. |
| Micro-architecture 기반 멀티 프로세스 | `collector`, `backend`, `worker`, `ui`를 별도 프로세스로 분리하고 TCP 또는 pipe 기반 IPC로 연결한다. |

## 5. 범위

### 5.1 MVP 범위

- Pico 2W 1~3대 또는 simulator 지원
- 방 단위 device 등록
- 센서 데이터 수집: temperature, humidity, light, motion
- 액추에이터 상태 수집: light, air_conditioner, curtain, fan
- SQLite 저장
- pywebview dashboard
- 최근 로그 및 기본 차트
- 프로세스별 로그 파일

### 5.2 제외 범위

- 실제 Matter 제품 연동
- Mobius/oneM2M 플랫폼 연동
- 산업용 프로토콜 연동
- RTOS 기반 펌웨어
- C++ core 기반 고성능 처리
- 다중 사용자 웹 서비스

위 항목은 프로젝트 구조를 흔들지 않는 확장 옵션으로만 남긴다.

## 6. 추천 옵션

### 6.1 채택 추천

| 옵션 | 추천 여부 | 이유 |
|---|---:|---|
| SQLite | 추천 | 로컬 데스크톱 앱과 교육용 실습에 적합하고 설치 부담이 작다. |
| FastAPI | 추천 | pywebview UI와 HTTP/WebSocket API를 분리하기 쉽다. |
| WebSocket | 추천 | 센서값과 경고 상태를 대시보드에 실시간 반영하기 좋다. |
| MQTT | 조건부 추천 | TCP 직접 전송 MVP 이후 pub/sub 구조를 보여주는 확장 단계로 적합하다. |
| device/sensor/event 정규화 모델 | 추천 | 이전 프로젝트의 방별 고정 map보다 확장성이 좋다. |

### 6.2 후순위 추천

| 옵션 | 권장 단계 | 이유 |
|---|---|---|
| Matter | Level 4 이후 | 스마트홈 상용 제품 연동에는 좋지만 MVP 난도가 높다. |
| Mobius/oneM2M | Level 4 이후 | 표준 플랫폼 연계가 목표일 때만 필요하다. |
| C++ core | Level 5 이후 | Python으로 충분하지 않은 고속 처리나 장비 제어가 생긴 뒤 도입한다. |
| RTOS | Level 6 이후 | Pico 2W 제어 주기가 엄격해질 때만 필요하다. |
| PostgreSQL/TimescaleDB | Level 5 이후 | 장기 운영 또는 대량 시계열 저장이 필요할 때 전환한다. |

## 7. 시스템 구성

```text
Pico 2W Device 또는 Simulator
  -> TCP JSON
Collector Process
  -> local TCP / pipe
Backend Process
  -> SQLite
Worker Process
  -> alert / aggregation / health check
Backend Process
  -> HTTP / WebSocket
pywebview UI Process
```

## 8. 주요 기능

### 8.1 장치 데이터 수집

- Pico 2W는 3~5초 주기로 JSON payload를 전송한다.
- collector는 여러 Pico 연결을 동시에 처리한다.
- 잘못된 payload는 저장하지 않고 error log에 남긴다.

### 8.2 데이터 정규화

- device, sensor, actuator, reading, event를 분리한다.
- 내부 이벤트는 `device_id`, `sensor_id`, `value`, `unit`, `timestamp`, `quality`를 포함한다.

### 8.3 대시보드

- 방별 최신 센서값
- 센서 변화 차트
- 액추에이터 현재 상태
- 최근 이벤트 로그
- 경고 패널
- collector/backend/worker 상태 표시

### 8.4 에러 처리

- device offline
- invalid JSON
- unknown device_id
- collector/backend IPC timeout
- DB write failure

## 9. 개발 단계

### Level 1: 필수 구조 완성

- Pico simulator 구현
- collector/backend/ui 프로세스 분리
- pywebview window 실행
- 최신 센서값 표시

### Level 2: 저장과 차트

- SQLite schema 구성
- sensor_readings 저장
- 방별 차트 표시
- 최근 로그 패널

### Level 3: 실시간 처리

- WebSocket 갱신
- worker process에서 alert rule 처리
- 프로세스 heartbeat 표시

### Level 4: 프로토콜 확장

- MQTT adapter 추가
- device registry 도입
- protocol adapter 인터페이스 정리

### Level 5: 품질 강화

- 에러 포맷 표준화
- 로그 레벨 분리
- 설정 파일 관리
- 테스트 자동화

## 10. 역할 분담 예시

| 역할 | 담당 영역 |
|---|---|
| Firmware | Pico 2W TCP client, sensor payload |
| Collector | TCP server, payload validation, IPC publish |
| Backend | API, DB, schema, service logic |
| UI | pywebview, dashboard, chart, UX |
| QA/Docs | simulator, test scenario, 발표 자료 |

## 11. 발표 포인트

- 이전 프로젝트의 TCP 기반 Home Manager 경험을 2차 제한사항에 맞춰 발전시켰다.
- Pico 2W, pywebview, multi-process 구조를 모두 만족한다.
- 웹앱이 아니라 데스크톱 IoT 관제 앱으로 실행된다.
- 옵션 기능은 MVP와 확장 단계로 분리해 과도한 범위를 피했다.

