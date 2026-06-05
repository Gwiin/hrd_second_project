# Pico SafeRoom Incident Drill UI Polish

## TL;DR
> Summary:      Polish the newly added Incident Drill Mode panel so it reads like a refined Pico SafeRoom operations console while preserving the existing replay, acknowledgement, report, auth, and backend behavior.
> Deliverables:
> - Focused visual polish for the right-rail Incident Drill Mode panel
> - Source-contract TDD coverage for visual structure, empty/not-replayed state, and mobile text-fit regressions
> - Fresh browser QA screenshots/action logs for happy, empty, and narrow-layout scenarios
> - Build/test/backend regression evidence and cleanup receipt
> Effort:       Short
> Risk:         Medium - central files are large and the current worktree already has uncommitted UI-polish RED hooks; executor must preserve dirty state and avoid scope creep

## Scope
### Must have
- Preserve current backend API behavior from `apps/backend/main.py:190` through `apps/backend/main.py:217`; do not change replay, report, or ack routes.
- Keep the UI inside the existing dashboard right rail where `frontend/src/App.tsx:882` renders `IncidentResponsePanel`.
- Use the existing incident panel component structure from `frontend/src/IncidentResponsePanel.tsx:168` through `frontend/src/IncidentResponsePanel.tsx:294`.
- Polish the existing incident sub-surfaces: header/replay button, alert rows, guidance, drill review, checklist/form, report card, and replay timeline from `frontend/src/IncidentResponsePanel.tsx:170`, `frontend/src/IncidentResponsePanel.tsx:186`, `frontend/src/IncidentResponsePanel.tsx:212`, `frontend/src/IncidentResponsePanel.tsx:222`, `frontend/src/IncidentResponsePanel.tsx:240`, `frontend/src/IncidentResponsePanel.tsx:269`, and `frontend/src/IncidentResponsePanel.tsx:280`.
- Work primarily in `frontend/src/App.css`, especially the current incident styles at `frontend/src/App.css:1219`, `frontend/src/App.css:1255`, `frontend/src/App.css:1280`, `frontend/src/App.css:1303`, `frontend/src/App.css:1368`, `frontend/src/App.css:1401`, and `frontend/src/App.css:1412`.
- Preserve and extend the source-level frontend contract pattern in `tests/test_frontend_auth_gate.py:1` through `tests/test_frontend_auth_gate.py:18`.
- Cover three required UI criteria: happy visual polish, empty/no-alert or not-replayed state regression, and mobile/narrow layout text-fit regression.
- If visible copy changes are required for fit/readability, update both English and Korean copy in `frontend/src/language.ts:125` and `frontend/src/language.ts:268`, keeping the `IncidentCopy` type at `frontend/src/language.ts:6` synchronized.
- Treat current uncommitted changes as user/worker state. Based on exploration, `tests/test_frontend_auth_gate.py:107` already contains a visual-polish contract and `frontend/src/IncidentResponsePanel.tsx` already has some class hook changes, while matching CSS is still missing. Re-capture fresh RED/GREEN evidence; do not assume old evidence is current.

### Must NOT have (guardrails, anti-slop, scope boundaries)
- Do not add backend routes, database schema, hardware behavior, auth provider changes, notifications, LLM/chat, statistics-page work, or a new dashboard page.
- Do not change fetch URLs or API payload contracts in `frontend/src/IncidentResponsePanel.tsx:116` through `frontend/src/IncidentResponsePanel.tsx:165`.
- Do not broaden OAuth scope; Google/Kakao auth behavior remains untouched.
- Do not add a JS test runner dependency; frontend contract tests remain in `tests/test_frontend_auth_gate.py` because `frontend/AGENTS.md:20` through `frontend/AGENTS.md:21` says build uses `npm --prefix frontend run build` and there is no JS test runner.
- Do not edit `.omo/ulw-loop/` or `.omo/notepads/ulw-incident-drill-ui-polish.md`; both were already dirty/untracked during planning.
- Do not grow `frontend/src/IncidentResponsePanel.tsx` with broad markup. It is already over the 250 pure-LOC programming guideline. Prefer CSS-only polish and in-place class replacements; if extra TSX is unavoidable, keep it limited to Task 1 and do not introduce new state, effects, or fetches.
- Do not commit without explicit user approval.

## Verification strategy
> Zero human intervention - all verification is agent-executed.
- Test decision: TDD + existing `pytest` source-contract tests and TypeScript/Vite build
- QA policy: every task has agent-executed scenarios
- Evidence: `.omo/evidence/task-<N>-incident-drill-ui-polish.<ext>`

## Execution strategy
### Parallel execution waves
> Target 5-8 tasks per wave. <3 per wave (except final) = under-splitting.
> Extract shared dependencies as Wave-1 tasks to maximize parallelism.

Wave 1 (no dependencies):
- Task 1: lock visual structure hooks and top-level polish contract
- Task 2: polish alert/guidance/review/form/report CSS as one stylesheet-safe slice
- Task 3: add empty/no-alert and not-replayed state regression coverage
- Task 4: add mobile/narrow text-fit regression coverage
- Task 5: prepare real-browser QA harness and cleanup receipts

Wave 2 (after Wave 1):
- Task 6: run integrated validation and backend behavior regression, depends [1, 2, 3, 4, 5]

Critical path: Task 1 -> Task 2 -> Task 6

### Dependency matrix
| Task | Depends on | Blocks | Can parallelize with |
|------|------------|--------|----------------------|
| 1    | none       | 2, 6   | 3, 4, 5              |
| 2    | 1          | 6      | none                 |
| 3    | none       | 2, 6   | 1, 4, 5              |
| 4    | none       | 2, 6   | 1, 3, 5              |
| 5    | none       | 6      | 1, 3, 4              |
| 6    | 1, 2, 3, 4, 5 | none | none                 |

## Todos
> Implementation + Test = ONE task. Never separate.
> Every task MUST have: References + Acceptance Criteria + QA Scenarios + Commit.

- [ ] 1. Lock visual structure hooks and top-level polish contract

  What to do: Use or strengthen the existing `test_incident_drill_panel_has_polished_visual_structure` contract. It must fail before final CSS is present and pass only when the incident panel exposes class hooks for a designed review card, score ring, checklist card, report card, and section label. If class hooks are already present in dirty TSX, preserve them; if any are missing, add only in-place class replacements in `IncidentResponsePanel.tsx` with no new state/effects/fetches.
  Must NOT do: Do not add a new component, new route, new fetch, new copy key, or new data field.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [2, 6] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:168` - panel root and scoped incident markup
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:212` - guidance block where a section label can be added without changing behavior
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:222` - review block to style as the drill score area
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:240` - form/checklist block to style without changing submission
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:269` - report block to style as a compact card
  - Pattern:  `frontend/src/App.css:80` - existing glass panel visual language
  - Test:     `tests/test_frontend_auth_gate.py:107` - current visual-polish source contract to use or strengthen
  - External: `https://playwright.dev/docs/locators` - browser QA should use user-facing locators such as roles and labels

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_panel_has_polished_visual_structure -v > .omo/evidence/task-1-incident-drill-ui-polish-red.txt 2>&1` fails before the final polish implementation, with failure caused by missing visual hook/CSS selector rather than import or syntax errors.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_panel_has_polished_visual_structure -v > .omo/evidence/task-1-incident-drill-ui-polish-green.txt 2>&1` passes after implementation.
  - [ ] The passing test asserts all of these exact tokens are present: `incident-review-card`, `incident-score-ring`, `incident-checklist-card`, `incident-report-card`, `incident-section-label`, `.incident-review-card`, `.incident-score-ring`, `.incident-checklist-card`, `.incident-report-card`, and `overflow-wrap: anywhere`.
  - [ ] `git diff -- frontend/src/IncidentResponsePanel.tsx` contains no new state variable, no new `useEffect`, and no new `fetch(` call.

  QA scenarios (MANDATORY - task incomplete without these):
  > Name the exact tool AND its exact invocation - not "verify it works". Browser use: use Chrome to drive the page; if Chrome is not available, download and use agent-browser (https://github.com/vercel-labs/agent-browser). Computer use: OS-level GUI automation for a non-browser desktop app.
  ```
  Scenario: visual structure source contract goes green
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_panel_has_polished_visual_structure -v
    Expected: PASS; pytest output contains `test_incident_drill_panel_has_polished_visual_structure PASSED`.
    Evidence: .omo/evidence/task-1-incident-drill-ui-polish-green.txt

  Scenario: no behavior fetch regression in incident component
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && git diff -- frontend/src/IncidentResponsePanel.tsx | tee .omo/evidence/task-1-incident-drill-ui-polish-diff.txt
    Expected: diff contains className/hierarchy polish only; no added `fetch(`, `useEffect`, `useState`, `/api/alerts`, `/api/auth`, or route strings.
    Evidence: .omo/evidence/task-1-incident-drill-ui-polish-diff.txt
  ```

  Commit: YES | Message: `fix(frontend): add incident drill polish hooks` | Files: [`frontend/src/IncidentResponsePanel.tsx`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before `git commit`

- [ ] 2. Polish incident drill visual CSS in one stylesheet-safe slice

  What to do: Update the incident CSS as one coherent slice so the panel looks designed, not bolted on. Keep the existing glass dashboard palette from `:root` and panel styles. Add refined row/card surfaces, a score ring, checklist affordances, compact report card, readable timeline chips, focus/hover states, and text wrapping. Because all visual implementation converges on `frontend/src/App.css`, do this as a single CSS task to avoid concurrent overwrite conflicts.
  Must NOT do: Do not introduce a one-note purple/blue gradient, decorative blobs, nested cards inside page sections, clipped text, huge hero styling, or broad dashboard redesign.

  Parallelization: Can parallel: NO | Wave 1 | Blocks: [6] | Blocked by: [1, 3, 4]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/App.css:1` - design tokens and current palette
  - Pattern:  `frontend/src/App.css:80` - shared glass panel styling
  - Pattern:  `frontend/src/App.css:1219` - incident header styling to refine
  - Pattern:  `frontend/src/App.css:1255` - alert row styling to make less flat and more scannable
  - Pattern:  `frontend/src/App.css:1280` - shared incident block spacing to replace with richer surfaces
  - Pattern:  `frontend/src/App.css:1303` - current simple review background to replace with card + score hierarchy
  - Pattern:  `frontend/src/App.css:1368` - checklist styling to make checkboxes feel intentional
  - Pattern:  `frontend/src/App.css:1401` - textarea styling to keep forms readable
  - Pattern:  `frontend/src/App.css:1412` - replay timeline rows and text wrapping
  - Test:     `tests/test_frontend_auth_gate.py:107` - source contract for required CSS selectors
  - External: `https://vite.dev/guide/cli/` - Vite CLI supports host/port flags used by browser QA

  Acceptance criteria (agent-executable only):
  - [ ] GREEN recaptured after CSS: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_panel_has_polished_visual_structure -v > .omo/evidence/task-2-incident-drill-ui-polish-visual-green.txt 2>&1`.
  - [ ] CSS contains selectors for `.incident-review-card`, `.incident-review-main`, `.incident-score-ring`, `.incident-checklist-card`, `.incident-report-card`, `.incident-section-label`, `.incident-event span`, and `.incident-alert strong`.
  - [ ] CSS includes text-fit guards: `min-width: 0`, `overflow-wrap: anywhere`, and no negative `letter-spacing`.
  - [ ] Buttons and inputs keep visible focus styling through `:focus-visible` or an existing equivalent focus pattern.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: CSS contract contains designed incident surfaces
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_panel_has_polished_visual_structure -v
    Expected: PASS; test asserts visual class hooks and CSS selectors exist.
    Evidence: .omo/evidence/task-2-incident-drill-ui-polish-visual-green.txt

  Scenario: CSS avoids broad palette drift and negative tracking
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && (rg -n "letter-spacing:\\s*-" frontend/src/App.css || true; rg -n "incident-(review-card|score-ring|checklist-card|report-card|section-label)" frontend/src/App.css) | tee .omo/evidence/task-2-incident-drill-ui-polish-css-scan.txt
    Expected: no `letter-spacing: -...` lines; required incident selectors are listed.
    Evidence: .omo/evidence/task-2-incident-drill-ui-polish-css-scan.txt
  ```

  Commit: YES | Message: `fix(frontend): polish incident drill panel styling` | Files: [`frontend/src/App.css`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before `git commit`

- [ ] 3. Add empty/no-alert and not-replayed visual regression coverage

  What to do: Add or strengthen a source-contract test named `test_incident_drill_empty_state_stays_readable` in `tests/test_frontend_auth_gate.py`. The test must pin that no-alert fallback still uses `copy.noActiveAlert`, disabled non-replayable alerts still render, empty guidance lists are hidden or neutralized visually, and the disabled alert row remains readable. Implement the minimal CSS needed for the test to pass.
  Must NOT do: Do not remove the fallback alert object from `IncidentResponsePanel.tsx:186`; it is the current no-alert UI contract.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [2, 6] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:186` - fallback no-active-alert row
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:194` - disabled not-replayable alert behavior
  - Pattern:  `frontend/src/IncidentResponsePanel.tsx:212` - fallback guidance renders even before replay
  - Pattern:  `frontend/src/language.ts:133` - English no-active-alert copy
  - Pattern:  `frontend/src/language.ts:276` - Korean no-active-alert copy
  - Pattern:  `frontend/src/App.css:1264` - existing disabled alert style
  - Test:     `tests/test_frontend_auth_gate.py:100` - current source-level regression style for incident behavior
  - External: `https://playwright.dev/docs/locators` - browser QA should assert visible text and disabled controls by role/label

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_empty_state_stays_readable -v > .omo/evidence/task-3-incident-drill-ui-polish-red.txt 2>&1` fails before implementation because the new empty-state CSS/source contract is missing.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_empty_state_stays_readable -v > .omo/evidence/task-3-incident-drill-ui-polish-green.txt 2>&1` passes after implementation.
  - [ ] The test asserts `copy.noActiveAlert`, `disabled={!replayable}`, `.incident-alert:disabled`, `.incident-guidance ul:empty`, and `copy.notReplayable`.
  - [ ] Empty-state styling does not require a backend change or a new prop.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: empty-state source contract goes green
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_empty_state_stays_readable -v
    Expected: PASS; pytest output contains `test_incident_drill_empty_state_stays_readable PASSED`.
    Evidence: .omo/evidence/task-3-incident-drill-ui-polish-green.txt

  Scenario: no API contract drift while empty state is polished
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && git diff -- frontend/src/IncidentResponsePanel.tsx frontend/src/App.css tests/test_frontend_auth_gate.py | tee .omo/evidence/task-3-incident-drill-ui-polish-diff.txt
    Expected: diff has no backend file changes and no new endpoint strings.
    Evidence: .omo/evidence/task-3-incident-drill-ui-polish-diff.txt
  ```

  Commit: YES | Message: `fix(frontend): preserve incident drill empty state` | Files: [`frontend/src/App.css`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before `git commit`

- [ ] 4. Add mobile/narrow text-fit regression coverage

  What to do: Add a source-contract test named `test_incident_drill_mobile_layout_has_text_fit_guards` in `tests/test_frontend_auth_gate.py`. It must pin narrow-layout CSS for the incident header, alert rows, review card, report card, form controls, and replay timeline. Implement minimal CSS inside existing media-query areas at `frontend/src/App.css:1583` and `frontend/src/App.css:1642`.
  Must NOT do: Do not scale font size with viewport width, hide required controls, or rely on truncation for important incident text.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [2, 6] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/src/App.css:1583` - existing medium viewport breakpoint
  - Pattern:  `frontend/src/App.css:1642` - existing narrow viewport breakpoint
  - Pattern:  `frontend/src/App.css:1689` - existing mobile blackbox-event grid adaptation
  - Pattern:  `frontend/src/App.css:1412` - incident timeline row grid likely needs mobile adjustment
  - Pattern:  `frontend/src/App.css:1219` - incident header flex layout likely needs wrapping
  - Test:     `tests/test_frontend_auth_gate.py:21` - source/CSS assertion pattern
  - External: `https://playwright.dev/docs/next/screenshots` - browser QA should capture full-page and panel screenshots

  Acceptance criteria (agent-executable only):
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_mobile_layout_has_text_fit_guards -v > .omo/evidence/task-4-incident-drill-ui-polish-red.txt 2>&1` fails before implementation because mobile CSS guards are missing.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_mobile_layout_has_text_fit_guards -v > .omo/evidence/task-4-incident-drill-ui-polish-green.txt 2>&1` passes after implementation.
  - [ ] The test asserts `@media (max-width: 560px)`, `.incident-header`, `.incident-alert`, `.incident-review-main`, `.incident-report-card`, `.incident-event`, `grid-template-columns: 1fr`, and `overflow-wrap: anywhere`.
  - [ ] Narrow CSS keeps all incident action buttons visible and does not set `display: none` for `.incident-form`, `.incident-review-card`, or `.incident-report-card`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: mobile source contract goes green
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && .venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_mobile_layout_has_text_fit_guards -v
    Expected: PASS; pytest output contains `test_incident_drill_mobile_layout_has_text_fit_guards PASSED`.
    Evidence: .omo/evidence/task-4-incident-drill-ui-polish-green.txt

  Scenario: no hidden incident controls in mobile CSS
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && rg -n "incident-(form|review-card|report-card).*display:\\s*none|display:\\s*none.*incident-(form|review-card|report-card)" frontend/src/App.css | tee .omo/evidence/task-4-incident-drill-ui-polish-hidden-scan.txt || true
    Expected: output file is empty.
    Evidence: .omo/evidence/task-4-incident-drill-ui-polish-hidden-scan.txt
  ```

  Commit: YES | Message: `fix(frontend): tighten incident drill mobile layout` | Files: [`frontend/src/App.css`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before `git commit`

- [ ] 5. Prepare real-browser QA harness and cleanup receipts

  What to do: Create QA-only scripts under `.omo/evidence/` to drive real Chrome through the live dashboard. These scripts are evidence artifacts, not source files. They must start from fresh DB files, authenticate through the UI or API session, seed only the data needed for the scenario, capture screenshots/action logs, close browser contexts, and record cleanup receipts. Use Playwright with `channel: 'chrome'`; if Chrome is unavailable, download/use agent-browser from `https://github.com/vercel-labs/agent-browser` and record that fallback in the action log.
  Must NOT do: Do not commit QA-only scripts, DB files, screenshots, or action logs unless the user explicitly asks to commit evidence.

  Parallelization: Can parallel: YES | Wave 1 | Blocks: [6] | Blocked by: []

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/package.json:3` - dev server script uses Vite on `127.0.0.1`
  - Pattern:  `frontend/vite.config.ts:6` - `/api` and `/internal` proxy to backend port 8000
  - Pattern:  `frontend/src/App.tsx:945` - auth form that browser QA must clear
  - Pattern:  `apps/backend/main.py:124` - signup endpoint used by browser QA
  - Pattern:  `apps/backend/main.py:228` - internal event endpoint used to seed alert data
  - Pattern:  `apps/backend/incidents.py:43` - gas critical checklist labels used in browser assertions
  - External: `https://playwright.dev/docs/locators` - use role/label/text locators
  - External: `https://playwright.dev/docs/next/screenshots` - capture screenshots with explicit paths
  - External: `https://vite.dev/guide/cli/` - run Vite with explicit `--port`

  Acceptance criteria (agent-executable only):
  - [ ] QA script path exists after setup: `.omo/evidence/incident-drill-ui-polish-browser-qa.mjs`.
  - [ ] Script contains three scenario functions named `runHappyDrill`, `runEmptyDrill`, and `runMobileDrill`.
  - [ ] Script writes action logs to `.omo/evidence/task-5-incident-drill-ui-polish-happy-actions.txt`, `.omo/evidence/task-5-incident-drill-ui-polish-empty-actions.txt`, and `.omo/evidence/task-5-incident-drill-ui-polish-mobile-actions.txt`.
  - [ ] Script writes screenshots to `.omo/evidence/task-5-incident-drill-ui-polish-happy.png`, `.omo/evidence/task-5-incident-drill-ui-polish-empty.png`, and `.omo/evidence/task-5-incident-drill-ui-polish-mobile.png`.
  - [ ] Cleanup receipt written to `.omo/evidence/task-5-incident-drill-ui-polish-cleanup.txt`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: create QA harness file without committing it
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && test -f .omo/evidence/incident-drill-ui-polish-browser-qa.mjs && rg -n "runHappyDrill|runEmptyDrill|runMobileDrill|channel: 'chrome'|page.screenshot" .omo/evidence/incident-drill-ui-polish-browser-qa.mjs
    Expected: command exits 0 and lists all required functions plus Chrome/screenshot usage.
    Evidence: .omo/evidence/incident-drill-ui-polish-browser-qa.mjs

  Scenario: QA artifacts stay uncommitted
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && git status --short .omo/evidence | tee .omo/evidence/task-5-incident-drill-ui-polish-evidence-status.txt
    Expected: evidence files may be untracked or modified, but no source files are staged by this task.
    Evidence: .omo/evidence/task-5-incident-drill-ui-polish-evidence-status.txt
  ```

  Commit: NO | Message: `n/a` | Files: [`.omo/evidence/incident-drill-ui-polish-browser-qa.mjs`, `.omo/evidence/task-5-incident-drill-ui-polish-*.txt`, `.omo/evidence/task-5-incident-drill-ui-polish-*.png`, `.omo/evidence/task-5-incident-drill-ui-polish-*.db`]

- [ ] 6. Integrated validation, browser QA, backend regression, and cleanup

  What to do: After Tasks 1-5 are complete, run the exact targeted tests, build, backend incident regressions, browser QA, and cleanup. The executor must not declare completion from tests alone; browser evidence is required for all three user criteria.
  Must NOT do: Do not leave tmux sessions, bound ports, Chrome contexts, or temp directories running.

  Parallelization: Can parallel: NO | Wave 2 | Blocks: [] | Blocked by: [1, 2, 3, 4, 5]

  References (executor has NO interview context - be exhaustive):
  - Pattern:  `frontend/AGENTS.md:32` - required frontend validation commands
  - Pattern:  `tests/AGENTS.md:13` - frontend contracts read source text directly
  - Pattern:  `tests/test_backend.py:347` - replay API regression
  - Pattern:  `tests/test_backend.py:361` - not-started drill review regression
  - Pattern:  `tests/test_backend.py:376` - partial drill review regression
  - Pattern:  `tests/test_backend.py:418` - report after partial response regression
  - Pattern:  `frontend/package.json:4` - build runs TypeScript before Vite
  - External: `https://vite.dev/config/server-options` - note that Vite may fall through to another port unless explicit port handling is verified

  Acceptance criteria (agent-executable only):
  - [ ] Targeted source contracts pass: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py::test_incident_drill_panel_has_polished_visual_structure tests/test_frontend_auth_gate.py::test_incident_drill_empty_state_stays_readable tests/test_frontend_auth_gate.py::test_incident_drill_mobile_layout_has_text_fit_guards -v > .omo/evidence/task-6-incident-drill-ui-polish-contracts.txt 2>&1`.
  - [ ] Full frontend contract file passes: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py -v > .omo/evidence/task-6-incident-drill-ui-polish-frontend-contracts.txt 2>&1`.
  - [ ] Build passes: `npm --prefix frontend run build > .omo/evidence/task-6-incident-drill-ui-polish-build.txt 2>&1`.
  - [ ] Backend incident behavior is preserved: `.venv/bin/python -m pytest tests/test_backend.py::test_alert_replay_returns_incident_bundle tests/test_backend.py::test_alert_replay_includes_not_started_drill_review tests/test_backend.py::test_ack_alert_returns_partial_drill_review tests/test_backend.py::test_alert_report_returns_command_report_after_partial_response -v > .omo/evidence/task-6-incident-drill-ui-polish-backend-regression.txt 2>&1`.
  - [ ] Browser happy-path screenshot/action log exist and action log contains `Partial response`, `Incident command report`, `checkedCount: 1`, and `uncheckedCount: 2`.
  - [ ] Browser empty-state screenshot/action log exist and action log contains `No active alert`, `not replayable`, and `replayButtonDisabled: true`.
  - [ ] Browser mobile screenshot/action log exist and action log reports no horizontal overflow: `document.documentElement.scrollWidth <= document.documentElement.clientWidth`.
  - [ ] Cleanup receipt exists and confirms no `incident-ui-backend` or `incident-ui-frontend` tmux session remains and no process is listening on ports 8000 or 5176.
  - [ ] Diff hygiene passes: `git diff --check > .omo/evidence/task-6-incident-drill-ui-polish-diff-check.txt 2>&1`.

  QA scenarios (MANDATORY - task incomplete without these):
  ```
  Scenario: happy visual polish in browser
    Tool:     playwright(real Chrome)
    Steps:    cd /Users/chanpark/2n_project && rm -f .omo/evidence/task-6-incident-drill-ui-polish-happy.db; tmux new-session -d -s incident-ui-backend 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-6-incident-drill-ui-polish-happy.db\")), host=\"127.0.0.1\", port=8000)"'; tmux new-session -d -s incident-ui-frontend 'cd /Users/chanpark/2n_project && npm --prefix frontend run dev -- --host 127.0.0.1 --port 5176 --strictPort'; sleep 3; npx --yes -p playwright node .omo/evidence/incident-drill-ui-polish-browser-qa.mjs happy http://127.0.0.1:5176
    Expected: `.omo/evidence/task-6-incident-drill-ui-polish-happy-actions.txt` contains HTTP seed/signup success, `Partial response`, `Incident command report`, `checkedCount: 1`, `uncheckedCount: 2`; screenshot `.omo/evidence/task-6-incident-drill-ui-polish-happy.png` exists.
    Evidence: .omo/evidence/task-6-incident-drill-ui-polish-happy-actions.txt and .omo/evidence/task-6-incident-drill-ui-polish-happy.png

  Scenario: empty/no-alert or not-replayed state regression
    Tool:     playwright(real Chrome)
    Steps:    cd /Users/chanpark/2n_project && rm -f .omo/evidence/task-6-incident-drill-ui-polish-empty.db; tmux kill-session -t incident-ui-backend 2>/dev/null || true; tmux new-session -d -s incident-ui-backend 'cd /Users/chanpark/2n_project && .venv/bin/python -c "from pathlib import Path; import uvicorn; from apps.backend.main import create_app; uvicorn.run(create_app(db_path=Path(\".omo/evidence/task-6-incident-drill-ui-polish-empty.db\")), host=\"127.0.0.1\", port=8000)"'; sleep 2; npx --yes -p playwright node .omo/evidence/incident-drill-ui-polish-browser-qa.mjs empty http://127.0.0.1:5176
    Expected: `.omo/evidence/task-6-incident-drill-ui-polish-empty-actions.txt` contains `No active alert`, `not replayable`, `replayButtonDisabled: true`, and no uncaught browser console error; screenshot `.omo/evidence/task-6-incident-drill-ui-polish-empty.png` exists.
    Evidence: .omo/evidence/task-6-incident-drill-ui-polish-empty-actions.txt and .omo/evidence/task-6-incident-drill-ui-polish-empty.png

  Scenario: mobile/narrow layout and text-fit regression
    Tool:     playwright(real Chrome)
    Steps:    cd /Users/chanpark/2n_project && npx --yes -p playwright node .omo/evidence/incident-drill-ui-polish-browser-qa.mjs mobile http://127.0.0.1:5176
    Expected: `.omo/evidence/task-6-incident-drill-ui-polish-mobile-actions.txt` contains `viewport: 390x900`, `hasHorizontalOverflow: false`, visible `Acknowledge with evidence`, visible `Incident command report`, and screenshot `.omo/evidence/task-6-incident-drill-ui-polish-mobile.png` exists.
    Evidence: .omo/evidence/task-6-incident-drill-ui-polish-mobile-actions.txt and .omo/evidence/task-6-incident-drill-ui-polish-mobile.png

  Scenario: cleanup receipt
    Tool:     bash
    Steps:    cd /Users/chanpark/2n_project && tmux kill-session -t incident-ui-frontend 2>/dev/null || true; tmux kill-session -t incident-ui-backend 2>/dev/null || true; lsof -ti tcp:8000 tcp:5176 | xargs -r kill; { tmux ls 2>/dev/null || true; lsof -nP -iTCP:8000 -sTCP:LISTEN || true; lsof -nP -iTCP:5176 -sTCP:LISTEN || true; } > .omo/evidence/task-6-incident-drill-ui-polish-cleanup.txt
    Expected: cleanup file does not list `incident-ui-backend`, `incident-ui-frontend`, `:8000`, or `:5176` listeners.
    Evidence: .omo/evidence/task-6-incident-drill-ui-polish-cleanup.txt
  ```

  Commit: YES | Message: `fix(frontend): polish incident drill mode ui` | Files: [`frontend/src/IncidentResponsePanel.tsx`, `frontend/src/App.css`, `frontend/src/language.ts`, `tests/test_frontend_auth_gate.py`] | Approval-gated: ask before `git commit`

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
- Reference the plan file path in the final commit footer: `Plan: .omo/plans/incident-drill-ui-polish.md`.
- Do not commit evidence artifacts unless the user explicitly requests evidence in git.
- Ask before every commit; this repo already had dirty `.omo/ulw-loop` and `.omo/notepads` state during planning.

## Success criteria
- All Must-Have shipped; all QA scenarios pass with captured evidence; F1-F4 approved; commit history clean.
