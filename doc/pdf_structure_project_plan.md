# HRD 2차 프로젝트 계획서

2026년 6월 1일

## 주제: Pico SafeRoom - 스마트 실내 환경 안전 관제 시스템

## 개인 역할 분담 및 실행

| 담당 | 역할 | 실행 내용 |
| --- | --- | --- |
| 팀원 1 | PM / 아키텍처 | 전체 일정 관리, 요구사항 정리, 시스템 구조 설계, 발표 자료 정리 |
| 팀원 2 | Pico 2W / Collector | Raspberry Pi Pico 2W MicroPython firmware, MQTT topic 설계, simulator 및 MQTT collector 구현 |
| 팀원 3 | Backend / Worker | FastAPI 서버, SQLite 저장소, 경고 판단, heartbeat/API/log 기능 구현 |
| 팀원 4 | Frontend / Desktop / QA | React/Vite 대시보드, WebSocket 실시간 갱신, pywebview 실행, 테스트 시나리오 점검 |

## 과제 목표

- Raspberry Pi Pico 2W 기반 센서 노드를 활용하여 실내 환경과 안전 상태를 모니터링하는 IoT 관제 시스템을 구현한다.
- 온도, 습도, 조도, 움직임, 가스 센서 데이터를 수집하고 표준 `SensorEvent` 형식으로 정규화한다.
- collector, backend, worker, desktop UI를 분리한 micro-architecture 구조로 각 기능을 독립적으로 실행하고 관리한다.
- FastAPI backend를 통해 센서 최신값, 센서 이력, 장치 목록, 경고 목록, 시스템 로그, 상태 정보를 REST API로 제공한다.
- SQLite를 사용하여 장치 registry, 센서 readings, alerts, system logs, process heartbeat를 저장한다.
- WebSocket 기반 `/ws/realtime` 채널을 통해 dashboard에 최신 센서 이벤트를 즉시 반영한다.
- pywebview 기반 데스크톱 앱에서 React/Vite 대시보드를 실행하여 실시간 센서 상태, 장치 상태, 경고 상태를 확인할 수 있도록 한다.
- simulator 기반 흐름과 Pico 2W + MQTT 기반 흐름을 모두 지원할 수 있는 구조로 만든다.

## 수행 계획서

- 시스템을 Pico 2W 센서 노드, collector 프로세스, backend 프로세스, worker 프로세스, pywebview 대시보드로 분리하여 설계한다.
- Pico 2W 또는 simulator에서 온도, 습도, 조도, 움직임, 가스 값을 주기적으로 생성하고 전송한다.
- simulator collector는 mock 센서 이벤트를 생성하고, MQTT collector는 `saferoom/{zone}/{device}/sensors/{sensor}/reading` topic을 수신한다.
- collector는 입력 데이터를 수신한 뒤 `SensorEvent` 스키마에 맞게 변환하여 backend의 `/internal/events` API로 전달한다.
- backend는 전달받은 센서 이벤트를 SQLite에 저장하고 `/api/health`, `/api/devices`, `/api/readings/latest`, `/api/readings/history`, `/api/alerts`, `/api/logs` API를 제공한다.
- backend는 `/internal/heartbeats/device`, `/internal/heartbeats/process` endpoint로 장치와 프로세스 상태를 수신한다.
- worker는 별도 프로세스로 실행되며 heartbeat 출력과 이후 임계값, 장치 offline, 센서 stale 판단 기능 확장의 기반 역할을 한다.
- frontend는 4개의 Pico 2W 장치 상태, 센서별 최신값, 안전 상태, WebSocket 연결 상태, 프로세스 상태, 최근 로그를 한 화면에서 확인할 수 있도록 구성한다.
- pywebview launcher는 backend, collector, worker를 실행하고 데스크톱 창에서 dashboard를 열어 최종 시연 환경을 구성한다.
- simulator 기반 mock 데이터로 end-to-end 흐름을 검증하고, MQTT broker와 Pico 2W firmware scaffold를 사용해 실제 장치 연동 흐름으로 확장한다.
- 최종 시연에서는 센서 데이터 생성, backend 수신, SQLite 저장, WebSocket dashboard 갱신, 안전 상태 표시, 경고/로그 확인 흐름을 순서대로 보여준다.

## 시행 목적

본 프로젝트의 목적은 Raspberry Pi Pico 2W와 데스크톱 대시보드를 활용하여 실내 환경 안전 상태를 관제하는 로컬 IoT 시스템을 구축하는 것이다.

실내 공간을 여러 구역으로 나누고 각 구역에 Pico 2W 센서 노드가 배치되어 있다고 가정한다. 각 노드는 온도, 습도, 조도, 움직임, 가스/연기와 같은 안전 관련 데이터를 수집하며, collector와 backend를 거쳐 대시보드에 표시된다. 사용자는 pywebview 데스크톱 앱에서 장치별 최신 센서값, 센서 이력, 전체 안전 상태, WebSocket 연결 상태, 프로세스 상태, 경고, 시스템 로그를 확인할 수 있다.

이를 통해 단순한 센서 읽기 실습을 넘어 센서 데이터 수집, 데이터 스키마 표준화, backend API 설계, SQLite 저장, WebSocket 실시간 전송, 프로세스 분리, 데스크톱 UI 구현, 경고 판단 로직까지 하나의 시스템으로 통합하는 경험을 얻는 것을 목표로 한다. 또한 simulator를 먼저 사용해 전체 구조를 검증한 뒤 실제 Pico 2W와 MQTT 통신을 연결할 수 있도록 설계하여 단계적 개발과 협업 개발 방식을 학습한다.

## 사용 환경 및 사용 기술

| 구분 | 내용 |
| --- | --- |
| 장치 | Raspberry Pi Pico 2W |
| 센서 | 온도, 습도, 조도, 움직임, 가스/연기 센서 또는 simulator |
| Firmware | MicroPython scaffold, Pico SDK 확장 가능 |
| 통신 | MQTT, HTTP internal API, REST API, WebSocket |
| Collector | Python, Pydantic, sensor simulator, paho-mqtt 기반 MQTT collector |
| Backend | FastAPI, Uvicorn, SQLite repository |
| Worker | Python process, heartbeat, alert/stale/offline rule 확장 |
| Desktop | pywebview |
| Frontend | React, Vite, TypeScript, CSS |
| 데이터 모델 | `SensorEvent` schema |
| 테스트 | pytest, MQTT parser test, SQLite repository test, backend API test, frontend build |

## 사용 장비

- Raspberry Pi Pico 2W 4대
- 온습도 센서
- 조도 센서
- 움직임 감지 센서
- 가스/연기 센서
- 브레드보드
- 점퍼선
- USB 케이블
- 개발용 PC
- 로컬 MQTT broker용 Mosquitto

## 최종 시연 시나리오

1. pywebview 데스크톱 앱을 실행한다.
2. simulator collector 또는 MQTT collector가 4개의 Pico 2W 장치 데이터를 전달한다.
3. backend가 센서 이벤트를 수신하고 SQLite에 저장한다.
4. WebSocket을 통해 dashboard의 장치별 센서값과 전체 안전 상태가 갱신된다.
5. 가스 또는 온도 값이 임계값을 넘는 상황을 만들어 warning 또는 critical alert를 확인한다.
6. 최근 로그, 센서 이력, 장치 상태, 프로세스 상태를 확인하며 micro-architecture 구조로 동작하는 것을 설명한다.

## 기대 효과

- Pico 2W 기반 IoT 장치와 Python backend, 데스크톱 dashboard를 하나의 시스템으로 연결하는 경험을 얻는다.
- collector, backend, worker, UI를 분리하여 micro-architecture 구조의 장점을 이해한다.
- 센서 데이터 표준화, SQLite 저장, REST API, WebSocket 설계를 통해 여러 입력 방식이 추가되어도 dashboard를 유지할 수 있는 구조를 학습한다.
- 실제 센서가 준비되지 않은 상황에서도 simulator로 개발을 진행하고, 이후 실제 장치로 자연스럽게 확장하는 방식을 익힌다.
- 최종 발표에서 센서 데이터 흐름, 시스템 구조, UI 결과, 테스트 방법을 명확하게 제시할 수 있다.
