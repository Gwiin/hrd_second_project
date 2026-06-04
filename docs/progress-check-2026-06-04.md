# Pico SafeRoom 중간점검 정리

작성일: 2026-06-04

## 1. 프로젝트 개요

Pico SafeRoom은 Raspberry Pi Pico 2W 기반의 다중 공간 안전 모니터링 시스템이다. 각 Pico는 센서값과 heartbeat를 MQTT로 발행하고, PC의 collector가 이를 FastAPI 백엔드로 전달한다. 대시보드는 실시간 센서 상태, 장비 생존 상태, 프로세스 상태, 알림, 로그, incident response 흐름을 보여준다.

핵심 데이터 흐름:

```text
Pico 2W 센서/heartbeat
  -> MQTT broker(amqtt, port 1883)
  -> MQTT collector
  -> FastAPI backend
  -> SQLite
  -> React dashboard
```

## 2. 현재 실행 구성

현재 로컬 PC에서 실행 중인 주요 구성은 다음과 같다.

```text
MQTT broker: amqtt, 0.0.0.0:1883
Backend: FastAPI/Uvicorn, http://127.0.0.1:8000
Collector: apps.collector.mqtt_client
Worker: apps.worker.main
Dashboard: http://127.0.0.1:8000
```

현재 PC의 MQTT broker IP로 사용하는 값:

```text
163.152.213.111
```

Pico 펌웨어의 MQTT 설정도 이 IP를 바라보도록 구성되어 있다.

## 3. 구현 완료된 주요 기능

### Backend

- FastAPI 기반 API 서버 구성
- SQLite 저장소 구성
- 센서 최신값 조회
- 센서 히스토리 조회
- 장비 목록 및 liveness 조회
- 프로세스 heartbeat 저장
- threshold 기반 alert 생성
- stale sensor alert 생성
- system log 저장
- timeline/blackbox 이벤트 제공
- 이메일 회원가입/로그인
- Google/Kakao social login callback 경로
- incident replay / guided response 기능 반영

### Frontend

- React/Vite 대시보드 구성
- 장비별 최신 센서값 표시
- Safety state 표시
- backend / collector / worker process 상태 표시
- Liveness 패널에서 device/process 분리 표시
- Recent alerts / System log / Blackbox timeline 표시
- 로그인 gate 적용
- incident response panel 반영

### MQTT / Collector

- 실제 Pico MQTT topic 수신
- sensor reading topic 처리

```text
saferoom/{zone_id}/{device_id}/sensors/{sensor_id}/reading
```

- device heartbeat topic 처리

```text
saferoom/{zone_id}/{device_id}/status
```

- collector process heartbeat 추가
- worker process heartbeat 추가
- collector/worker가 dashboard에서 `simulated`가 아니라 실제 `online/offline`으로 보이도록 수정

### Pico Firmware

- `main.py`, `payloads.py`, `sensors.py`, `config.py` 기반 MicroPython 펌웨어 구성
- Wi-Fi 접속
- MQTT 접속
- 센서값 publish
- device heartbeat publish
- Wi-Fi/MQTT 장애 후 재연결 루프 추가
- MicroPython boot 방식에 맞게 `main.py` 자동 실행 조건 보정

## 4. 최근 해결한 문제

### 4.1 Liveness에서 연결되지 않은 Pico가 online으로 보이던 문제

기존 로직은 `last_seen_at`이 없는 장비를 `online`으로 처리했다. 이 때문에 한 번도 heartbeat를 보낸 적 없는 `pico-safe-002~004`가 online처럼 보였다.

수정 후:

```text
last_seen_at 없음 -> offline
최근 heartbeat 있음 -> online
오래된 heartbeat -> offline
```

관련 파일:

```text
apps/backend/db/sqlite_repository.py
tests/test_backend.py
tests/test_sqlite_repository.py
```

### 4.2 collector / worker가 simulated로 표시되던 문제

기존 백엔드 기본값이 다음과 같았다.

```text
collector: simulated
worker: simulated
```

수정 후:

```text
collector: offline 기본값, heartbeat 수신 시 online
worker: offline 기본값, heartbeat 수신 시 online
```

관련 파일:

```text
apps/collector/mqtt_client.py
apps/worker/main.py
frontend/src/App.tsx
tests/test_collector_mqtt_client.py
tests/test_worker.py
```

### 4.3 Pico 펌웨어 자동 복구 문제

기존 펌웨어는 Wi-Fi/MQTT 연결이나 publish 중 예외가 발생하면 자동 복구가 약했다.

수정 후:

- Wi-Fi 연결 상태 재확인
- MQTT client 재생성
- publish 예외 발생 시 2초 후 재시도
- serial log 출력 추가
- `__name__ in ("__main__", "main")` 조건으로 MicroPython 자동 실행 보정

관련 파일:

```text
firmware/pico2w/main.py
tests/test_pico_firmware_main.py
```

## 5. 현재 하드웨어 상태

현재 Windows에서 정상 serial port로 인식되는 Pico는 `COM4` 하나이다.

```text
COM4: USB serial device
```

최근 `COM4` 보드는 사용자의 요청에 따라 다음 역할로 설정하여 펌웨어를 올렸다.

```text
DEVICE_ID = "pico-safe-004"
ZONE_ID = "room-4"
MQTT_HOST = "163.152.213.111"
MQTT_PORT = 1883
```

단, 최근 liveness snapshot에서는 다음처럼 보였다.

```text
pico-safe-001: online
pico-safe-002: offline
pico-safe-003: offline
pico-safe-004: offline
collector: online
worker: online
```

이 상태는 추가 확인이 필요하다. 가능한 원인은 다음과 같다.

- 다른 Pico가 아직 `pico-safe-001 / room-1` 설정으로 publish 중
- `COM4` Pico가 `pico-safe-004`로 publish하다가 센서/네트워크 문제로 중단
- 여러 보드 중 일부가 Windows serial port로 보이지 않음
- 각 Pico에 고유한 `DEVICE_ID` / `ZONE_ID`가 아직 모두 반영되지 않음

## 6. 검증 결과

최근 원격 최신 병합 후 검증:

```text
pytest: 85 passed
frontend build: success
```

펌웨어 관련 검증:

```text
tests/test_pico_firmware_main.py
tests/test_pico_firmware_payloads.py
tests/test_pico_firmware_sensors.py
tests/test_pico_sensor_scaling.py
tests/test_mqtt_parser.py
```

MQTT 경로 검증:

```text
local publish/subscribe 성공
Pico topic -> collector -> backend 반영 성공
collector process heartbeat online 확인
worker process heartbeat online 확인
```

## 7. 원격 업데이트 반영 상태

원격 `origin/main` 최신 변경을 가져와 로컬 변경과 병합했다.

반영된 원격 주요 내용:

- incident replay / guided response 관련 backend/frontend 추가
- incident response panel 추가
- 관련 테스트 추가
- README 및 계획 문서 업데이트

로컬 변경도 유지했다.

유지된 로컬 주요 변경:

- device liveness offline 기본값 수정
- collector/worker heartbeat 추가
- Pico 펌웨어 재연결 루프 추가
- Pico firmware main 테스트 추가
- worker heartbeat 테스트 추가

아직 커밋하지 않은 로컬 변경이 남아 있다.

## 8. 중간점검에서 설명할 핵심 포인트

1. 단순 센서 표시가 아니라 장비 heartbeat와 process heartbeat까지 포함한 runtime monitoring 구조를 만들었다.
2. Simulator 경로와 실제 Pico MQTT 경로를 분리했다.
3. 실제 보드에서는 `pico-safe-001~004`가 고유 ID를 가져야 하며, 이 ID가 dashboard liveness의 기준이 된다.
4. MQTT broker는 PC에서 실행되고 Pico는 PC IP와 1883 포트로 publish한다.
5. 연결이 끊긴 장비는 `offline`으로 표시되도록 liveness 신뢰도를 개선했다.
6. collector/worker도 실제 heartbeat 기반으로 상태가 표시되도록 개선했다.
7. 원격 최신 incident response 기능을 병합했고, 기존 로컬 수정도 유지했다.
8. 현재 남은 주요 과제는 4대 Pico 전체를 Windows에서 안정적으로 인식시키고, 각 보드에 고유 config를 올리는 것이다.

## 9. 남은 작업

- Pico 1~4 각각을 serial port로 안정적으로 인식시키기
- 각 보드별 config 업로드

```text
pico-safe-001 / room-1
pico-safe-002 / room-2
pico-safe-003 / room-3
pico-safe-004 / room-4
```

- 각 보드 reset 후 MQTT broker connection log 확인
- dashboard에서 4대 모두 online 확인
- 센서별 실제값 범위 확인
- 필요 시 Pico별 센서 enable/disable 설정 분리
- 현재 로컬 변경사항 정리 후 커밋 여부 결정

## 10. 데모 순서 제안

1. `amqtt`, backend, collector, worker 실행 상태 확인
2. dashboard 접속

```text
http://127.0.0.1:8000
```

3. process 상태가 `online`인지 확인
4. Pico heartbeat가 들어오면 Liveness에서 해당 Pico가 `online`으로 바뀌는지 확인
5. 센서값 publish 시 Latest readings 변화 확인
6. alert 조건에 해당하는 값이 들어왔을 때 Recent alerts / timeline 반영 확인
7. incident response panel 기능 설명

