# Pico SafeRoom 한국어 안내

Pico SafeRoom은 Raspberry Pi Pico 2W 4대와 실제 센서를 사용해 실내 안전 상태를 모니터링하는 로컬 IoT 관제 프로젝트입니다.

## 먼저 읽을 문서

| 목적 | 문서 |
| --- | --- |
| 개발 환경 설치와 실행 | [SETUP.ko.md](SETUP.ko.md) |
| Pico 2W 펌웨어 복사/설정 | [firmware/pico2w/README.ko.md](firmware/pico2w/README.ko.md) |
| 센서 배선 방법과 그림 | [firmware/pico2w/README.real-sensors.ko.md](firmware/pico2w/README.real-sensors.ko.md) |
| 원본 영어 setup 문서 | [SETUP.md](SETUP.md) |

## 현재 구조

```text
Pico 2W 실제 센서
  -> MQTT Broker
  -> MQTT Collector
  -> FastAPI Backend
  -> SQLite
  -> WebSocket
  -> React/Vite Dashboard
```

시뮬레이터는 실제 Pico 펌웨어와 분리되어 있습니다.

- 실제 장치 코드: `firmware/pico2w/`
- 시뮬레이터 코드: `apps/collector/simulator.py`
- MQTT collector: `apps/collector/mqtt_client.py`
- Backend: `apps/backend/`
- Frontend: `frontend/`

## 차별점: Incident Replay + Guided Response

Pico SafeRoom은 센서값을 보여주는 dashboard에서 끝나지 않고, 위험 alert가 발생했을 때 대응 checklist, 운영자 note/evidence, replay 가능한 timeline을 함께 남기는 incident response demo입니다.

로컬 demo는 실제 Pico bring-up 없이도 내부 HTTP event로 확인할 수 있습니다.

```bash
curl -i -X POST http://127.0.0.1:8000/internal/events \
  -H 'Content-Type: application/json' \
  -d '{"event_id":"incident-demo-gas","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"demo":true}}'

curl -i http://127.0.0.1:8000/api/alerts/1/replay

curl -i -X POST http://127.0.0.1:8000/api/alerts/1/ack \
  -H 'Content-Type: application/json' \
  -d '{"checklist":["evacuate","ventilate","inspect_sensor"],"note":"Demo operator confirmed gas threshold and opened ventilation.","evidence":"Window opened, sensor cable checked."}'

curl -i http://127.0.0.1:8000/api/alerts/1/replay
```

실제 4대 Pico 2W 센서 bring-up과 OAuth provider credential 검증은 별도 현장 검증 항목입니다.

## 펌웨어 언어 결정

현재 프로젝트는 **MicroPython**을 사용합니다.

이유:

- Pico 2W에서 Wi-Fi, MQTT, GPIO, ADC를 빠르게 확인할 수 있습니다.
- 수업 프로젝트에서 디버깅과 팀 협업이 쉽습니다.
- 현재 collector/backend가 MQTT JSON payload를 받도록 이미 구성되어 있습니다.

C/C++ Pico SDK는 나중에 엄격한 타이밍, RTOS, 저수준 제어가 필요할 때 고려합니다.

## 장치 ID

| Board | Device ID | Zone |
| --- | --- | --- |
| Pico 1 | `pico-safe-001` | `room-1` |
| Pico 2 | `pico-safe-002` | `room-2` |
| Pico 3 | `pico-safe-003` | `room-3` |
| Pico 4 | `pico-safe-004` | `room-4` |

## 실행 전 검증

저장소 루트에서 실행합니다.

```bash
.venv/bin/python -m pytest
npm --prefix frontend run build
```

현재 검증 기준:

- Python test suite
- Frontend production build
- MQTT parser / heartbeat forwarding
- Pico firmware helper tests
- simulator 분리 테스트
