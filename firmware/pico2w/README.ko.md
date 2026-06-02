# Pico SafeRoom Pico 2W 펌웨어 안내

이 폴더는 Raspberry Pi Pico 2W 4대에 올릴 **MicroPython 펌웨어**를 포함합니다.

실제 센서 배선 그림과 자세한 연결 방법은 [README.real-sensors.md](README.real-sensors.md)를 읽으세요.

## 펌웨어 파일

Pico에 복사해야 하는 파일:

```text
main.py
payloads.py
sensors.py
config.py
```

`config.py`는 `config.example.py`를 복사해서 만든 뒤 각 Pico에 맞게 수정합니다.

## 장치 ID

| Pico | `DEVICE_ID` | `ZONE_ID` |
| --- | --- | --- |
| Pico 1 | `pico-safe-001` | `room-1` |
| Pico 2 | `pico-safe-002` | `room-2` |
| Pico 3 | `pico-safe-003` | `room-3` |
| Pico 4 | `pico-safe-004` | `room-4` |

## 설정 순서

1. Pico 2W에 MicroPython firmware를 설치합니다.
2. `config.example.py`를 `config.py`로 복사합니다.
3. `config.py`에 Wi-Fi SSID/password와 MQTT broker IP를 입력합니다.
4. 각 보드에 맞는 `DEVICE_ID`, `ZONE_ID`를 설정합니다.
5. `main.py`, `payloads.py`, `sensors.py`, `config.py`를 Pico 파일 시스템에 복사합니다.
6. Pico를 재시작합니다.

## MQTT Topic

센서값 publish topic:

```text
saferoom/{ZONE_ID}/{DEVICE_ID}/sensors/{sensor_id}/reading
```

Heartbeat publish topic:

```text
saferoom/{ZONE_ID}/{DEVICE_ID}/status
```

## Simulator와 실제 펌웨어 차이

- Simulator: PC에서 실행, `apps/collector/simulator.py`, protocol은 `mock`입니다.
- 실제 Pico firmware: Pico 2W에서 실행, `firmware/pico2w/`, MQTT로 실제 센서값을 publish합니다.
