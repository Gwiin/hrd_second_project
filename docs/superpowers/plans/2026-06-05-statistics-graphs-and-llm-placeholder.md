# Statistics Graphs And LLM Placeholder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add room-level environment visuals to the Statistics tab and a non-functional LLM chat placeholder to the Dashboard.

**Architecture:** Keep the change frontend-focused. Reuse existing `devices`, latest readings, and timeline data; render SVG/CSS charts without a charting dependency; add source-contract tests to prevent accidental real LLM integration.

**Tech Stack:** React, TypeScript, CSS, pytest source-contract tests, Vite build.

---

### Task 1: Frontend Contract Tests

**Files:**
- Modify: `tests/test_frontend_auth_gate.py`

- [ ] Add a failing test that checks for environment graph copy and component hooks.
- [ ] Add a failing test that checks for the LLM placeholder panel and confirms no real chat endpoint or model/API-key UI is present.
- [ ] Run `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py -k "environment_graphs or llm_placeholder" -q` and confirm RED.

### Task 2: Statistics Environment Visuals

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/language.ts`
- Modify: `frontend/src/App.css`

- [ ] Extend frontend reading/timeline types for timeline `value`, `unit`, and `measured_at`.
- [ ] Add environment sensor copy for gas and graph labels.
- [ ] Add helper functions for chart-safe numeric values, bar width, and trend path generation.
- [ ] Render latest room comparison meters from `devices` and `readings`.
- [ ] Render recent trend SVGs from reading timeline events.
- [ ] Preserve responsive behavior.

### Task 3: Dashboard LLM Placeholder

**Files:**
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/language.ts`
- Modify: `frontend/src/App.css`

- [ ] Add a dashboard panel under Blackbox timeline.
- [ ] Render prepared assistant-style messages and a disabled/local-only input area.
- [ ] Do not call any backend chat endpoint.
- [ ] Keep copy explicit that real LLM integration is not active.

### Task 4: Verification

**Files:**
- Evidence only.

- [ ] Run `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py -q`.
- [ ] Run `npm --prefix frontend run build`.
- [ ] Run `.venv/bin/python -m pytest -q` if targeted checks pass.
- [ ] Start backend with built frontend and capture browser screenshots for Statistics and Dashboard.
- [ ] Confirm port cleanup.
