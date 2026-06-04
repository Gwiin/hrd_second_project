# Pico SafeRoom Incident Replay + Guided Response Differentiator

## TL;DR
> **Summary**: Add a demoable differentiator that turns Pico SafeRoom from a sensor dashboard into an incident-response system: each real threshold alert can show deterministic guidance, capture operator response evidence, and replay the surrounding safety timeline.
> **Deliverables**:
> - Backend incident guidance and response persistence
> - `GET /api/alerts/{alert_id}/replay` derived replay endpoint
> - `POST /api/alerts/{alert_id}/ack` upgraded to accept checklist/note/evidence text
> - Dashboard incident workflow reusing the existing alerts/timeline region
> - Korean and English demo docs explaining the differentiator
> **Effort**: Medium
> **Parallel**: YES - 3 waves
> **Critical Path**: Task 1 -> Task 3 -> Task 5 -> Task 8

## Context
### Original Request
The user asked: "I want to have 차별점 with other simillar projects in this project."

### Interview Summary
No blocking interview was needed after repo exploration. The current project is already a strong local IoT safety monitor, so the plan chooses a buildable differentiator rather than another generic dashboard feature.

### Research Findings
- `README.ko.md:14` defines the current real-sensor flow: Pico 2W -> MQTT Broker -> MQTT Collector -> FastAPI -> SQLite -> WebSocket -> React/Vite Dashboard.
- `doc/project_plan.md:20` defines the existing goal as sensor collection, alerting, heartbeat/offline detection, and dashboard display.
- `plan.md:28` already has an unresolved checklist item: choose a clear differentiation direction beyond a generic IoT dashboard.
- `docs/superpowers/UPDATE_HISTORY.md:9` says Level 1 through Level 5D monitoring, alert, heartbeat, log, auth, real-board launcher, and dashboard work is already complete.
- `apps/backend/main.py:56` exposes the current API surface; `apps/backend/main.py:176` has the existing alert acknowledge endpoint.
- `apps/backend/store.py:133` computes safety state from gas and temperature thresholds.
- `apps/backend/db/sqlite_repository.py:259` returns persisted alerts plus computed stale alerts; computed stale alerts can have `alert_id = null`.
- `frontend/src/App.tsx:175` owns the current dashboard state and already fetches health, devices, readings, logs, alerts, timeline, and liveness.
- Public similar IoT safety projects commonly stop at sensor publishing, MQTT dashboards, smoke/gas alerts, and notification-style demos. This repo should differentiate by proving incident handling, not merely showing another graph.

### Metis Review (gaps addressed)
- Persistence conflict resolved: use a new additive `incident_responses` table keyed by `alert_id`; do not modify existing `alerts` columns.
- Replay ambiguity resolved: `GET /api/alerts/{alert_id}/replay` derives a replay from current persisted readings, the alert row, logs, liveness, and timeline. It does not store full snapshot blobs.
- Stale alert ambiguity resolved: computed stale alerts with `alert_id = null` remain visible but are not replayable or acknowledgeable.
- WebSocket scope resolved: do not add alert WebSocket events in this plan; existing polling/refresh behavior remains acceptable.
- Guidance source resolved: deterministic backend catalog by alert code. No AI and no external provider.
- Evidence scope resolved: plain text only, 500-character maximum.
- UI ownership resolved: reuse the existing recent-alerts/timeline dashboard area as an incident workflow, not a new page.

## Work Objectives
### Core Objective
Make Pico SafeRoom clearly different from similar projects by adding a visible incident-response loop: alert -> recommended action -> checklist -> evidence note -> replayable timeline.

### Deliverables
- Deterministic response guidance catalog for known alert codes.
- Additive SQLite persistence for incident responses.
- Backend API contracts for alert replay and ack-with-response.
- Frontend incident panel integrated into the existing dashboard.
- Documentation and demo script proving why this is differentiated.

### Definition of Done (verifiable conditions with commands)
- Backend tests pass:
  ```bash
  .venv/bin/python -m pytest tests/test_backend.py tests/test_sqlite_repository.py -v
  ```
- Frontend static/contract tests pass:
  ```bash
  .venv/bin/python -m pytest tests/test_frontend_auth_gate.py -v
  ```
- Full Python suite passes:
  ```bash
  .venv/bin/python -m pytest -v
  ```
- Frontend build passes:
  ```bash
  npm --prefix frontend run build
  ```
- Manual HTTP QA captures a threshold alert, replay payload, ack response, and post-ack replay state:
  ```bash
  mkdir -p .omo/evidence
  DB_PATH="$(mktemp -t saferoom-incident-XXXXXX.db)"
  .venv/bin/python -m uvicorn apps.backend.main:create_app --factory --host 127.0.0.1 --port 8011 > .omo/evidence/task-8-server.log 2>&1 &
  SERVER_PID=$!
  curl -i http://127.0.0.1:8011/api/health > .omo/evidence/task-8-health.txt
  curl -i -X POST http://127.0.0.1:8011/internal/events -H 'Content-Type: application/json' -d '{"event_id":"incident-demo-gas","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"demo":true}}' > .omo/evidence/task-8-ingest.txt
  curl -i http://127.0.0.1:8011/api/alerts > .omo/evidence/task-8-alerts.txt
  curl -i http://127.0.0.1:8011/api/alerts/1/replay > .omo/evidence/task-8-replay-before-ack.txt
  curl -i -X POST http://127.0.0.1:8011/api/alerts/1/ack -H 'Content-Type: application/json' -d '{"checklist":["evacuate","ventilate","inspect_sensor"],"note":"Demo operator confirmed gas threshold and opened ventilation.","evidence":"Window opened, sensor cable checked."}' > .omo/evidence/task-8-ack.txt
  curl -i http://127.0.0.1:8011/api/alerts/1/replay > .omo/evidence/task-8-replay-after-ack.txt
  kill "$SERVER_PID"
  rm -f "$DB_PATH"
  ```

### Must Have
- The differentiator must be observable in UI and API, not only in docs.
- The implementation must preserve current sensor ingest, WebSocket reading, auth gate, and alert list behavior.
- The new response workflow must be deterministic and classroom-demo friendly.
- All tests must be written before production changes when executing this plan.

### Must NOT Have
- No AI/LLM assistant.
- No new hardware actuator requirement.
- No cloud notification provider.
- No PostgreSQL/TimescaleDB migration.
- No live OAuth provider credential work.
- No real four-board bring-up requirement.
- No alert WebSocket expansion.
- No broad dashboard redesign.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: TDD with existing `pytest` and frontend production build.
- QA policy: Every task has agent-executed scenarios.
- Evidence: `.omo/evidence/task-{N}-{slug}.{ext}`.

## Execution Strategy
### Parallel Execution Waves
> Target: 5-8 tasks per wave. <3 per wave except final means under-splitting.

Wave 1: Task 1, Task 2, Task 4
Wave 2: Task 3, Task 6, Task 7
Wave 3: Task 5, Task 8

### Dependency Matrix (full, all tasks)
| Task | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1. Response guidance catalog | None | 3, 5, 8 | 2, 4 |
| 2. Incident response persistence | None | 3, 5, 8 | 1, 4 |
| 3. Replay and ack API contracts | 1, 2 | 5, 8 | 6, 7 |
| 4. Frontend incident contract tests | None | 5 | 1, 2 |
| 5. Dashboard incident workflow | 1, 2, 3, 4 | 8 | None |
| 6. Documentation/demo script | 1, 3 | 8 | 7 |
| 7. Regression guardrails | 1, 2 | 8 | 3, 6 |
| 8. Final verification and evidence capture | 3, 5, 6, 7 | None | None |

## TODOs
> Implementation + Test = ONE task. Never separate.
> EVERY task MUST have: References + Acceptance Criteria + QA Scenarios.

- [ ] 1. Add deterministic response guidance catalog

  **What to do**: Add a small backend response catalog for persisted threshold alert codes: `gas.warning`, `gas.critical`, `temperature.warning`, `temperature.critical`. Each entry must include `summary`, `recommended_action`, and `checklist` item ids/labels. Keep the catalog deterministic and local.
  **Must NOT do**: Do not call an AI API, do not add external dependencies, and do not make guidance configurable yet.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 3, 5, 8 | Blocked By: none

  **References**:
  - Pattern: `apps/backend/store.py:133` - current safety thresholds.
  - Pattern: `apps/backend/db/sqlite_repository.py:66` - alert code generation path.
  - Test pattern: `tests/test_backend.py:152` - threshold alert test style.

  **Acceptance Criteria**:
  - [ ] A backend unit/API test first fails, then passes, proving `gas.critical` exposes `recommended_action` and checklist ids.
  - [ ] Unknown alert codes return a safe fallback guidance object.
  - [ ] Guidance appears in replay/API payloads only after Task 3 wires API contracts.

  **QA Scenarios**:
  ```
  Scenario: Gas critical guidance exists
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_backend.py::test_gas_critical_alert_includes_response_guidance -v
    Expected: PASS after implementation; RED before implementation because guidance is missing
    Evidence: .omo/evidence/task-1-guidance-test.txt

  Scenario: Unknown code fallback
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_backend.py::test_unknown_alert_code_uses_safe_guidance_fallback -v
    Expected: PASS after implementation; response includes inspect_area/check_sensor style fallback
    Evidence: .omo/evidence/task-1-guidance-fallback.txt
  ```

  **Commit**: YES | Message: `feat(incidents): add deterministic response guidance` | Files: `apps/backend/store.py`, `apps/backend/db/sqlite_repository.py` or a new backend helper, `tests/test_backend.py`

- [ ] 2. Persist incident response acknowledgements without altering existing alert columns

  **What to do**: Add an additive `incident_responses` table in SQLite initialization with `alert_id`, `checklist_json`, `note`, `evidence`, `created_at`, and `updated_at`. Persist one response row per alert. Use `INSERT ... ON CONFLICT(alert_id) DO UPDATE` so repeated acknowledgement updates note/checklist/evidence while keeping the alert acknowledged.
  **Must NOT do**: Do not add formal migration tooling; do not modify existing `alerts` table columns; do not support file uploads.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 3, 5, 8 | Blocked By: none

  **References**:
  - Pattern: `apps/backend/db/sqlite_repository.py:18` - repository initialization style.
  - Pattern: `apps/backend/db/sqlite_repository.py:276` - current ack logic.
  - Risk: existing DBs need additive table creation; do not rely on altering existing columns.

  **Acceptance Criteria**:
  - [ ] Repository test first fails, then passes, proving ack response data persists across app/repository instances.
  - [ ] Re-acknowledging the same alert updates the response row and remains idempotent.
  - [ ] Note and evidence strings are trimmed and capped at 500 characters.

  **QA Scenarios**:
  ```
  Scenario: Persist ack response across app instances
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_sqlite_repository.py::test_incident_response_persists_across_repository_instances -v
    Expected: PASS after implementation; second repository instance reads the same checklist/note/evidence
    Evidence: .omo/evidence/task-2-persistence.txt

  Scenario: Re-ack updates response
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_sqlite_repository.py::test_incident_response_reack_updates_existing_row -v
    Expected: PASS after implementation; latest note/evidence is returned
    Evidence: .omo/evidence/task-2-reack.txt
  ```

  **Commit**: YES | Message: `feat(incidents): persist alert response evidence` | Files: `apps/backend/db/sqlite_repository.py`, `apps/backend/store.py`, `tests/test_sqlite_repository.py`

- [ ] 3. Add replay and ack-with-response API contracts

  **What to do**: Upgrade `POST /api/alerts/{alert_id}/ack` to accept optional JSON body `{ "checklist": string[], "note": string, "evidence": string }`. Add `GET /api/alerts/{alert_id}/replay`. Replay returns `{ alert, guidance, response, related_events }`, where `related_events` is derived from existing timeline/readings/logs/liveness data around the alert. Unknown alert returns 404. Computed stale alerts with `alert_id = null` are not routed.
  **Must NOT do**: Do not add alert WebSocket events. Do not require authentication for this task; preserve current ack auth behavior.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 5, 8 | Blocked By: 1, 2

  **References**:
  - Route pattern: `apps/backend/main.py:176` - current ack endpoint.
  - Route pattern: `apps/backend/main.py:93` - timeline endpoint.
  - Store pattern: `apps/backend/store.py:80` - alerts and ack store methods.
  - Test pattern: `tests/test_backend.py:166` - current ack API test.

  **Acceptance Criteria**:
  - [ ] API test first fails, then passes, proving ack accepts checklist/note/evidence and returns persisted response.
  - [ ] API test first fails, then passes, proving replay returns alert, guidance, response, and related timeline events for a gas critical alert.
  - [ ] Replay for unknown alert id returns 404.
  - [ ] Ack with invalid payload, such as checklist not list of strings or note over 500 characters, returns 422 or standard validation error.

  **QA Scenarios**:
  ```
  Scenario: Replay returns incident bundle
    Tool: curl
    Steps: Run backend on 127.0.0.1:8011; POST gas critical JSON to /internal/events; curl -i http://127.0.0.1:8011/api/alerts/1/replay
    Expected: HTTP/1.1 200 and JSON includes "alert", "guidance", "related_events"
    Evidence: .omo/evidence/task-3-replay-curl.txt

  Scenario: Ack with response evidence
    Tool: curl
    Steps: curl -i -X POST http://127.0.0.1:8011/api/alerts/1/ack -H 'Content-Type: application/json' -d '{"checklist":["evacuate","ventilate"],"note":"Operator opened window.","evidence":"Window open confirmed."}'
    Expected: HTTP/1.1 200 and JSON response includes status "acknowledged" plus response.note
    Evidence: .omo/evidence/task-3-ack-curl.txt
  ```

  **Commit**: YES | Message: `feat(incidents): expose alert replay API` | Files: `apps/backend/main.py`, `apps/backend/store.py`, `apps/backend/db/sqlite_repository.py`, `tests/test_backend.py`

- [ ] 4. Add frontend contract tests for the incident workflow

  **What to do**: Add static frontend tests that fail first and require the dashboard source to include incident workflow affordances: response checklist labels, replay action, response note field, and calls to `/api/alerts/${alertId}/replay` and `/api/alerts/${alertId}/ack`.
  **Must NOT do**: Do not make brittle visual CSS assertions beyond naming key classes/strings.

  **Parallelization**: Can Parallel: YES | Wave 1 | Blocks: 5 | Blocked By: none

  **References**:
  - Pattern: `tests/test_frontend_auth_gate.py:9` - current static frontend contract test style.
  - Current type: `frontend/src/App.tsx:39` - alert type to extend later.
  - Current state surface: `frontend/src/App.tsx:175` - dashboard component.

  **Acceptance Criteria**:
  - [ ] Static test first fails, then passes, proving the incident panel has replay and response evidence UI hooks.
  - [ ] Static test first fails, then passes, proving frontend fetches replay and ack endpoints.

  **QA Scenarios**:
  ```
  Scenario: Incident UI hooks are present
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_dashboard_has_incident_response_workflow_hooks -v
    Expected: PASS after implementation; source includes Replay incident, response note, and checklist hooks
    Evidence: .omo/evidence/task-4-frontend-contract.txt

  Scenario: Frontend endpoint contracts are present
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_dashboard_uses_incident_replay_and_ack_endpoints -v
    Expected: PASS after implementation; source fetches /api/alerts/${alertId}/replay and /api/alerts/${alertId}/ack
    Evidence: .omo/evidence/task-4-frontend-endpoints.txt
  ```

  **Commit**: YES | Message: `test(frontend): pin incident workflow contracts` | Files: `tests/test_frontend_auth_gate.py`

- [ ] 5. Implement dashboard incident workflow in the existing alerts/timeline area

  **What to do**: Extend `frontend/src/App.tsx` to select a persisted alert, fetch replay details, render deterministic guidance, show checklist items, allow a plain text note/evidence entry, submit ack-with-response, and show related replay events. Keep computed stale alerts visible but label them as not replayable when `alert_id` is null. Use the existing visual system and avoid broad redesign.
  **Must NOT do**: Do not create a separate route/page. Do not replace the auth gate. Do not remove existing alerts/timeline/log/liveness sections.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: 8 | Blocked By: 1, 2, 3, 4

  **References**:
  - Current alert type: `frontend/src/App.tsx:39`.
  - Current dashboard state: `frontend/src/App.tsx:175`.
  - Current data fetch pattern: `frontend/src/App.tsx:207`.
  - Current auth gate tests: `tests/test_frontend_auth_gate.py:9`.
  - Design guardrail: `docs/superpowers/UPDATE_HISTORY.md:20` - keep approved light Liquid Glass dashboard direction and information structure.

  **Acceptance Criteria**:
  - [ ] Frontend build passes.
  - [ ] Existing auth gate tests still pass.
  - [ ] Incident panel shows a selected gas critical alert guidance and replay events.
  - [ ] A stale computed alert with null id is visible but not replayable.
  - [ ] Acknowledging an alert updates displayed status/response without reloading the page.

  **QA Scenarios**:
  ```
  Scenario: Frontend compiles with incident workflow
    Tool: bash
    Steps: npm --prefix frontend run build
    Expected: exit 0
    Evidence: .omo/evidence/task-5-frontend-build.txt

  Scenario: Browser incident workflow smoke
    Tool: browser use
    Steps: Start backend + built frontend on 127.0.0.1:8011; sign in or use test session path if auth fixture exists; inject gas critical event by curl; open http://127.0.0.1:8011/; click the persisted alert; click Replay incident; fill response note and evidence; submit acknowledge.
    Expected: Page shows guidance checklist, replay timeline, and acknowledged response state
    Evidence: .omo/evidence/task-5-browser-incident.png and .omo/evidence/task-5-browser-actions.txt
  ```

  **Commit**: YES | Message: `feat(frontend): add incident response workflow` | Files: `frontend/src/App.tsx`, `frontend/src/App.css`, `tests/test_frontend_auth_gate.py`

- [ ] 6. Document the differentiator and demo script

  **What to do**: Update `README.ko.md`, `README.md`, and `docs/superpowers/UPDATE_HISTORY.md` with a short section explaining the differentiator: Pico SafeRoom does not only monitor; it records incident response evidence and replays the safety timeline. Add exact demo steps using internal event posts/simulator, not real hardware.
  **Must NOT do**: Do not claim live four-board bring-up, live OAuth provider validation, cloud notification, or AI behavior.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8 | Blocked By: 1, 3

  **References**:
  - Existing README structure: `README.ko.md:1`.
  - Current validation commands: `README.ko.md:55`.
  - Update log current status style: `docs/superpowers/UPDATE_HISTORY.md:7`.
  - Current active plan blocker: `plan.md:28`.

  **Acceptance Criteria**:
  - [ ] Docs state the differentiator in one sentence in Korean and English.
  - [ ] Demo script includes exact HTTP commands to trigger a gas critical alert, replay it, acknowledge it with evidence, and replay again.
  - [ ] Docs clearly mark real hardware bring-up as separate from this differentiator demo.

  **QA Scenarios**:
  ```
  Scenario: Korean README has differentiator
    Tool: bash
    Steps: rg -n "Incident Replay|대응|증거|차별" README.ko.md
    Expected: Output includes the differentiator section
    Evidence: .omo/evidence/task-6-readme-ko.txt

  Scenario: Demo commands documented
    Tool: bash
    Steps: rg -n "/api/alerts/.*/replay|/api/alerts/.*/ack|incident-demo-gas" README.md README.ko.md docs/superpowers/UPDATE_HISTORY.md
    Expected: Output includes replay and ack demo commands
    Evidence: .omo/evidence/task-6-demo-docs.txt
  ```

  **Commit**: YES | Message: `docs(incidents): document response replay differentiator` | Files: `README.md`, `README.ko.md`, `docs/superpowers/UPDATE_HISTORY.md`, `plan.md`

- [ ] 7. Add regression guardrails for existing behavior

  **What to do**: Before and after implementation, run and preserve targeted tests for existing ingest, alerts, ack, WebSocket reading, auth gate, and import-no-DB behavior. If any fail, fix the regression within the task that caused it.
  **Must NOT do**: Do not weaken existing tests or change assertions to match broken behavior.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 8 | Blocked By: 1, 2

  **References**:
  - `tests/test_backend.py:100` - ingest updates latest readings.
  - `tests/test_backend.py:143` - importing backend does not create default DB.
  - `tests/test_backend.py:166` - ack alert current behavior.
  - `tests/test_backend.py:182` - WebSocket reading created.
  - `tests/test_frontend_auth_gate.py:9` - auth gate.

  **Acceptance Criteria**:
  - [ ] Targeted regression tests pass after the new incident feature.
  - [ ] Full suite passes before final verification.
  - [ ] No test is skipped, deleted, weakened, or marked xfail.

  **QA Scenarios**:
  ```
  Scenario: Backend regression set
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_backend.py::test_ingest_event_updates_latest_readings tests/test_backend.py::test_importing_backend_main_does_not_create_default_database tests/test_backend.py::test_ack_alert_api_updates_alert_status tests/test_backend.py::test_realtime_websocket_receives_reading_created -v
    Expected: exit 0
    Evidence: .omo/evidence/task-7-backend-regression.txt

  Scenario: Auth gate regression
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_frontend_auth_gate.py -v
    Expected: exit 0
    Evidence: .omo/evidence/task-7-auth-regression.txt
  ```

  **Commit**: NO | Message: `n/a` | Files: no direct files unless a regression is found

- [ ] 8. Final verification and real-surface evidence capture

  **What to do**: Run targeted tests, full tests, frontend build, `git diff --check`, and the manual HTTP/browser QA. Capture all outputs under `.omo/evidence/`. Clean up server process, temp DB, browser context, and any tmux sessions.
  **Must NOT do**: Do not claim done from tests alone. Do not leave runtime processes or temp files.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: none | Blocked By: 3, 5, 6, 7

  **References**:
  - Validation baseline: `README.ko.md:55`.
  - Active validation list: `plan.md:32`.
  - Manual QA policy: project AGENTS.md and active ultrawork instructions require real-surface evidence for user-facing behavior.

  **Acceptance Criteria**:
  - [ ] `.venv/bin/python -m pytest -v` exits 0.
  - [ ] `npm --prefix frontend run build` exits 0.
  - [ ] `git diff --check` exits 0.
  - [ ] HTTP QA artifacts show alert creation, replay, ack-with-response, and replay-after-ack.
  - [ ] Browser QA screenshot shows dashboard incident workflow.
  - [ ] Cleanup receipt records killed server PID, removed temp DB, closed browser context, and no leftover tmux sessions.

  **QA Scenarios**:
  ```
  Scenario: Full automated verification
    Tool: bash
    Steps: .venv/bin/python -m pytest -v && npm --prefix frontend run build && git diff --check
    Expected: all commands exit 0
    Evidence: .omo/evidence/task-8-full-verification.txt

  Scenario: Manual HTTP incident scenario
    Tool: HTTP call
    Steps: Use the exact curl sequence listed in Definition of Done against http://127.0.0.1:8011
    Expected: health 200, ingest 201, alerts 200 with gas.critical, replay 200 with guidance, ack 200 with response, replay-after-ack 200 with response
    Evidence: .omo/evidence/task-8-*.txt plus cleanup receipt
  ```

  **Commit**: NO | Message: `n/a` | Files: evidence only

## Final Verification Wave (MANDATORY - after ALL implementation tasks)
> ALL must APPROVE. Present consolidated results to user and get explicit "okay" before completing.
- [ ] F1. Plan Compliance Audit: verify every task has references, acceptance criteria, QA scenarios, and commit guidance.
- [ ] F2. Code Quality Review: run a reviewer on the implementation diff if this plan is executed.
- [ ] F3. Real Manual QA: capture HTTP and browser evidence for the incident workflow.
- [ ] F4. Scope Fidelity Check: confirm no AI, cloud notification, DB-engine migration, hardware bring-up, OAuth credential work, or alert WebSocket expansion was added.

## Commit Strategy
- Commit Task 1 through Task 6 as atomic conventional commits if the user approves committing.
- Do not commit Task 7 or Task 8 unless they require actual regression fixes or durable evidence docs.
- Suggested final branch message sequence:
  - `feat(incidents): add deterministic response guidance`
  - `feat(incidents): persist alert response evidence`
  - `feat(incidents): expose alert replay API`
  - `test(frontend): pin incident workflow contracts`
  - `feat(frontend): add incident response workflow`
  - `docs(incidents): document response replay differentiator`

## Success Criteria
- Pico SafeRoom can be presented as an incident-response system, not just an IoT dashboard.
- A gas or temperature threshold alert shows deterministic guidance and checklist.
- Operator response evidence can be saved through the ack endpoint and displayed afterward.
- Replay endpoint shows alert context and related timeline events.
- Dashboard exposes the incident workflow without breaking existing auth/realtime/dashboard behavior.
- Docs include a clear differentiator statement and exact demo commands.
- All automated and manual QA evidence is captured under `.omo/evidence/`.
