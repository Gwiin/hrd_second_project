# Pico SafeRoom 업데이트 기록

이 문서는 `docs/superpowers` 아래의 spec, plan, asset, 구현 진행 상태를 한곳에 모아 보는 업데이트 기록입니다.

마지막 업데이트: 2026-06-02

## 현재 상태

- 완료: Level 1부터 Level 5D까지의 backend, collector, dashboard, alert, heartbeat, log 기반 기능.
- 완료: 실제 Pico 2W용 MicroPython real-sensor firmware 경로.
- 완료: 팀원용 한국어 README/SETUP/firmware 문서.
- 완료: Apple Liquid Glass 스타일 dashboard redesign 구현.
- 다음 작업: 실제 센서 bring-up 후 real data 상태에서 dashboard calibration/status UI 보강.

## 최신 디자인 기준

Apple Liquid Glass dashboard visual은 승인 완료 상태입니다.

- 승인된 visual asset: [pico-saferoom-liquid-glass-dashboard-concept.png](assets/pico-saferoom-liquid-glass-dashboard-concept.png)
- 핵심 방향:
  - Apple/macOS 느낌의 light-mode Liquid Glass dashboard.
  - 큰 top-left 로고 제거.
  - `Pico SafeRoom` 텍스트 중심의 header.
  - 기존 dashboard 정보 구조 유지.
  - Remotion은 사용하지 않음.

## 2026-06-02

### 실제 Pico 2W 센서 펌웨어

상태: 완료

- 실제 Raspberry Pi Pico 2W 4대 사용을 위한 MicroPython firmware 경로를 추가.
- host-side simulator와 실제 firmware 경로를 분리.
- DHT-style temperature/humidity, PIR motion, analog gas, analog light sensor adapter 구조를 추가.
- MQTT reading/status publish contract를 기존 collector와 호환되게 유지.
- 실제 센서 연결용 wiring guide와 SVG visual을 추가.

관련 문서:

- [Real Sensor Firmware Design](specs/2026-06-02-pico-saferoom-real-sensor-firmware-design.md)
- [Real Sensor Firmware Plan](plans/2026-06-02-pico-saferoom-real-sensor-firmware.md)

관련 주요 파일:

- `firmware/pico2w/main.py`
- `firmware/pico2w/sensors.py`
- `firmware/pico2w/payloads.py`
- `firmware/pico2w/README.real-sensors.md`
- `firmware/pico2w/assets/pico2w-real-sensor-wiring.svg`

### 한국어 팀 문서

상태: 완료

- 팀원이 바로 읽을 수 있도록 주요 setup/project/firmware 문서를 한국어로 정리.
- 한국어 전용 문서와 기존 README/SETUP 계열 문서를 함께 정리.

관련 주요 파일:

- `README.ko.md`
- `SETUP.ko.md`
- `firmware/pico2w/README.ko.md`
- `firmware/pico2w/README.real-sensors.ko.md`

### Apple Liquid Glass Dashboard Redesign

상태: 구현 완료, visual QA 완료

- Build Web Apps 방향으로 React/Vite dashboard redesign 진행.
- Build macOS Apps의 Liquid Glass 원칙을 web dashboard에 맞게 적용 예정.
- 사용자가 top-left 로고를 싫어한다고 피드백하여 큰 로고를 제거한 revised visual을 생성.
- 최종 승인된 visual 기준으로 `frontend/src/App.tsx`와 `frontend/src/App.css`를 구현.
- 기존 data fetching, REST fallback, WebSocket client logic은 유지.
- Local QA에서 WebSocket은 환경에 `websockets`/`wsproto` server library가 없어 `Reconnecting`으로 표시됨. 이 항목은 styling regression이 아니라 runtime dependency 확인 항목임.

관련 asset:

- [pico-saferoom-liquid-glass-dashboard-concept.png](assets/pico-saferoom-liquid-glass-dashboard-concept.png)

구현 대상:

- `frontend/src/App.tsx`
- `frontend/src/App.css`

검증:

- `npm --prefix frontend run build`
- desktop screenshot 검증
- mobile screenshot 검증

## 2026-06-01

### Level 1: 프로젝트 골격

상태: 완료

- Pico SafeRoom 기본 skeleton 구성.
- FastAPI backend, collector, worker, desktop launcher, React dashboard의 기본 형태를 생성.
- 4개 Pico 2W device identity와 기본 sensor reading flow를 정의.

관련 문서:

- [Level 1 Design](specs/2026-06-01-pico-saferoom-level1-design.md)
- [Level 1 Plan](plans/2026-06-01-pico-saferoom-level1.md)

### Level 2A: SQLite 저장소

상태: 완료

- `data/saferoom.db` 기반 SQLite persistence 추가.
- `devices`, `sensors`, `sensor_readings`, `system_logs` schema 추가.
- `/api/readings/latest`를 SQLite 기반으로 유지.
- `/api/readings/history` 추가.

관련 문서:

- [Level 2A Design](specs/2026-06-01-pico-saferoom-level2a-design.md)
- [Level 2A Plan](plans/2026-06-01-pico-saferoom-level2a.md)

### Level 2B: Alerts

상태: 완료

- threshold 기반 alert persistence 추가.
- gas/temperature warning 및 critical alert rule 추가.
- `GET /api/alerts`, `POST /api/alerts/{alert_id}/ack` 추가.

관련 문서:

- [Level 2B Alerts Design](specs/2026-06-01-pico-saferoom-level2b-alerts-design.md)
- [Level 2B Alerts Plan](plans/2026-06-01-pico-saferoom-level2b-alerts.md)

### Level 3: Pico MQTT

상태: 완료

- Pico 2W reading/status MQTT topic contract 정의.
- MQTT collector가 reading payload를 `SensorEvent(protocol="mqtt")`로 normalize하도록 구성.
- MicroPython firmware scaffold와 `config.example.py` 추가.

관련 문서:

- [Level 3 Pico MQTT Design](specs/2026-06-01-pico-saferoom-level3-pico-mqtt-design.md)
- [Level 3 Pico MQTT Plan](plans/2026-06-01-pico-saferoom-level3-pico-mqtt.md)

### Level 4: Realtime Dashboard

상태: 완료

- FastAPI WebSocket `/ws/realtime` 추가.
- reading ingest 후 `reading.created` event broadcast 추가.
- React dashboard WebSocket client 추가.
- REST polling fallback 유지.

관련 문서:

- [Level 4 Realtime Dashboard Design](specs/2026-06-01-pico-saferoom-level4-realtime-dashboard-design.md)
- [Level 4 Realtime Dashboard Plan](plans/2026-06-01-pico-saferoom-level4-realtime-dashboard.md)

### Level 5A: Data Quality

상태: 완료

- sensor reading quality 처리를 강화.
- dashboard와 backend가 reading quality 상태를 표시할 수 있게 정리.

관련 문서:

- [Level 5A Quality Design](specs/2026-06-01-pico-saferoom-level5a-quality-design.md)
- [Level 5A Quality Plan](plans/2026-06-01-pico-saferoom-level5a-quality.md)

### Level 5B: Device Heartbeat

상태: 완료

- device heartbeat schema와 backend persistence/API flow 추가.
- MQTT collector가 Pico status topic을 device heartbeat로 전달하도록 확장.

관련 문서:

- [Level 5B Heartbeat Design](specs/2026-06-01-pico-saferoom-level5b-heartbeat-design.md)
- [Level 5B Heartbeat Plan](plans/2026-06-01-pico-saferoom-level5b-heartbeat.md)

### Level 5C: Stale Sensors

상태: 완료

- stale sensor detection과 stale alert 흐름 추가.
- 오래 갱신되지 않은 sensor 상태를 alert로 볼 수 있게 정리.

관련 문서:

- [Level 5C Stale Sensors Design](specs/2026-06-01-pico-saferoom-level5c-stale-sensors-design.md)
- [Level 5C Stale Sensors Plan](plans/2026-06-01-pico-saferoom-level5c-stale-sensors.md)

### Level 5D: Process Logs

상태: 완료

- process heartbeat persistence 추가.
- `/api/health.processes`가 persisted process heartbeat를 반영하도록 확장.
- UI-facing SQLite system logs와 developer file logs를 분리.

관련 문서:

- [Level 5D Process Logs Design](specs/2026-06-01-pico-saferoom-level5d-process-logs-design.md)
- [Level 5D Process Logs Plan](plans/2026-06-01-pico-saferoom-level5d-process-logs.md)

## Git 기준 주요 기록

- `ef1d7ae docs: add Korean project guides`
- `c6b13cc merge real Pico sensor firmware path`
- `15a1fef feat: add real Pico sensor firmware path`
- `6ed2e85 docs: document level 5d setup`
- `4f32012 feat: add pico saferoom level 1 skeleton`

## 업데이트 규칙

- 새 Level, design, plan, major implementation, merge, hardware decision이 생기면 이 문서에 한 줄 이상 추가한다.
- 자세한 요구사항은 `specs/`에 남기고, 실행 계획은 `plans/`에 남긴다.
- 이 문서는 팀원이 현재 상태를 빠르게 파악하기 위한 요약본으로 유지한다.
- 진행 중인 항목은 반드시 `진행 중`, `디자인 승인 완료`, `구현 예정`처럼 완료 여부를 명확히 적는다.
