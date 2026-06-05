# Pico SafeRoom Incident Drill Mode

## TL;DR
> Summary:      Turn the existing incident replay/guided response flow into an active operator drill: users select performed checklist actions, get deterministic response-quality feedback, and generate a compact incident command report.
> Deliverables:
> - Backend drill review helper derived from existing guidance and stored response evidence
> - `response_review` added to replay/ack payloads, plus a derived `/api/alerts/{alert_id}/report` endpoint
> - Interactive checklist, missed-action feedback, and report view in the existing incident response panel
> - English/Korean copy, styling, docs, TDD evidence, HTTP QA, and browser QA artifacts
> Effort:       Medium
> Risk:         Medium - central backend repository and central React incident panel are already large, so scoped changes and regression checks matter

## Scope
### Must have
- Build on the existing incident replay/guided response feature in `apps/backend/main.py:190`, `apps/backend/main.py:197`, `apps/backend/db/sqlite_repository.py:444`, and `frontend/src/IncidentResponsePanel.tsx:61`.
- Make the feature active, not passive: the UI must let the operator choose which checklist actions were actually completed instead of auto-submitting every guidance item from `frontend/src/IncidentResponsePanel.tsx:108`.
- Return deterministic drill feedback from the backend: completed checklist items, missed checklist items, completion ratio, status, score label, and next best action.
- Keep the response review derived from existing guidance plus existing `incident_responses.checklist_json` data from `apps/backend/db/sqlite_repository.py:676`; do not add a new database table unless a test proves derivation cannot meet the contract.
- Add a compact incident command report endpoint and UI section derived from replay data, response review, operator note/evidence, and the top related timeline events.
- Preserve existing alert replay, acknowledgement, stats, auth, realtime, and static dashboard behavior.
- Use TDD: every production change must have a failing test captured before implementation and a passing test captured after implementation.
- Use real-surface QA: HTTP for API behavior and Chrome-driven browser QA for dashboard behavior, with artifacts under `.omo/evidence/`.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not build another passive dashboard/statistics page.
- Do not add an LLM, OpenAI API call, chatbot, prompt template, embedding flow, or cloud dependency.
- Do not add SMS/email/push notifications, external provider accounts, actuator/buzzer control, or real four-board hardware bring-up.
- Do not change OAuth provider scope; Google/Kakao remain the only social providers and Apple is only visual style language if mentioned elsewhere.
- Do not change ingestion payloads from `shared/schemas/sensor_event.py`, MQTT topic contracts, firmware payloads, auth session behavior, or WebSocket message shape.
- Do not broadly redesign the dashboard; keep work scoped to the existing right-rail incident panel and minimal CSS additions.
- Do not edit `AGENTS.md`, `agent-map.md`, or `.omo/ulw-loop/`; they are existing dirty/user state.
- Do not commit without explicit user approval, even though each task includes an approval-gated commit instruction.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD + existing `pytest`, source-contract tests in `tests/test_frontend_auth_gate.py`, and `npm --prefix frontend run build`
- QA policy: every task has agent-executed scenarios
- Evidence: `.omo/evidence/task-<N>-<slug>.<ext>`

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. This scope is intentionally narrow enough that some dependency waves are smaller; do not merge unrelated tasks just to inflate wave size.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: Add deterministic incident drill review helper
- Task 4: Add frontend drill copy and source-contract guardrails

Wave 2 (after Wave 1):
- Task 2: depends [1]

Wave 3 (after Wave 2):
- Task 3: depends [1, 2]
- Task 5: depends [1, 2, 4]

Wave 4 (after Wave 3):
- Task 6: depends [3, 5]

Wave 5 (after Wave 4):
- Task 7: depends [2, 3, 5, 6]

Critical path: Task 1 -> Task 2 -> Task 3 -> Task 6 -> Task 7

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | 2, 3, 5 | 4 |
| 2    | 1          | 3, 5, 7 | none |
| 3    | 1, 2       | 6, 7 | 5 |
| 4    | none       | 5, 6 | 1 |
| 5    | 1, 2, 4    | 6, 7 | 3 |
| 6    | 3, 5       | 7 | none |
| 7    | 2, 3, 5, 6 | none | none |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Add deterministic incident drill review helper

  What to do: Add a backend helper in `apps/backend/incidents.py` that compares selected checklist ids against `guidance_for_code(code)["checklist"]`. The helper must return a JSON-safe review object:
  - `status`: `"not_started"`, `"partial"`, or `"complete"`
  - `completed_checklist`: selected known checklist ids in guidance order
  - `missed_checklist`: checklist item objects not selected
  - `unknown_checklist`: selected ids not present in guidance
  - `completion_ratio`: float rounded to 2 decimals
  - `score_label`: `"Not started"`, `"Partial response"`, or `"Response complete"`
  - `next_best_action`: first missed checklist label, or `"Response complete"`

  Must NOT do: Do not store review output in SQLite, do not add new dependencies, do not change guidance text, and do not make the review probabilistic.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [2, 3, 5] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `apps/backend/incidents.py:10` - existing `ChecklistItem` shape to reuse for missed items
  - Pattern:  `apps/backend/incidents.py:15` - existing `ResponseGuidance` contract to extend without breaking callers
  - Pattern:  `apps/backend/incidents.py:27` - deterministic guidance catalog by alert code
  - Pattern:  `apps/backend/incidents.py:74` - `guidance_for_code(code)` lookup seam
  - Test:     `tests/test_backend.py:300` - current guidance assertion style
  - External: `https://fastapi.tiangolo.com/tutorial/testing/` - FastAPI project already uses `TestClient`/pytest; keep tests ordinary pytest functions

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_incidents.py::test_review_response_marks_partial_gas_drill -v > .omo/evidence/task-1-review-partial-red.txt 2>&1` fails before implementation with missing import/function/assertion.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_incidents.py::test_review_response_marks_partial_gas_drill -v > .omo/evidence/task-1-review-partial-green.txt 2>&1` passes after implementation.
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_incidents.py::test_review_response_handles_not_started_response -v > .omo/evidence/task-1-review-not-started-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_incidents.py::test_review_response_handles_not_started_response -v > .omo/evidence/task-1-review-not-started-green.txt 2>&1` passes after implementation.
  - [ ] `completed_checklist` preserves guidance order even when input ids are unsorted.
  - [ ] Unknown checklist ids are reported in `unknown_checklist` and never counted as completed.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: partial gas drill review
    Tool:     bash
    Steps:    .venv/bin/python -m pytest tests/test_incidents.py::test_review_response_marks_partial_gas_drill -v
    Expected: PASS; assertion confirms selected ["evacuate"] yields status "partial", ratio 0.33, and missed ids ["ventilate", "inspect_sensor"].
    Evidence: .omo/evidence/task-1-review-partial-green.txt

  Scenario: empty response is not started
    Tool:     bash
    Steps:    .venv/bin/python -m pytest tests/test_incidents.py::test_review_response_handles_not_started_response -v
    Expected: PASS; assertion confirms empty checklist yields status "not_started", ratio 0.0, and next_best_action "Move people away from the room".
    Evidence: .omo/evidence/task-1-review-not-started-green.txt
  ```

  Commit: YES | Message: `feat(incidents): add deterministic drill review` | Files: [`apps/backend/incidents.py`, `tests/test_incidents.py`] | Approval-gated: ask before running `git commit`

- [ ] 2. Wire replay and acknowledgement APIs to return drill review

  What to do: Update `apps/backend/db/sqlite_repository.py`, `apps/backend/store.py`, and `apps/backend/main.py` so `GET /api/alerts/{alert_id}/replay` and `POST /api/alerts/{alert_id}/ack` include `response_review`. For ack, persist only known checklist ids; if the submitted checklist contains unknown ids for that alert code, return HTTP 422 with exact detail `Unknown checklist item: <id>`. Keep existing note/evidence validation via `AlertResponsePayload` and `clean_response_text`.

  Must NOT do: Do not change existing response fields (`alert`, `guidance`, `response`, `related_events`), do not require auth for these endpoints, do not add WebSocket alert events, and do not change stale computed alerts with `alert_id = null`.

  Parallelization: Can parallel: NO | Wave 2 | Blocks: [3, 5, 7] | Blocked by: [1]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `apps/backend/main.py:190` - existing replay route and 404 behavior
  - Pattern:  `apps/backend/main.py:197` - existing ack route that accepts `AlertResponsePayload`
  - Pattern:  `apps/backend/store.py:98` - store replay facade
  - Pattern:  `apps/backend/store.py:101` - store ack facade
  - Pattern:  `apps/backend/db/sqlite_repository.py:387` - current ack persistence and response return path
  - Pattern:  `apps/backend/db/sqlite_repository.py:444` - replay bundle assembly
  - Pattern:  `apps/backend/db/sqlite_repository.py:534` - existing incident response readback shape
  - API/Type: `apps/backend/incidents.py:21` - request body type for ack payload
  - Test:     `tests/test_backend.py:324` - ack with evidence test style
  - Test:     `tests/test_backend.py:347` - replay bundle test style
  - Test:     `tests/test_backend.py:370` - long note validation regression
  - External: `https://fastapi.tiangolo.com/tutorial/body/` - request body should remain Pydantic-backed

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_backend.py::test_alert_replay_includes_not_started_drill_review -v > .omo/evidence/task-2-replay-review-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_backend.py::test_alert_replay_includes_not_started_drill_review -v > .omo/evidence/task-2-replay-review-green.txt 2>&1` passes after implementation.
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_backend.py::test_ack_alert_returns_partial_drill_review -v > .omo/evidence/task-2-ack-partial-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_backend.py::test_ack_alert_returns_partial_drill_review -v > .omo/evidence/task-2-ack-partial-green.txt 2>&1` passes after implementation.
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_backend.py::test_ack_alert_rejects_unknown_checklist_item -v > .omo/evidence/task-2-ack-unknown-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_backend.py::test_ack_alert_rejects_unknown_checklist_item -v > .omo/evidence/task-2-ack-unknown-green.txt 2>&1` passes after implementation.
  - [ ] Existing tests still pass: `.venv/bin/python -m pytest tests/test_backend.py::test_ack_alert_api_accepts_response_evidence tests/test_backend.py::test_alert_replay_returns_incident_bundle tests/test_backend.py::test_ack_alert_rejects_too_long_response_note -v > .omo/evidence/task-2-existing-api-regression.txt 2>&1`.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: partial drill review through live HTTP
    Tool:     curl
    Steps:    tmux new-session -d -s drill-api 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-2-http-qa.db\")), host=\"127.0.0.1\", port=8012)"'; sleep 2; curl -i -X POST http://127.0.0.1:8012/internal/events -H 'Content-Type: application/json' -d '{"event_id":"task-2-gas","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"demo":true}}' > .omo/evidence/task-2-ingest.txt; curl -i -X POST http://127.0.0.1:8012/api/alerts/1/ack -H 'Content-Type: application/json' -d '{"checklist":["evacuate"],"note":"Operator started evacuation.","evidence":"Door opened."}' > .omo/evidence/task-2-ack-http.txt; curl -i http://127.0.0.1:8012/api/alerts/1/replay > .omo/evidence/task-2-replay-http.txt; tmux kill-session -t drill-api
    Expected: `.omo/evidence/task-2-replay-http.txt` contains HTTP 200, `"status":"partial"`, `"completion_ratio":0.33`, and `"inspect_sensor"` under missed checklist.
    Evidence: .omo/evidence/task-2-replay-http.txt

  Scenario: unknown checklist id is rejected
    Tool:     curl
    Steps:    tmux new-session -d -s drill-api-error 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-2-error-qa.db\")), host=\"127.0.0.1\", port=8013)"'; sleep 2; curl -i -X POST http://127.0.0.1:8013/internal/events -H 'Content-Type: application/json' -d '{"event_id":"task-2-gas-error","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"demo":true}}' > .omo/evidence/task-2-error-ingest.txt; curl -i -X POST http://127.0.0.1:8013/api/alerts/1/ack -H 'Content-Type: application/json' -d '{"checklist":["fake_step"],"note":"Bad drill data.","evidence":"N/A"}' > .omo/evidence/task-2-ack-unknown-http.txt; tmux kill-session -t drill-api-error
    Expected: `.omo/evidence/task-2-ack-unknown-http.txt` contains HTTP 422 and `Unknown checklist item: fake_step`.
    Evidence: .omo/evidence/task-2-ack-unknown-http.txt
  ```

  Commit: YES | Message: `feat(incidents): include drill review in alert APIs` | Files: [`apps/backend/main.py`, `apps/backend/store.py`, `apps/backend/db/sqlite_repository.py`, `apps/backend/incidents.py`, `tests/test_backend.py`] | Approval-gated: ask before running `git commit`

- [ ] 3. Add derived incident command report API

  What to do: Add `GET /api/alerts/{alert_id}/report` returning a JSON command report derived from the same replay bundle. Exact response shape:
  - `title`: `"Incident Command Report #<alert_id>"`
  - `alert`: existing alert object
  - `guidance_summary`: `guidance.summary`
  - `response_review`: same review object as Task 2
  - `operator_note`: response note or `""`
  - `operator_evidence`: response evidence or `""`
  - `missed_actions`: `response_review.missed_checklist`
  - `timeline`: first 5 `related_events`

  Must NOT do: Do not persist reports, do not generate PDF, do not add file download, do not include secrets/session/user data, and do not add a new frontend route.

  Parallelization: Can parallel: YES | Wave 3 | Blocks: [6, 7] | Blocked by: [1, 2]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `apps/backend/main.py:190` - route style and alert 404 translation
  - Pattern:  `apps/backend/db/sqlite_repository.py:444` - replay bundle is the report source
  - Pattern:  `apps/backend/db/sqlite_repository.py:872` - reading timeline event shape
  - Pattern:  `apps/backend/db/sqlite_repository.py:903` - alert timeline event shape
  - Pattern:  `README.md:11` - existing HTTP demo style to keep report demo compatible
  - Test:     `tests/test_backend.py:347` - replay test can be mirrored for report
  - External: `https://fastapi.tiangolo.com/tutorial/path-params/` - keep alert id as path parameter

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_backend.py::test_alert_report_returns_command_report_after_partial_response -v > .omo/evidence/task-3-report-partial-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_backend.py::test_alert_report_returns_command_report_after_partial_response -v > .omo/evidence/task-3-report-partial-green.txt 2>&1` passes after implementation.
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_backend.py::test_alert_report_before_response_is_not_started -v > .omo/evidence/task-3-report-not-started-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_backend.py::test_alert_report_before_response_is_not_started -v > .omo/evidence/task-3-report-not-started-green.txt 2>&1` passes after implementation.
  - [ ] Unknown alert report returns 404 with `Alert not found`.
  - [ ] Report `timeline` contains at most 5 events.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: command report after partial drill
    Tool:     curl
    Steps:    tmux new-session -d -s drill-report-api 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-3-http-qa.db\")), host=\"127.0.0.1\", port=8014)"'; sleep 2; curl -i -X POST http://127.0.0.1:8014/internal/events -H 'Content-Type: application/json' -d '{"event_id":"task-3-gas","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"demo":true}}' > .omo/evidence/task-3-ingest.txt; curl -i -X POST http://127.0.0.1:8014/api/alerts/1/ack -H 'Content-Type: application/json' -d '{"checklist":["evacuate"],"note":"Operator started evacuation.","evidence":"Door opened."}' > .omo/evidence/task-3-ack.txt; curl -i http://127.0.0.1:8014/api/alerts/1/report > .omo/evidence/task-3-report-http.txt; tmux kill-session -t drill-report-api
    Expected: `.omo/evidence/task-3-report-http.txt` contains HTTP 200, `Incident Command Report #1`, `Partial response`, operator note, and missed actions.
    Evidence: .omo/evidence/task-3-report-http.txt

  Scenario: missing report returns 404
    Tool:     curl
    Steps:    tmux new-session -d -s drill-report-error 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-3-error-qa.db\")), host=\"127.0.0.1\", port=8015)"'; sleep 2; curl -i http://127.0.0.1:8015/api/alerts/999/report > .omo/evidence/task-3-report-404-http.txt; tmux kill-session -t drill-report-error
    Expected: `.omo/evidence/task-3-report-404-http.txt` contains HTTP 404 and `Alert not found`.
    Evidence: .omo/evidence/task-3-report-404-http.txt
  ```

  Commit: YES | Message: `feat(incidents): expose incident command report` | Files: [`apps/backend/main.py`, `apps/backend/store.py`, `apps/backend/db/sqlite_repository.py`, `tests/test_backend.py`] | Approval-gated: ask before running `git commit`

- [ ] 4. Add frontend drill copy and source-contract guardrails

  What to do: Extend `frontend/src/language.ts` `IncidentCopy` with drill/report strings for both English and Korean. Add source-contract tests in `tests/test_frontend_auth_gate.py` proving the UI will use interactive checklist input, not auto-submitted checklist ids, and that English/Korean copy exists.

  Must NOT do: Do not add JSX-only visible text, do not add a JS test framework, do not weaken existing auth/statistics source assertions, and do not add frontend dependencies.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [5, 6] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/language.ts:6` - `IncidentCopy` type to extend
  - Pattern:  `frontend/src/language.ts:108` - English incident copy block
  - Pattern:  `frontend/src/language.ts:228` - Korean incident copy block
  - Test:     `tests/test_frontend_auth_gate.py:55` - existing incident workflow source assertion
  - Test:     `tests/test_frontend_auth_gate.py:147` - message-key source assertion style
  - External: `https://react.dev/reference/react-dom/components/textarea` - existing form fields are React textarea controls; keep form semantics simple

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_copy_and_interactive_checklist_contract -v > .omo/evidence/task-4-drill-copy-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_copy_and_interactive_checklist_contract -v > .omo/evidence/task-4-drill-copy-green.txt 2>&1` passes after implementation.
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_does_not_autocomplete_all_actions -v > .omo/evidence/task-4-no-autocomplete-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_does_not_autocomplete_all_actions -v > .omo/evidence/task-4-no-autocomplete-green.txt 2>&1` passes after implementation.
  - [ ] Existing frontend source tests still pass: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py -v > .omo/evidence/task-4-frontend-source-full.txt 2>&1`.
  - [ ] `npm --prefix frontend run build > .omo/evidence/task-4-frontend-build.txt 2>&1` exits 0.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: frontend source exposes drill copy and checklist controls
    Tool:     bash
    Steps:    .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_copy_and_interactive_checklist_contract -v
    Expected: PASS; source assertions find `response_review`, checkbox checklist controls, `Incident drill`, `Partial response`, `Incident command report`, and Korean equivalents.
    Evidence: .omo/evidence/task-4-drill-copy-green.txt

  Scenario: frontend source no longer auto-completes every guidance item
    Tool:     bash
    Steps:    .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_does_not_autocomplete_all_actions -v
    Expected: PASS; source no longer contains `guidance.checklist.map((item) => item.id)` as the submitted checklist payload and does contain `form.getAll('response-checklist')`.
    Evidence: .omo/evidence/task-4-no-autocomplete-green.txt
  ```

  Commit: YES | Message: `test(frontend): guard incident drill contracts` | Files: [`frontend/src/language.ts`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before running `git commit`

- [ ] 5. Implement interactive incident drill UI

  What to do: Update `frontend/src/IncidentResponsePanel.tsx` so guidance checklist items render as checkboxes named `response-checklist`. On submit, send only `form.getAll('response-checklist')` string ids. Extend local `AlertReplay` types with `response_review`, render status/ratio/next best action, and list missed actions. Preserve existing note/evidence fields and replay timeline. Add minimal scoped CSS in `frontend/src/App.css`.

  Must NOT do: Do not move the panel out of the right rail, do not convert the app to a new router/page, do not add state management libraries, and do not remove replay or ack endpoint calls.

  Parallelization: Can parallel: YES | Wave 3 | Blocks: [6, 7] | Blocked by: [1, 2, 4]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:39` - replay payload type to extend
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:88` - replay load flow
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:102` - current form submit flow
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:176` - current guidance rendering
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:186` - current form controls
  - Pattern:  `frontend/src/App.tsx:741` - panel integration point in the right rail
  - Pattern:  `frontend/src/App.css:1026` - incident panel CSS region
  - Test:     `tests/test_frontend_auth_gate.py:65` - endpoint-source assertion
  - External: `https://react.dev/reference/react/useState` - use local component state only if needed

  Acceptance criteria (agent-executable only):
  - [ ] RED captured by Task 4 source tests before implementation and GREEN retained here: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_copy_and_interactive_checklist_contract tests/test_frontend_auth_gate.py::test_incident_drill_does_not_autocomplete_all_actions -v > .omo/evidence/task-5-frontend-drill-contract-green.txt 2>&1`.
  - [ ] `npm --prefix frontend run build > .omo/evidence/task-5-frontend-build.txt 2>&1` exits 0.
  - [ ] UI shows `Partial response` and missed actions after selecting only one gas critical checklist item.
  - [ ] UI shows `Response complete` and no missed actions after selecting all gas critical checklist items.
  - [ ] Existing replay unavailable/save failed/saved messages still render from `copy` keys, not hardcoded strings.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: browser partial drill feedback
    Tool:     playwright(real Chrome)
    Steps:    npm --prefix frontend run build; tmux new-session -d -s drill-ui 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-5-browser-qa.db\"), frontend_dist=Path(\"frontend/dist\")), host=\"127.0.0.1\", port=8016)"'; sleep 2; curl -i -X POST http://127.0.0.1:8016/internal/events -H 'Content-Type: application/json' -d '{"event_id":"task-5-gas","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"demo":true}}' > .omo/evidence/task-5-seed-http.txt; launch Chrome with Playwright `chromium.launch({ channel: "chrome" })`; navigate to `http://127.0.0.1:8016`; click `text=Create account`; fill `input[name="email"]` with `drill@example.com`; fill `input[name="password"]` with `safe-password-123`; click `button:has-text("Create account")`; click `button:has-text("Replay incident")`; check only `input[name="response-checklist"][value="evacuate"]`; fill `textarea[name="response-note"]` with `Operator started evacuation.`; fill `textarea[name="response-evidence"]` with `Door opened.`; click `button:has-text("Complete drill")`; save screenshot `.omo/evidence/task-5-browser-partial-drill.png`; save action log `.omo/evidence/task-5-browser-partial-drill-log.txt`; tmux kill-session -t drill-ui
    Expected: Browser page contains `Partial response`, `Ventilate the room`, and `Check the gas sensor and wiring`; screenshot exists and is non-empty.
    Evidence: .omo/evidence/task-5-browser-partial-drill.png

  Scenario: browser complete drill feedback
    Tool:     playwright(real Chrome)
    Steps:    Reuse the same action script pattern against `http://127.0.0.1:8017` with isolated DB `.omo/evidence/task-5-browser-complete-qa.db`; seed event id `task-5-gas-complete`; create account `complete@example.com`; replay alert; check `evacuate`, `ventilate`, and `inspect_sensor`; submit note `All response steps completed.` and evidence `Room cleared, ventilation opened, sensor checked.`; save screenshot `.omo/evidence/task-5-browser-complete-drill.png`; save action log `.omo/evidence/task-5-browser-complete-drill-log.txt`; kill tmux session `drill-ui-complete`.
    Expected: Browser page contains `Response complete`, does not list missed actions, and replay timeline is still visible.
    Evidence: .omo/evidence/task-5-browser-complete-drill.png
  ```

  Commit: YES | Message: `feat(frontend): make incident response an operator drill` | Files: [`frontend/src/IncidentResponsePanel.tsx`, `frontend/src/App.css`, `frontend/src/language.ts`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before running `git commit`

- [ ] 6. Render incident command report in the right rail

  What to do: Extend `IncidentResponsePanel` to fetch `/api/alerts/{alert_id}/report` after replay and after successful drill submission. Render a compact report section containing title, status/score label, operator note/evidence, missed actions, and first timeline entries. Use the existing panel visual language and the same English/Korean copy added in Task 4.

  Must NOT do: Do not add a separate report page, do not implement PDF/export/download, do not expose auth user details, and do not remove the existing replay timeline block.

  Parallelization: Can parallel: NO | Wave 4 | Blocks: [7] | Blocked by: [3, 5]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:39` - replay payload type and related events type
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:201` - existing replay timeline section to keep visible
  - Pattern:  `frontend/src/App.css:1087` - incident guidance/form/replay shared styling
  - Pattern:  `frontend/src/language.ts:108` - English incident copy block
  - Pattern:  `frontend/src/language.ts:228` - Korean incident copy block
  - Test:     `tests/test_frontend_auth_gate.py:55` - source workflow hook tests to extend with report endpoint/copy
  - External: `https://playwright.dev/docs/api/class-page` - use real page actions and screenshots for browser QA

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_panel_fetches_and_renders_command_report -v > .omo/evidence/task-6-report-ui-red.txt 2>&1` fails before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_panel_fetches_and_renders_command_report -v > .omo/evidence/task-6-report-ui-green.txt 2>&1` passes after implementation.
  - [ ] `npm --prefix frontend run build > .omo/evidence/task-6-frontend-build.txt 2>&1` exits 0.
  - [ ] The report fetch is relative (`/api/...`) and works under backend static serving and Vite proxy.
  - [ ] If report fetch returns 404/500, the replay panel remains usable and shows existing replay guidance rather than crashing.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: browser report after partial drill
    Tool:     playwright(real Chrome)
    Steps:    npm --prefix frontend run build; tmux new-session -d -s drill-report-ui 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-6-browser-qa.db\"), frontend_dist=Path(\"frontend/dist\")), host=\"127.0.0.1\", port=8018)"'; sleep 2; seed gas event `task-6-gas` with curl to `http://127.0.0.1:8018/internal/events`; launch Chrome with Playwright `chromium.launch({ channel: "chrome" })`; sign up as `report@example.com`; replay incident; select only `evacuate`; submit note/evidence; wait for `Incident command report`; save screenshot `.omo/evidence/task-6-browser-report.png`; save action log `.omo/evidence/task-6-browser-report-log.txt`; tmux kill-session -t drill-report-ui
    Expected: Browser page contains `Incident command report`, `Partial response`, `Operator started evacuation.`, and at least one missed action.
    Evidence: .omo/evidence/task-6-browser-report.png

  Scenario: report endpoint failure leaves replay usable
    Tool:     playwright(real Chrome)
    Steps:    In the browser QA script, intercept `**/api/alerts/1/report` and fulfill status 500; navigate to `http://127.0.0.1:8019` backed by isolated DB `.omo/evidence/task-6-report-error-qa.db`; seed gas event; sign up; click `Replay incident`; save screenshot `.omo/evidence/task-6-browser-report-error.png`; save action log `.omo/evidence/task-6-browser-report-error-log.txt`; kill tmux session `drill-report-ui-error`.
    Expected: Browser page still contains guidance text `Critical gas level detected` and replay timeline; no blank panel or uncaught error text is visible.
    Evidence: .omo/evidence/task-6-browser-report-error.png
  ```

  Commit: YES | Message: `feat(frontend): show incident command report` | Files: [`frontend/src/IncidentResponsePanel.tsx`, `frontend/src/App.css`, `frontend/src/language.ts`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before running `git commit`

- [ ] 7. Update demo docs for the differentiator

  What to do: Update `README.md` and `README.ko.md` so the differentiator is now "Incident Drill Mode + Command Report" rather than only "Incident Replay + Guided Response". Add exact local HTTP demo commands for ingest, replay, partial ack, replay with review, and report. Add one short note that the feature is deterministic/local and does not require LLM, cloud notifications, or actuator hardware.

  Must NOT do: Do not rewrite the development log tables, do not remove Korean runbook structure, do not claim real four-board bring-up or live OAuth provider verification, and do not edit `SETUP.md` unless the executor discovers a command mismatch that prevents the README demo from running.

  Parallelization: Can parallel: NO | Wave 5 | Blocks: [] | Blocked by: [2, 3, 5, 6]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `README.md:5` - current differentiator section
  - Pattern:  `README.md:11` - existing local HTTP demo command format
  - Pattern:  `README.ko.md:34` - Korean differentiator section
  - Pattern:  `README.ko.md:40` - Korean local demo command block
  - Pattern:  `docs/superpowers/UPDATE_HISTORY.md:16` - current incident replay status and related files
  - Test:     `tests/test_frontend_auth_gate.py:55` - source tests verify terminology in UI; docs should use the same terms
  - External: `https://www.sqlite.org/lang_upsert.html` - no new migration expected; mention deterministic local data, not new persistence machinery

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `bash -lc 'grep -n "Incident Drill Mode" README.md && grep -n "/api/alerts/1/report" README.md && grep -n "Incident Drill Mode" README.ko.md && grep -n "/api/alerts/1/report" README.ko.md' > .omo/evidence/task-7-docs-red.txt 2>&1` fails before docs update.
  - [ ] GREEN captured: `bash -lc 'grep -n "Incident Drill Mode" README.md && grep -n "/api/alerts/1/report" README.md && grep -n "Incident Drill Mode" README.ko.md && grep -n "/api/alerts/1/report" README.ko.md' > .omo/evidence/task-7-docs-green.txt 2>&1` passes after docs update.
  - [ ] Live README command sequence captured: `.omo/evidence/task-7-docs-http-demo.txt` contains HTTP 201 for ingest, HTTP 200 for replay, HTTP 200 for partial ack, and HTTP 200 for report.
  - [ ] Guardrail grep captured: `bash -lc '! grep -R "OpenAI\\|GPT\\|SMS\\|buzzer\\|actuator" README.md README.ko.md' > .omo/evidence/task-7-docs-guardrails.txt 2>&1` exits 0, unless the term appears only in a Must-NOT explanatory sentence; if so, update the grep to assert that it appears only in that explanatory sentence.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: README demo commands match live API
    Tool:     curl
    Steps:    tmux new-session -d -s drill-docs-api 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-7-http-qa.db\")), host=\"127.0.0.1\", port=8020)"'; sleep 2; curl -i -X POST http://127.0.0.1:8020/internal/events -H 'Content-Type: application/json' -d '{"event_id":"incident-drill-demo-gas","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"demo":true}}' > .omo/evidence/task-7-docs-ingest.txt; curl -i http://127.0.0.1:8020/api/alerts/1/replay > .omo/evidence/task-7-docs-replay-before.txt; curl -i -X POST http://127.0.0.1:8020/api/alerts/1/ack -H 'Content-Type: application/json' -d '{"checklist":["evacuate"],"note":"Demo operator started evacuation.","evidence":"Door opened; ventilation pending."}' > .omo/evidence/task-7-docs-ack.txt; curl -i http://127.0.0.1:8020/api/alerts/1/replay > .omo/evidence/task-7-docs-replay-after.txt; curl -i http://127.0.0.1:8020/api/alerts/1/report > .omo/evidence/task-7-docs-http-demo.txt; tmux kill-session -t drill-docs-api
    Expected: Final report artifact contains HTTP 200, `Incident Command Report #1`, `Partial response`, and the submitted evidence.
    Evidence: .omo/evidence/task-7-docs-http-demo.txt

  Scenario: docs do not oversell excluded scope
    Tool:     bash
    Steps:    bash -lc '! grep -R "real four-board verified\\|live OAuth verified\\|cloud notification\\|AI assistant" README.md README.ko.md'
    Expected: Exit 0; docs do not claim hardware/OAuth/cloud/AI work that this plan does not ship.
    Evidence: .omo/evidence/task-7-docs-scope-guard.txt
  ```

  Commit: YES | Message: `docs(readme): document incident drill differentiator` | Files: [`README.md`, `README.ko.md`] | Approval-gated: ask before running `git commit`

## Final verification wave (MANDATORY - after all implementation tasks)
> Runs in PARALLEL. ALL must APPROVE. Surface results to the caller and wait for an explicit "okay" before declaring complete.
- [ ] F1. Plan compliance audit - every task done, every acceptance criterion met
- [ ] F2. Code quality review - diagnostics clean, idioms match, no dead code
- [ ] F3. Real manual QA - every QA scenario executed with evidence captured
- [ ] F4. Scope fidelity - nothing extra shipped beyond Must-Have, nothing Must-NOT-Have introduced

## Commit strategy
- One logical change per commit. Conventional Commits (`<type>(<scope>): <subject>` body + footer).
- Atomic: every commit builds and passes tests on its own.
- No "WIP" / "fix typo squash later" commits on the final branch - clean up before merge.
- Commits are approval-gated by the project instructions: ask the user before running `git commit`.
- Reference the plan file path in the final commit footer: `Plan: .omo/plans/pico-saferoom-incident-drill-mode.md`.

## Success criteria
- All Must-Have shipped; all QA scenarios pass with captured evidence; F1-F4 approved; commit history clean.
