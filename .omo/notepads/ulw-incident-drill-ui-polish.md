# ULW Notepad: Incident Drill UI Polish

## Objective
Make the newly added Incident Drill Mode panel visually cohesive with the Pico SafeRoom dashboard while preserving behavior.

## Skills Used
- `omo:ulw-loop`: user requested durable evidence-bound execution and manual QA.
- `omo:frontend-ui-ux`: the defect is visual design quality in the browser surface.
- `tdd`: required RED -> GREEN for production UI changes.
- `karpathy-guidelines`: keep the change surgical and avoid speculative redesign.
- `omo:programming`: required for TypeScript/TSX edits.

## Scope
- Files expected in scope: `frontend/src/IncidentResponsePanel.tsx`, `frontend/src/App.css`, `tests/test_frontend_auth_gate.py`.
- Keep backend API behavior unchanged.
- Design direction: refined operations-console polish; denser, calmer, card-like inner sections that match existing glass dashboard, with better checklist affordances, review meter, and text fit.

## Success Criteria
- C001 happy browser path: replay a critical gas alert, select one checklist item, submit, and verify the panel shows a polished drill review with progress meter, styled checklist, missed actions, and command report.
- C002 edge visual path: load the dashboard with no replayed incident/no active alert and verify the panel remains readable without empty awkward boxes.
- C003 responsive regression: run the same browser surface at a narrow viewport and verify text does not overflow and core controls remain visible.

## Evidence Plan
- RED/GREEN source tests in `tests/test_frontend_auth_gate.py`.
- Browser QA artifacts under `.omo/evidence/incident-drill-ui-*`.
- Full validation: `npm --prefix frontend run build`, `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py`.

## Findings
- Previous drill UI worked functionally but looked bolted on: flat green/blue bands, raw list/checklist styling, weak hierarchy, and no visual progress affordance.
