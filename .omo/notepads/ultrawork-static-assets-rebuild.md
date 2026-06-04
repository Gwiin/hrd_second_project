# Goal
objective: Improve the project by fixing a concrete, verified reliability issue end-to-end: backend app creation must tolerate frontend/dist being present while frontend/dist/assets is temporarily missing during Vite rebuild.
status: active

## Skills
- Superpowers using-superpowers: project requires applicable skills first.
- Superpowers brainstorming: user asked open-ended improvement; narrowed to concrete reliability defect found in evidence.
- Superpowers TDD: mandatory for bug fix.
- Superpowers verification-before-completion: required before completion claim.
- karpathy-guidelines: keep change surgical and verified.
- OMO programming: Python change in FastAPI backend.

## Scope
Distinct surfaces: backend static dashboard route, backend tests, HTTP manual QA.
Files expected: apps/backend/main.py, tests/test_backend.py, evidence/notepad only.
Plan agent: skipped because the selected change is now one narrow bug fix with one production file and one test file; no architecture decision remains.

## Success Criteria
Deliverable: backend no longer crashes when dist/index.html exists but dist/assets is temporarily absent during frontend rebuild.

Scenarios:
1. Happy path rebuild fallback
   - Automated test: tests/test_backend.py::test_dashboard_fallback_when_frontend_assets_are_mid_rebuild
   - RED evidence: `.venv/bin/python -m pytest tests/test_backend.py::test_dashboard_fallback_when_frontend_assets_are_mid_rebuild -q` failed with `TypeError: create_app() got an unexpected keyword argument 'frontend_dist'`.
   - GREEN evidence: same command passed `1 passed, 1 warning`.
   - Manual QA channel: HTTP call `curl -i http://127.0.0.1:8020/` to live app using temporary dist/index.html without assets.
   - Manual QA evidence: PASS, returned `HTTP/1.1 200 OK`, `content-type: application/json`, body `{"message":"Pico SafeRoom backend is running. Build the dashboard with npm --prefix frontend run build."}`.
2. Adjacent regression: normal API remains available when assets missing
   - Automated test: same test module existing tests/test_backend.py::test_health_reports_level1_processes plus targeted run.
   - RED/GREEN evidence: full `.venv/bin/python -m pytest` passed `80 passed, 1 warning`.
   - Manual QA channel: HTTP curl /api/health on same live app; PASS if 200 and app Pico SafeRoom.
   - Manual QA evidence: PASS, `curl -i http://127.0.0.1:8020/api/health` returned `HTTP/1.1 200 OK` and JSON with `"app":"Pico SafeRoom"`.
3. Adjacent regression: frontend build still works after code change
   - Automated test: npm --prefix frontend run build
   - RED/GREEN evidence: `npm --prefix frontend run build` passed.
   - Manual QA channel: HTTP curl / after normal built dist; PASS if index HTML served or fallback only under missing assets scenario.
   - Manual QA evidence: PASS, `curl -i http://127.0.0.1:8021/` returned `HTTP/1.1 200 OK`, `content-type: text/html; charset=utf-8`, and built asset links.

## Findings
- During previous verification, parallel pytest and Vite build raced: Vite removed frontend/dist/assets while frontend/dist still existed, causing Starlette StaticFiles to throw at app creation.
- Smallest fix: mount static assets only when both frontend_dist/index.html and frontend_dist/assets exist; otherwise serve existing fallback message.

## Cleanup
- QA server on port 8020 stopped with Ctrl-C; `lsof -nP -iTCP:8020 -sTCP:LISTEN` returned no listener.
- QA server on port 8021 stopped with Ctrl-C; `lsof -nP -iTCP:8021 -sTCP:LISTEN` returned no listener.
