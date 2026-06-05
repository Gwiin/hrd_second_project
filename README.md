## 2차 프로젝트 개발 일지

팀원이 먼저 읽을 한국어 안내 문서: [README.ko.md](README.ko.md)


프로젝트 계획서 : [2차_2조_프로젝트_계획서](doc/2차_2조_프로젝트_계획서.hwp)
프로젝트 기술서 : [2차_2조_프로젝트_기술서.hwp](doc/2차_2조_프로젝트_기술서.hwp)
프로젝트 기술서 : [2차_2조_프로젝트_기술서.pdf](doc/2차_2조_프로젝트_기술서.pdf)



## Differentiator

Pico SafeRoom is not only an IoT sensor dashboard. Its Incident Replay + Guided Response flow lets a demo trigger a gas/temperature alert, review deterministic response guidance, save operator note/evidence on acknowledgement, and replay the related safety timeline.

Local HTTP demo:

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

Real four-board sensor bring-up and live OAuth credential verification remain separate field checks.

|일자|요일|시간|인원|내용|
|---|---|---|---|---|
|6/1|월|오전|전체|아이디어 회의|
|||오후|전체|아이디어 선정 및 역할 분담|
||||||
|6/2|화|오전|정귀인|Backend|
||||황지용|micropython pico2w 펌웨어|
||||박찬웅|Front-end|
||||박시영|c pico2w 펌웨어|
|||오후|정귀인|backend-frontend-pico 2w 연결 테스트|
||||황지용|pico 2w 센서 테스트|
||||박찬웅|social login(google) 추가|
||||박시영|pico 2w 센서 테스트|
||||||
|6/4|목|오전|정귀인||
||||황지용||
||||박찬웅||
||||박시영||
|||오후|정귀인||
||||황지용||
||||박찬웅||
||||박시영||
---
