# 2nd Project Guide

이 문서는 raw 문서를 기준으로 프로젝트 요구사항을 다시 정리한 가이드입니다.
핵심 기준은 다음 두 가지입니다.

- 필수 제한 사항은 최소한으로 고정한다.
- 나머지 설계, 프로토콜, 기능, 확장 방향은 모두 옵션으로 둔다.

## 1. 필수 제한 사항

아래 3가지는 반드시 지켜야 하는 프로젝트 제한 사항입니다.

### 1.1 Raspberry Pi Pico 2W 기반 기기 구현

- 실제 또는 가상 센서/디바이스는 Raspberry Pi Pico 2W를 중심으로 구현한다.
- 기기 펌웨어, 센서 입력, 네트워크 전송은 Pico 2W를 기준으로 설계한다.
- 다른 보드나 장비는 확장 옵션으로만 고려한다.

### 1.2 pywebview 기반 대시보드 구현

- 사용자 화면은 pywebview 기반 데스크톱 대시보드로 구현한다.
- 프론트엔드는 HTML, CSS, JavaScript 또는 React/Vite 조합을 사용할 수 있다.
- 브라우저 앱이 아니라 데스크톱 앱 형태의 실행 경험을 유지한다.

### 1.3 Micro-architecture 기반 멀티 프로세스 구조

- 시스템은 하나의 단일 프로세스로 만들지 않는다.
- collector, backend, core, worker, ui 같은 역할을 여러 프로세스로 나눈다.
- 프로세스 간 연동은 shared-memory 또는 pipe, TCP/IP stack 기반 통신으로 구현한다.
- 내부 메시지 흐름은 모듈 경계를 분리해서 유지한다.

## 2. 권장 기본 아키텍처

필수 제한 사항을 만족하는 최소 구조는 아래처럼 잡는다.

```text
Pico 2W Device
	↓
Collector Process
	↓ shared-memory / pipe / TCP-IP
Backend Process
	↓ WebSocket / HTTP API
pywebview Dashboard
```

이 구조는 이후 기능이 늘어나도 유지되는 최종 뼈대다.

## 3. 옵션 사항 분류 원칙

raw 문서의 나머지 내용은 모두 옵션 사항으로 분류한다.

- 구현 우선순위는 팀 상황에 따라 조정 가능하다.
- 단계별 확장은 가능하지만, 필수 구조를 바꾸지 않는다.
- 옵션 사항은 교육용 범위, 데모 범위, 상용 확장 범위로 나누어 선택한다.

## 4. 옵션 사항: IoT 센서 및 장치 아키텍처

아래 항목은 필수는 아니지만, 프로젝트가 성장할 때 채택할 수 있는 구조다.

- 고정된 센서 이벤트 모델 사용
- device / sensor / asset / site 계층 분리
- protocol adapter 패턴 적용
- normalization layer 도입
- device registry, asset registry, protocol registry 구성
- metadata, unit, quality, timestamp 표준화

예시 내부 센서 이벤트 구조:

```json
{
	"device_id": "pico-001",
	"sensor_id": "temp-01",
	"protocol": "mqtt",
	"value": 26.4,
	"unit": "celsius",
	"timestamp": "2026-06-01T10:00:00+09:00",
	"quality": "good"
}
```

## 5. 옵션 사항: 표준 프로토콜 연계

상용 IoT 제품 및 산업용 장비와의 연동은 옵션으로 둔다.

### 5.1 MQTT

- 기본 메시징 프로토콜로 채택 가능
- 센서 publish / subscribe 구조에 적합
- 교육용, 데모용, 경량 운영 환경에 적합

### 5.2 Matter

- 상용 IoT 제품 연동용 옵션 계층
- 스마트홈, 상용 디바이스, 브리지 기반 연동에 적합
- 프로젝트의 핵심 프로토콜이라기보다 연동 확장층으로 둔다

### 5.3 Mobius / oneM2M

- 표준 IoT 플랫폼 연계 옵션
- oneM2M 기반 자원 모델, 구독, 알림 연동을 고려한다
- 공공/표준 플랫폼 연계가 필요할 때 선택한다

### 5.4 산업용 프로토콜

- Modbus
- OPC-UA
- Serial
- BLE
- CAN

이들 프로토콜은 산업용 장비, 교육용 장치, 근거리 센서, 특수 장비를 연결할 때 선택한다.

## 6. 옵션 사항: 실시간 처리 및 메시징

실시간성은 필수는 아니지만, 시스템 확장 단계에서 매우 유용하다.

- WebSocket 기반 실시간 대시보드 갱신
- ZeroMQ 기반 프로세스 간 이벤트 버스
- message queue 기반 비동기 처리
- heartbeat 및 retry 정책
- trace_id 기반 요청 추적

## 7. 옵션 사항: Backend 확장 구조

백엔드는 초기에 단순하게 시작하고, 필요할 때만 확장한다.

- FastAPI 기반 HTTP API
- WebSocket 서버
- DB session 관리
- process manager
- IPC client
- device service
- sensor service
- schema validation

## 8. 옵션 사항: Frontend 확장 구조

pywebview 대시보드는 다음 요소를 필요에 따라 포함할 수 있다.

- device list
- sensor chart
- alert panel
- system log
- settings panel
- diagnostics
- asset map
- twin viewer

## 9. 옵션 사항: Database 및 저장소

저장소는 MVP 이후 점진적으로 확장한다.

- SQLite: 개발 및 로컬 실습
- PostgreSQL: 운영 및 다중 사용자
- TimescaleDB 또는 InfluxDB: 시계열 데이터
- Redis: 캐시 및 실시간 상태

권장 테이블 예시:

- sites
- zones
- assets
- devices
- sensors
- sensor_readings
- device_protocols
- protocol_messages
- device_adapters

## 10. 옵션 사항: 에러 처리 및 로그

프로젝트 품질을 올리기 위한 선택 사항이다.

- 공통 에러 포맷 정의
- device offline, core timeout, IPC broken pipe 처리
- 로그 레벨 분리
- 파일 로그와 UI 로그 패널 분리
- crash dump 또는 stderr 캡처

## 11. 옵션 사항: 보안 및 운영

상용화를 고려하면 아래 항목을 추가할 수 있다.

- API 인증 토큰
- 로컬 포트 제한
- 장비 명령 권한 체크
- 설정 파일 보호
- 민감 정보 로그 제외
- C++ 또는 core command whitelist

## 12. 옵션 사항: C++ Core 또는 고성능 처리 계층

고성능 처리나 장비 제어가 필요할 때만 도입한다.

- 실시간 필터링
- 프로토콜 파싱
- 고속 계산
- 장비 제어 로직
- 하드웨어 연동

이 계층은 Python backend와 분리된 별도 프로세스로 두는 것이 좋다.

## 13. 옵션 사항: Real-time OS 연계

실시간 OS는 필수는 아니지만, 하드웨어 제어 정밀도가 필요하면 고려할 수 있다.

- Raspberry Pi Pico 2W의 펌웨어 실행 환경과 분리해서 생각한다.
- RTOS는 센서 주기, 제어 주기, 인터럽트 반응성이 중요한 경우에만 선택한다.
- FreeRTOS 또는 유사 RTOS를 옵션으로 두고, 상위 대시보드와는 IPC 또는 네트워크로 연결한다.
- 교육 단계에서는 bare metal 또는 경량 firmware로 시작하고, 이후 RTOS로 확장할 수 있다.

## 14. 옵션 사항: 멀티플랫폼 구현

앱 실행 환경은 하나로 고정하지 않아도 된다.

- Windows
- Linux
- macOS
- 필요 시 embedded Linux 또는 kiosk 환경

pywebview와 Python backend를 중심으로 하면 데스크톱 멀티플랫폼 확장이 비교적 쉽다.

## 15. 옵션 사항: 팀 프로젝트 확장 로드맵

레벨별로 구조를 바꾸지 말고, 구현 깊이만 높인다.

### Level 1

- Pico 2W 기반 센서 출력
- pywebview 단일 화면
- 단순 collector / backend / dashboard 분리

### Level 2

- 센서 데이터 정규화
- DB 저장
- 기본 차트 표시

### Level 3

- MQTT 연동
- 프로세스 간 메시징 정리
- 장치 등록 구조 도입

### Level 4

- Matter 또는 Mobius 연계 옵션 검토
- protocol adapter 추가
- 실시간 상태 반영

### Level 5

- WebSocket 기반 실시간 관제
- 에러 처리와 로그 체계 강화

### Level 6 이후

- 산업용 프로토콜 확장
- RTOS 연계
- 멀티플랫폼 패키징
- AI, 협업, 디지털 트윈, 운영 포털 확장

## 16. 최종 정리

이 프로젝트의 핵심은 다음과 같이 정리할 수 있다.

1. 필수 제한 사항은 Pico 2W, pywebview, multi-process micro-architecture의 3가지로 고정한다.
2. raw 문서의 나머지 내용은 모두 옵션 사항으로 둔다.
3. IoT 센서 구조, Matter, Mobius, real-time OS, 멀티플랫폼은 확장 옵션으로 분리한다.
4. 낮은 레벨에서도 최종 구조를 유지하고, 구현 깊이만 단계적으로 높인다.
