# Pico SafeRoom ?ㅼ튂 諛??ㅽ뻾 ?덈궡

??臾몄꽌????먯씠 媛쒕컻 ?섍꼍??留뚮뱾怨? backend/dashboard/MQTT collector/desktop launcher瑜??ㅽ뻾?섍린 ?꾪븳 ?쒓뎅???덈궡?낅땲??

## ?꾩옱 ?ы븿??湲곕뒫

- FastAPI backend
- SQLite ??μ냼
- React/Vite dashboard
- pywebview desktop launcher
- 4媛?Pico 2W ?μ튂 ID ?깅줉
- MQTT reading collector
- device heartbeat / process heartbeat
- threshold alert / stale sensor alert
- email ?뚯썝媛??濡쒓렇??
- Pico 2W MicroPython firmware
- ?ㅼ젣 ?쇱꽌 諛곗꽑 臾몄꽌? 洹몃┝

## Python 媛?곹솚寃?留뚮뱾湲?

???꾨줈?앺듃??Python 3.11???ъ슜?⑸땲??

macOS/Linux:

```bash
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
npm install --prefix frontend
```

Windows PowerShell:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm.cmd install --prefix frontend
```

PowerShell?먯꽌 `npm.ps1` ?ㅽ뻾??留됲엳硫?`npm.cmd`瑜??ъ슜?⑸땲??

## 寃利?紐낅졊

macOS/Linux:

```bash
.venv/bin/python -m pytest
npm --prefix frontend run build
```

Windows PowerShell:

```powershell
New-Item -ItemType Directory -Force data | Out-Null
$env:TEMP = (Resolve-Path data).Path
$env:TMP = (Resolve-Path data).Path
.\.venv\Scripts\python.exe -m pytest -p no:cacheprovider --basetemp=data\pytest-temp
npm.cmd --prefix frontend run build
```

## Backend? Dashboard ?ㅽ뻾

癒쇱? frontend瑜?build?⑸땲??

```bash
npm --prefix frontend run build
```

Backend ?ㅽ뻾:

macOS/Linux:

```bash
.venv/bin/python -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
```

釉뚮씪?곗??먯꽌 ?닿린:

```text
http://127.0.0.1:8000
```

## 濡쒓렇???ㅼ젙

?쇰컲 ?뚯썝媛?낃낵 濡쒓렇?몄? email/password濡?諛붾줈 ?ъ슜?????덉뒿?덈떎. 鍮꾨?踰덊샇??SQLite??plain text濡???ν븯吏 ?딄퀬 hash濡???ν빀?덈떎.


```text
http://127.0.0.1:8000/api/auth/social/google/callback
http://127.0.0.1:8000/api/auth/social/kakao/callback
```

.env example:

```dotenv
PICO_AUTH_REDIRECT_BASE_URL="http://127.0.0.1:8000"
PICO_AUTH_GOOGLE_CLIENT_ID="your-google-client-id"
PICO_AUTH_GOOGLE_CLIENT_SECRET="your-google-client-secret"
PICO_AUTH_KAKAO_CLIENT_ID="your-kakao-client-id"
PICO_AUTH_KAKAO_CLIENT_SECRET="your-kakao-client-secret"
```

?ㅼ젣 secret 媛믪? git???щ━吏 ?딆뒿?덈떎.

## MQTT Collector ?ㅽ뻾

?ㅼ젣 Pico 2W瑜??ъ슜???뚮뒗 濡쒖뺄 MQTT broker瑜?癒쇱? ?ㅽ뻾?댁빞 ?⑸땲??

```bash
.venv/bin/python -m apps.collector.mqtt_client --broker-host 127.0.0.1 --broker-port 1883 --backend-url http://127.0.0.1:8000
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.collector.mqtt_client --broker-host 127.0.0.1 --broker-port 1883 --backend-url http://127.0.0.1:8000
```

Collector媛 援щ룆?섎뒗 topic:

```text
saferoom/+/+/sensors/+/reading
saferoom/+/+/status
```

Reading topic? `/internal/events`濡??꾨떖?섍퀬, heartbeat topic? `/internal/heartbeats/device`濡??꾨떖?⑸땲??

## Desktop Launcher ?ㅽ뻾

湲곕낯 ?ㅽ뻾? ?ㅼ젣 Pico 2W + MQTT collector 紐⑤뱶?낅땲?? Simulator???먮룞?쇰줈 ?ㅽ뻾?섏? ?딆뒿?덈떎.

pywebview濡??닿린:

```bash
.venv/bin/python -m apps.desktop.app
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.desktop.app
```

釉뚮씪?곗?濡??닿린:

```bash
.venv/bin/python -m apps.desktop.app --open browser
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.desktop.app --open browser
```

Launcher??backend, MQTT collector, worker瑜?蹂꾨룄 process濡??쒖옉?⑸땲?? GUI ?섍꼍?대㈃ pywebview 李쎌씠 ?대━怨? `--open browser`瑜??ъ슜?섎㈃ 媛숈? dashboard瑜?釉뚮씪?곗??먯꽌 ?쎈땲??

## Simulator ?ㅽ뻾

Simulator??媛쒕컻/?뚯뒪???꾩슜?대ŉ ?ㅼ젣 Pico 2W ?ㅽ뻾 寃쎈줈? 遺꾨━?섏뼱 ?덉뒿?덈떎. ?ㅼ젣 蹂대뱶 諛쒗몴???곕え?먯꽌???ㅽ뻾?섏? ?딆뒿?덈떎.

```bash
.venv/bin/python -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
```

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m apps.collector.main --backend-url http://127.0.0.1:8000 --interval 2
```

## Runtime ?뚯씪

| ?뚯씪/?대뜑 | ?ㅻ챸 |
| --- | --- |
| `data/saferoom.db` | SQLite database |
| `logs/saferoom.log` | 媛쒕컻?먯슜 log file |
| `frontend/dist/` | frontend build output |
| `firmware/pico2w/config.example.py` | Pico ?ㅼ젙 ?덉떆 |
| `firmware/pico2w/config.py` | ?ㅼ젣 Pico??蹂듭궗??local ?ㅼ젙 ?뚯씪 |

`data/`, `logs/`, `frontend/dist/`, `firmware/pico2w/config.py`??git???щ━吏 ?딆뒿?덈떎.

## Pico 愿??臾몄꽌

- 湲곕낯 ?뚯썾???덈궡: [firmware/pico2w/README.md](firmware/pico2w/README.md)
- ?ㅼ젣 ?쇱꽌 諛곗꽑 ?덈궡: [firmware/pico2w/README.real-sensors.md](firmware/pico2w/README.real-sensors.md)

