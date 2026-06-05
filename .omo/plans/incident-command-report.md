# Incident Command Report

## TL;DR
> **Summary**: Add a deterministic Incident Command Report that packages an alert, guidance, operator response evidence, checklist completion, related blackbox timeline, and next action.
> **Deliverables**: `/api/alerts/{alert_id}/report`; Incident Response panel report summary; backend/frontend tests; HTTP and browser QA evidence.
> **Effort**: Short
> **Parallel**: LIMITED - tests and implementation touch coupled backend/frontend files.
> **Critical Path**: RED backend API test -> backend report implementation -> RED frontend contract test -> frontend report UI -> HTTP/browser QA -> reviewer.

## Context
### Original Request
Build more things that can make this project unique and special compared to similar projects, using `omo:ulw-plan` and `omo:ulw-loop`.

### Interview Summary
No extra user interview was needed: the repo already shows Pico SafeRoom as a safety dashboard with incident replay/guided response, and prior memory says "fresh" should avoid passive dashboard-only ideas.

### Metis Review
Pending background planner/metis-style review. Default applied: implement one high-impact differentiator rather than several speculative features.

## Work Objectives
### Core Objective
Make Pico SafeRoom feel like a real emergency-response system, not only a sensor dashboard.

### Deliverables
- Backend command report endpoint.
- Frontend report summary/action inside the existing incident panel.
- Evidence-first tests and live QA artifacts.

### Definition of Done
- `.venv/bin/python -m pytest tests/test_backend.py tests/test_frontend_auth_gate.py` passes.
- `npm --prefix frontend run build` passes.
- Live `curl -i /api/alerts/1/report` artifact captured.
- Live browser screenshot/action log captured.
- ULW criteria are recorded with cleanup receipts.

### Must Have
- Preserve existing replay and ack behavior.
- Unknown report alert id must return 404.
- Report payload must be deterministic and useful for demo/explanation.

### Must NOT Have
- No LLM/chat integration.
- No hardware/firmware scope.
- No changes to user-owned `AGENTS.md` or `agent-map.md`.
- No speculative provider/auth changes.

## Verification Strategy
> ZERO HUMAN INTERVENTION - all verification is agent-executed.
- Test decision: TDD with pytest/source-contract tests.
- QA policy: each ULW criterion gets HTTP or browser evidence.
- Evidence: `.omo/ulw-loop/evidence/*`.

## Execution Strategy
### Parallel Execution Waves
Wave 1: Backend RED/GREEN.
Wave 2: Frontend RED/GREEN.
Wave 3: Builds, HTTP QA, browser QA.
Wave 4: Review and checkpoint.

### Dependency Matrix
| Task | Depends on | Blocks | Can parallelize with |
| --- | --- | --- | --- |
| 1 Backend report | none | 2, 3 | none |
| 2 Frontend report UI | 1 payload shape | 3 | none |
| 3 Manual QA | 1, 2 | 4 | none |
| 4 Review/checkpoint | 3 | final | none |

## TODOs
- [ ] 1. Backend Incident Command Report endpoint

  **What to do**: Add failing tests in `tests/test_backend.py` for report happy path and unknown alert. Add minimal repository/store/route code.
  **Must NOT do**: Do not change existing replay/ack response shapes.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 2, 3 | Blocked By: none

  **References**:
  - Pattern: `apps/backend/main.py` alert replay route.
  - Pattern: `apps/backend/store.py` thin store facade.
  - Pattern: `apps/backend/db/sqlite_repository.py` `alert_replay` and `ack_alert`.
  - Test: `tests/test_backend.py` incident replay/ack tests.

  **Acceptance Criteria**:
  - [ ] `tests/test_backend.py::test_alert_report_returns_command_packet_after_ack` passes.
  - [ ] `tests/test_backend.py::test_alert_report_unknown_alert_returns_404` passes.

  **QA Scenarios**:
  ```
  Scenario: HTTP happy path
    Tool: curl
    Steps: POST event, POST ack, GET /api/alerts/1/report
    Expected: 200 plus report_id alert-1 and next_action monitor_until_clear
    Evidence: .omo/ulw-loop/evidence/incident-report-http-happy.txt

  Scenario: HTTP 404 edge
    Tool: curl
    Steps: GET /api/alerts/999/report
    Expected: 404 plus Alert not found
    Evidence: .omo/ulw-loop/evidence/incident-report-http-404.txt
  ```

  **Commit**: YES | Message: `feat(incident): add command report endpoint` | Files: `apps/backend/main.py`, `apps/backend/store.py`, `apps/backend/db/sqlite_repository.py`, `tests/test_backend.py`

- [ ] 2. Frontend Incident Report affordance

  **What to do**: Add failing source-contract test in `tests/test_frontend_auth_gate.py`; display report summary after replay fetch.
  **Must NOT do**: Do not add generic dashboard text or a separate navigation page.

  **Parallelization**: Can Parallel: NO | Wave 2 | Blocks: 3 | Blocked By: 1

  **References**:
  - Pattern: `frontend/src/IncidentResponsePanel.tsx` current replay and ack flow.
  - Pattern: `frontend/src/language.ts` bilingual incident copy.
  - Pattern: `frontend/src/App.css` incident panel styling.

  **Acceptance Criteria**:
  - [ ] `tests/test_frontend_auth_gate.py::test_incident_response_panel_surfaces_command_report` passes.
  - [ ] `npm --prefix frontend run build` passes.

  **QA Scenarios**:
  ```
  Scenario: Browser incident workflow regression
    Tool: browser
    Steps: open dashboard, sign up, click Replay incident
    Expected: Incident response and Incident report visible
    Evidence: .omo/ulw-loop/evidence/incident-report-browser.png
  ```

  **Commit**: YES | Message: `feat(incident): surface command report in dashboard` | Files: `frontend/src/IncidentResponsePanel.tsx`, `frontend/src/language.ts`, `frontend/src/App.css`, `tests/test_frontend_auth_gate.py`

## Final Verification Wave
- [ ] F1. Run backend/frontend tests and build.
- [ ] F2. Run live HTTP QA with cleanup receipt.
- [ ] F3. Run browser QA with screenshot/action log and cleanup receipt.
- [ ] F4. Reviewer approval.

## Commit Strategy
Do not commit automatically unless separately requested. Present changed files and suggested commit messages.

## Success Criteria
- All ULW criteria pass and are recorded through CLI.
- No user-owned dirty files are touched.
- Reviewer gives unconditional approval.
