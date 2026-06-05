# ULW Notepad: Incident Drill Mode

## Objective
Build a differentiating Pico SafeRoom feature: an active Incident Drill Mode that lets operators select performed checklist actions, receives deterministic backend feedback, and generates a compact command report.

## Skills Used
- `omo:ulw-plan`: requested by user; planning scope and criteria.
- `omo:ulw-loop`: requested by user; evidence-bound execution and manual QA.
- `karpathy-guidelines`: coding judgment; smallest scoped change.
- `omo:programming`: required for Python and TypeScript edits.
- `tdd`: mandatory RED -> GREEN implementation.
- `omo:frontend-ui-ux`: frontend-visible incident report affordance.
- `omo:review-work` / `codex-ultrawork-reviewer`: final verification because this is multi-file work.

## Scope
- Backend: add deterministic drill review, include `response_review` in replay/ack, reject unknown checklist ids with HTTP 422, and expose `/api/alerts/{alert_id}/report`.
- Frontend: replace auto-completed checklist submission with interactive checkbox evidence, show partial/complete feedback, next best action, and command report summary inside the existing Incident Response panel.
- Tests: backend helper/API tests, source-level frontend contract tests, full pytest, and frontend build.
- Out of scope: real OAuth provider changes, hardware/Pico firmware changes, root `AGENTS.md`, `agent-map.md`.

## Success Criteria
- C001 HTTP happy path: POST critical gas event, acknowledge with partial checklist evidence, replay/report return `response_review.status == "partial"`, `completion_ratio == 0.33`, missed actions, operator note/evidence, and command report title.
- C002 HTTP edge: unknown report alert id returns 404 with `Alert not found`.
- C003 Browser regression: built dashboard supports signup, replay, one checked action, two unchecked actions, partial feedback, next-best action, and Incident command report.

## TDD Evidence
- RED backend helper tests: `.omo/evidence/task-1-review-partial-red.txt`, `.omo/evidence/task-1-review-not-started-red.txt`.
- GREEN backend helper tests: `.omo/evidence/task-1-review-partial-green.txt`, `.omo/evidence/task-1-review-not-started-green.txt`.
- RED backend API tests: `.omo/evidence/task-2-replay-review-red.txt`, `.omo/evidence/task-2-ack-partial-red.txt`, `.omo/evidence/task-2-ack-unknown-red.txt`, `.omo/evidence/task-3-report-partial-red.txt`, `.omo/evidence/task-3-report-not-started-red.txt`.
- GREEN backend API tests: `.omo/evidence/task-2-replay-review-green.txt`, `.omo/evidence/task-2-ack-partial-green.txt`, `.omo/evidence/task-2-ack-unknown-green.txt`, `.omo/evidence/task-3-report-partial-green.txt`, `.omo/evidence/task-3-report-not-started-green.txt`.
- GREEN frontend contract/build checks: `.omo/evidence/task-4-drill-copy-green.txt`, `.omo/evidence/task-4-no-autocomplete-green.txt`, `.omo/evidence/task-4-frontend-source-full.txt`, `.omo/evidence/task-4-frontend-build.txt`.
- Full verification: `.omo/evidence/incident-drill-full-pytest.txt`, `.omo/evidence/incident-drill-frontend-build.txt`, `.omo/evidence/incident-drill-diff-check.txt`.
- Manual HTTP QA: `.omo/evidence/incident-drill-http-ack-partial.txt`, `.omo/evidence/incident-drill-http-ack-unknown.txt`, `.omo/evidence/incident-drill-http-replay.txt`, `.omo/evidence/incident-drill-http-report.txt`.
- Manual browser QA: `.omo/evidence/incident-drill-browser-actions.txt` and `.omo/evidence/incident-drill-browser.png`.
- Cleanup receipt: QA servers stopped, ports 8766/8767 had no listeners, browser closed.

## Findings
- Existing incident replay/ack flow is the best foundation. This avoids another passive dashboard/statistics feature.
- Parallel `steer` calls race on the same goals file; criteria repair was done sequentially.
- Subagents became available after tool discovery; Planner is running in background.
