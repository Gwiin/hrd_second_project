# ULW Notepad: Incident Command Report

## Objective
Build a differentiating Pico SafeRoom feature: an Incident Command Report that turns existing alert replay + acknowledgement evidence into a shareable response packet.

## Skills Used
- `omo:ulw-plan`: requested by user; planning scope and criteria.
- `omo:ulw-loop`: requested by user; evidence-bound execution and manual QA.
- `karpathy-guidelines`: coding judgment; smallest scoped change.
- `omo:programming`: required for Python and TypeScript edits.
- `tdd`: mandatory RED -> GREEN implementation.
- `omo:frontend-ui-ux`: frontend-visible incident report affordance.
- `omo:review-work` / `codex-ultrawork-reviewer`: final verification because this is multi-file work.

## Scope
- Backend: add `/api/alerts/{alert_id}/report` returning a deterministic command-report packet.
- Frontend: expose report status/next action inside the existing Incident Response panel.
- Tests: backend API tests and source-level frontend contract tests.
- Out of scope: real OAuth provider changes, hardware/Pico firmware changes, root `AGENTS.md`, `agent-map.md`.

## Success Criteria
- C001 HTTP happy path: POST critical gas event, acknowledge with evidence, curl report endpoint returns report_id, next_action, checklist counts, note.
- C002 HTTP edge: unknown report alert id returns 404 with `Alert not found`.
- C003 Browser regression: built dashboard still supports signup, replay, and displays Incident response plus Incident report.

## TDD Evidence
- RED backend report tests: `/api/alerts/1/report` returned 404 instead of 200; `/api/alerts/999/report` returned default `Not Found`; malformed checklist regression returned `completed == 4` against total `3`.
- RED frontend contract test: `test_incident_response_panel_surfaces_command_report` failed because `Incident report` was absent.
- GREEN backend report tests: `tests/test_backend.py::test_alert_report_returns_command_packet_after_ack`, `::test_alert_report_unknown_alert_returns_404`, and `::test_alert_report_ignores_unknown_checklist_items` passed.
- GREEN frontend/build checks: `tests/test_frontend_auth_gate.py::test_incident_response_panel_surfaces_command_report` passed; `npm --prefix frontend run build` passed.
- Full verification: `.venv/bin/python -m pytest` passed with `106 passed, 1 warning`.
- Manual HTTP QA: `.omo/ulw-loop/evidence/incident-report-http-happy.txt` and `.omo/ulw-loop/evidence/incident-report-http-404.txt`.
- Manual browser QA: `.omo/ulw-loop/evidence/incident-report-browser-actions.txt` and `.omo/ulw-loop/evidence/incident-report-browser.png`.
- Cleanup receipt: QA server stopped, port 8765 had no listener, `/private/tmp/ulw-incident-report.db*` and log removed, browser closed.

## Findings
- Worktree has pre-existing user changes in `AGENTS.md` and untracked `agent-map.md`; do not touch them.
- Existing incident replay/ack flow is the best foundation. This avoids another passive dashboard/statistics feature.
- Parallel `steer` calls race on the same goals file; criteria repair was done sequentially.
- Subagents became available after tool discovery; Planner is running in background.
