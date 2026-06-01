# Pico SafeRoom Level 3 Pico MQTT Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a testable MQTT collector path and Pico 2W MicroPython firmware scaffold for the four real device identities.

**Architecture:** Keep `/internal/events` as the backend ingest boundary. Add MQTT parsing in `apps/collector/mqtt_parser.py`, MQTT subscription/posting in `apps/collector/mqtt_client.py`, and firmware files under `firmware/pico2w/`.

**Tech Stack:** Python 3.11.15, Pydantic, pytest, paho-mqtt for the runtime collector, MicroPython on Raspberry Pi Pico 2W.

---

### Task 1: MQTT Parser

**Files:**
- Create: `apps/collector/mqtt_parser.py`
- Test: `tests/test_mqtt_parser.py`

- [ ] Write tests for valid reading topic conversion to `SensorEvent`.
- [ ] Write tests for invalid reading topic rejection.
- [ ] Run `.venv/bin/python -m pytest tests/test_mqtt_parser.py -v` and confirm failure.
- [ ] Implement topic parsing and payload normalization.
- [ ] Re-run `.venv/bin/python -m pytest tests/test_mqtt_parser.py -v` and confirm pass.

### Task 2: MQTT Collector Runtime

**Files:**
- Create: `apps/collector/mqtt_client.py`
- Modify: `requirements.txt`

- [ ] Add `paho-mqtt` to runtime requirements.
- [ ] Implement an MQTT callback that parses readings and posts them to the backend.
- [ ] Keep simulator collector unchanged.

### Task 3: Pico Firmware Scaffold

**Files:**
- Create: `firmware/pico2w/README.md`
- Create: `firmware/pico2w/config.example.py`
- Create: `firmware/pico2w/main.py`

- [ ] Add placeholder-only config for Wi-Fi, MQTT host, and device identity.
- [ ] Add MicroPython firmware that publishes readings and heartbeat topics.
- [ ] Ensure no real credentials are committed.

### Task 4: Full Validation

**Files:**
- No additional files.

- [ ] Run `.venv/bin/python -m pytest`.
- [ ] Run `npm --prefix frontend run build`.
- [ ] Run `git status --short` and review changed files.
