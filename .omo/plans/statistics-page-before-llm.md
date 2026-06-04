# Statistics Page Before LLM

## TL;DR
> **Summary**: Add a backend-backed statistics page for the data already visible on the Pico SafeRoom dashboard, with a compact `/api/stats` contract that can later feed a GPT API conversational layer. GPT/chat implementation is explicitly out of scope.
> **Deliverables**:
> - `/api/stats` dashboard statistics endpoint
> - Repository/store aggregation for dashboard-visible data
> - In-app React statistics view with navigation from the dashboard
> - English/Korean copy and styling consistent with the existing dashboard
> - RED->GREEN tests and manual QA evidence
> **Effort**: Medium
> **Parallel**: YES - 3 waves
> **Critical Path**: Task 1 -> Task 2 -> Task 3 -> Task 5

## Context

### Original Request

The user wants to make a statistics page showing statistics for the data visible on the dashboard, before implementing a conversational LLM through the GPT API that will use those statistics.

### Interview Summary

No extra user decision is required. Defaults applied:
- Build the statistics page now; do not implement GPT API calls, chat UI, prompts, embeddings, or model integration.
- Use a backend-backed `/api/stats` endpoint rather than frontend-only inference, because the future LLM needs a stable compact data contract.
- Make it an in-app statistics view/tab inside the existing authenticated dashboard shell, not a separate browser route, because the backend currently serves only `/` for the built frontend.
- Use all-time persisted reading aggregates plus current computed liveness/stale alert state. No date filters in this first page.

### Research Findings

- Current dashboard fetches `/api/health`, `/api/devices`, `/api/readings/latest`, `/api/logs`, `/api/alerts`, `/api/timeline?limit=12`, `/api/liveness` in `frontend/src/App.tsx`.
- Backend route map is `apps/backend/main.py`; store facade is `apps/backend/store.py`; SQLite persistence is `apps/backend/db/sqlite_repository.py`.
- No `/api/stats` route, stats repository method, stats page, or stats tests exist.
- Frontend copy lives in `frontend/src/language.ts`; visible copy must be added for both `en` and `ko`.
- Existing frontend tests are source-contract tests in `tests/test_frontend_auth_gate.py`; backend tests use `TestClient` and `tmp_path`.
- Worktree already has uncommitted `AGENTS.md` hierarchy changes from init-deep; implementers must not revert or modify those unless the user asks.

### Metis Review (gaps addressed)

- Exact metrics are defined below.
- Navigation is an in-app tab/view, not `/stats` route.
- `/api/stats` response shape is testable and future LLM-ready through an `llm_context` object.
- Stats include persisted readings/alerts plus computed stale alerts and liveness from existing repository methods.
- Empty-state, fetch-error, auth pattern, performance scope, and manual QA commands are specified.

## Work Objectives

### Core Objective

Create a statistics page that summarizes the same operational data currently visible on the dashboard and exposes the same summary through `/api/stats`.

### Deliverables

- `apps/backend/db/sqlite_repository.py`: new `stats()` method.
- `apps/backend/store.py`: new `stats()` facade method that includes current safety state.
- `apps/backend/main.py`: new `GET /api/stats` route.
- `frontend/src/App.tsx`: new stats state, fetch, view navigation, and statistics rendering.
- `frontend/src/language.ts`: English/Korean statistics copy.
- `frontend/src/App.css`: statistics view styling.
- `tests/test_backend.py`: `/api/stats` API tests.
- `tests/test_sqlite_repository.py`: repository aggregation tests.
- `tests/test_frontend_auth_gate.py`: frontend source-contract tests for stats page.

### Definition of Done

- `.venv/bin/python -m pytest tests/test_sqlite_repository.py tests/test_backend.py tests/test_frontend_auth_gate.py` exits 0.
- `npm --prefix frontend run build` exits 0.
- HTTP manual QA against a running backend captures `/api/stats` with expected JSON.
- Browser manual QA against the real page captures the authenticated statistics view screenshot.
- No GPT API/chat code exists in the diff.
- Existing dashboard view, auth gate, incident response, language toggle, and backend fallback behavior remain intact.

### Must Have

- `/api/stats` returns this schema:

```json
{
  "generated_at": "ISO-8601 string",
  "time_window": {
    "kind": "all_time",
    "label": "All persisted readings"
  },
  "summary": {
    "safety_state": "safe|warning|critical",
    "last_update": "ISO-8601 string|null",
    "total_devices": 4,
    "online_devices": 0,
    "offline_devices": 4,
    "total_readings": 0,
    "total_alerts": 0,
    "open_alerts": 0,
    "critical_alerts": 0,
    "warning_alerts": 0,
    "stale_sensor_count": 0
  },
  "device_breakdown": [
    {
      "device_id": "pico-safe-001",
      "zone_id": "room-1",
      "status": "online|offline",
      "latest_sensor_count": 0,
      "stale_sensor_count": 0,
      "alert_count": 0
    }
  ],
  "sensor_breakdown": [
    {
      "sensor_id": "temperature",
      "unit": "celsius",
      "count": 2,
      "min": 21.0,
      "max": 24.0,
      "average": 22.5,
      "latest_value": 24.0,
      "latest_device_id": "pico-safe-001",
      "latest_quality": "good",
      "quality_counts": {"good": 2}
    }
  ],
  "alert_breakdown": {
    "by_level": {"critical": 0, "warning": 0, "info": 0},
    "by_status": {"open": 0, "acknowledged": 0}
  },
  "timeline_breakdown": {
    "reading_events": 0,
    "alert_events": 0,
    "log_events": 0,
    "device_heartbeat_events": 0,
    "process_heartbeat_events": 0
  },
  "llm_context": {
    "headline": "Safe state with 0 readings and 4 offline devices.",
    "bullets": [
      "Safety state: safe",
      "Devices online: 0/4",
      "Open alerts: 0"
    ]
  }
}
```

- Numeric sensor stats include `count`, `min`, `max`, `average`, latest value/device/quality, and quality counts.
- Boolean motion stats include `count`, `true_count`, `false_count`, latest value/device/quality, and quality counts; omit `min`, `max`, and `average` for motion.
- `total_alerts`, alert counts, and stale counts include computed stale alerts from `alerts()` even though those have `alert_id: null`.
- Empty database returns 200 with default devices, zero counts, empty `sensor_breakdown`, and `llm_context` bullets.
- Frontend shows loading, error, and empty states for statistics.
- Frontend statistics copy exists in English and Korean.

### Must NOT Have

- No GPT API calls, API key handling, chat UI, model selection, prompt templates, embeddings, streaming, or vector search.
- No new frontend router dependency.
- No schema changes to existing ingestion payloads.
- No hardware/MQTT behavior changes.
- No auth model changes; preserve current pattern where UI is auth-gated but dashboard data APIs are not session-protected.
- No changes to unrelated `AGENTS.md` files unless required by merge conflict resolution.

## Verification Strategy

> ZERO HUMAN INTERVENTION - all verification is agent-executed.

- Test decision: TDD RED-GREEN with existing pytest and TypeScript build.
- QA policy: Every task has agent-executed scenarios.
- Evidence directory: `.omo/evidence/`
- Manual QA channels:
  - HTTP call for `/api/stats`.
  - Browser use for statistics view.
  - HTTP call for adjacent backend regression.

## Execution Strategy

### Parallel Execution Waves

Wave 1: Task 1 repository stats contract.
Wave 2: Task 2 API route/store facade and Task 4 frontend source-contract test can proceed after Task 1 schema is fixed.
Wave 3: Task 3 frontend implementation and Task 5 full QA.

### Dependency Matrix

| Task | Depends On | Blocks |
| --- | --- | --- |
| 1. Repository statistics aggregation | None | 2, 3, 5 |
| 2. `/api/stats` endpoint | 1 | 3, 5 |
| 3. Statistics frontend view | 1, 2, 4 | 5 |
| 4. Frontend contract tests | 1 schema decision | 3, 5 |
| 5. Full verification and manual QA | 1, 2, 3, 4 | Final |

## TODOs

- [x] 1. Add repository-level statistics aggregation with RED-GREEN tests

  **What to do**:
  1. In `tests/test_sqlite_repository.py`, write failing tests before production code:
     - `test_repository_stats_returns_empty_dashboard_summary`
     - `test_repository_stats_aggregates_visible_dashboard_data`
  2. Seed exact events through `SQLiteRepository.add_event()` using existing `make_event()` pattern:
     - `stats-temp-1`: device `pico-safe-001`, sensor `temperature`, value `21.0`, unit `celsius`, timestamp `2026-06-04T09:00:00+09:00`.
     - `stats-temp-2`: same device/sensor, value `24.0`, timestamp `2026-06-04T09:01:00+09:00`.
     - `stats-gas-critical`: same device, sensor `gas`, value `601.0`, unit `ppm`, timestamp `2026-06-04T09:02:00+09:00`.
     - `stats-motion`: same device, sensor `motion`, value `true`, unit `boolean`, timestamp `2026-06-04T09:03:00+09:00`.
  3. Add `SQLiteRepository.stats() -> dict[str, Any]`.
  4. Implement aggregation with SQL queries over existing tables and reuse `devices()`, `latest_readings()`, `alerts()`, and `timeline()` semantics where practical.
  5. Include computed stale alerts in counts by calling/reusing `_stale_sensor_alerts(conn)` inside the same connection.

  **Must NOT do**:
  - Do not change table schemas.
  - Do not change `latest_readings()`, `alerts()`, `timeline()`, or `devices()` response shapes.
  - Do not add a time-window query parameter in this task.

  **Parallelization**: Can Parallel: NO | Wave 1 | Blocks: 2, 3, 5 | Blocked By: none

  **References**:
  - Pattern: `tests/test_sqlite_repository.py:7` - `make_event()` helper and repository assertions.
  - Pattern: `apps/backend/db/sqlite_repository.py:90` - `latest_readings()` payload loading.
  - Pattern: `apps/backend/db/sqlite_repository.py:260` - `alerts()` combines persisted and stale alerts.
  - Pattern: `apps/backend/db/sqlite_repository.py:506` - table definitions.
  - Contract: `shared/schemas/sensor_event.py` - event payload model.

  **Acceptance Criteria**:
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_sqlite_repository.py -k "stats"`, failing because `SQLiteRepository.stats` is missing or expected fields are absent.
  - [ ] GREEN captured: same command exits 0 after implementation.
  - [ ] Empty stats response has four devices, zero readings, zero alerts, `sensor_breakdown == []`, and three `llm_context.bullets`.
  - [ ] Seeded stats response has `total_readings == 4`, `critical_alerts == 1`, temperature average `22.5`, gas max `601.0`, and motion `true_count == 1`.

  **QA Scenarios**:
  ```
  Scenario: Repository empty stats
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_sqlite_repository.py::test_repository_stats_returns_empty_dashboard_summary -q
    Expected: exit 0 and assertion confirms zero-count empty summary
    Evidence: .omo/evidence/task-1-repository-empty-green.txt

  Scenario: Repository seeded stats
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_sqlite_repository.py::test_repository_stats_aggregates_visible_dashboard_data -q
    Expected: exit 0 and assertion confirms average, alert, and motion counts
    Evidence: .omo/evidence/task-1-repository-seeded-green.txt
  ```

  **Commit**: YES | Message: `feat(stats): add repository dashboard statistics` | Files: `apps/backend/db/sqlite_repository.py`, `tests/test_sqlite_repository.py`

- [x] 2. Expose `/api/stats` through store and FastAPI with RED-GREEN tests

  **What to do**:
  1. In `tests/test_backend.py`, write failing tests before production code:
     - `test_stats_api_returns_empty_dashboard_summary`
     - `test_stats_api_aggregates_readings_alerts_liveness_and_llm_context`
  2. Add `ReadingStore.stats()` in `apps/backend/store.py`.
  3. Add `@app.get("/api/stats") def stats() -> dict:` in `apps/backend/main.py`.
  4. Ensure `summary.safety_state` uses the same state rules as `ReadingStore.health()`.
  5. Ensure route returns 200 with the exact schema defined in this plan.

  **Must NOT do**:
  - Do not require login for `/api/stats`.
  - Do not add GPT/LLM fields beyond the deterministic `llm_context` object.
  - Do not rename existing endpoints or change current fetches.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 3, 5 | Blocked By: 1

  **References**:
  - Pattern: `apps/backend/main.py:62` - `/api/health` route style.
  - Pattern: `apps/backend/store.py:46` - health facade and safety state.
  - Pattern: `tests/test_backend.py:60` - `TestClient(make_app(tmp_path))`.
  - Pattern: `tests/test_backend.py:131` - internal event ingestion then API assertion.

  **Acceptance Criteria**:
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_backend.py -k "stats_api"`, failing because `/api/stats` is 404 or fields are missing.
  - [ ] GREEN captured: same command exits 0 after implementation.
  - [ ] `GET /api/stats` returns 200 for empty DB and seeded DB.
  - [ ] Seeded gas critical event makes `summary.safety_state == "critical"` and `llm_context.headline` mention `critical`.

  **QA Scenarios**:
  ```
  Scenario: HTTP stats endpoint with seeded data
    Tool: HTTP call
    Steps:
      1. Start backend: .venv/bin/python -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000
      2. curl -i -X POST http://127.0.0.1:8000/internal/events -H 'Content-Type: application/json' -d '{"event_id":"qa-stats-gas","site_id":"safe-room-lab","zone_id":"room-1","device_id":"pico-safe-001","sensor_id":"gas","protocol":"mock","value":601,"unit":"ppm","timestamp":"2026-06-04T12:00:00+09:00","quality":"good","metadata":{"qa":true}}'
      3. curl -i http://127.0.0.1:8000/api/stats
    Expected: HTTP/1.1 200 OK; body has "safety_state":"critical", "critical_alerts":1, and "llm_context"
    Evidence: .omo/evidence/task-2-http-stats.txt

  Scenario: HTTP stats endpoint empty state
    Tool: HTTP call
    Steps:
      1. Start backend with a fresh temp database
      2. curl -i http://127.0.0.1:8000/api/stats
    Expected: HTTP/1.1 200 OK; body has "total_devices":4, "total_readings":0, "sensor_breakdown":[]
    Evidence: .omo/evidence/task-2-http-stats-empty.txt
  ```

  **Commit**: YES | Message: `feat(stats): expose dashboard statistics api` | Files: `apps/backend/main.py`, `apps/backend/store.py`, `tests/test_backend.py`

- [x] 3. Add authenticated in-app statistics view with RED-GREEN frontend contract

  **What to do**:
  1. After Task 4 RED tests are written, implement frontend behavior.
  2. In `frontend/src/App.tsx`, add types:
     - `StatsSummary`, `DeviceStat`, `SensorStat`, `AlertBreakdown`, `TimelineBreakdown`, `StatsResponse`.
  3. Add state:
     - `const [activeView, setActiveView] = useState<'dashboard' | 'statistics'>('dashboard');`
     - `const [stats, setStats] = useState<StatsResponse | null>(null);`
     - `const [statsError, setStatsError] = useState(false);`
  4. Extend the existing refresh `Promise.all` to fetch `/api/stats`.
  5. If stats fetch fails, keep dashboard usable and set `statsError`.
  6. Add topbar or workspace navigation buttons using copy keys:
     - `copy.app.dashboard`
     - `copy.stats.title`
     - `copy.stats.description`
  7. Render dashboard view exactly as now when `activeView === 'dashboard'`.
  8. Render statistics view when `activeView === 'statistics'`:
     - summary cards: safety state, devices online, total readings, open alerts, stale sensors
     - sensor breakdown table/cards
     - device breakdown list
     - alert breakdown
     - LLM-ready context preview using `stats.llm_context.headline` and bullets, labeled as future analysis context, not a chat
  9. Preserve auth gate: unauthenticated users still see blurred dashboard and login modal.

  **Must NOT do**:
  - Do not add React Router or a new dependency.
  - Do not move the whole app into many new files unless necessary; if extraction is needed, create only `frontend/src/StatisticsView.tsx`.
  - Do not add a chat input, GPT button, API key field, or model selector.
  - Do not remove existing dashboard, incident response, logs, liveness, language toggle, or sign-out behavior.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: 5 | Blocked By: 1, 2, 4

  **References**:
  - Pattern: `frontend/src/App.tsx:235` - existing refresh loop and fetch handling.
  - Pattern: `frontend/src/App.tsx:392` - language toggle rendering.
  - Pattern: `frontend/src/App.tsx:489` - reading card mapping.
  - Pattern: `frontend/src/IncidentResponsePanel.tsx:61` - optional component extraction style.
  - Pattern: `frontend/src/language.ts:30` - English/Korean copy structure.
  - Pattern: `frontend/src/App.css:77` - shared panel/card styling.

  **Acceptance Criteria**:
  - [ ] RED captured from Task 4 frontend contract test before implementation.
  - [ ] GREEN captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py -k "statistics"` exits 0.
  - [ ] `npm --prefix frontend run build` exits 0.
  - [ ] Authenticated user can switch between Dashboard and Statistics views.
  - [ ] Statistics view renders error message when `/api/stats` fetch fails.
  - [ ] English and Korean labels are both present.

  **QA Scenarios**:
  ```
  Scenario: Browser statistics happy path
    Tool: Browser use
    Steps:
      1. Start backend on http://127.0.0.1:8000 after npm --prefix frontend run build.
      2. Seed gas and temperature events with curl commands from Task 2.
      3. Open http://127.0.0.1:8000.
      4. Sign up with email qa-stats@example.com and password qa-stats-pass.
      5. Click the Statistics navigation button.
      6. Capture screenshot.
    Expected: page shows "Statistics", "Critical", "Total readings", "Open alerts", and an LLM context preview headline.
    Evidence: .omo/evidence/task-3-browser-statistics.png

  Scenario: Browser statistics Korean copy
    Tool: Browser use
    Steps:
      1. On the same running page, click "한국어".
      2. Click the Statistics navigation button if not already selected.
      3. Capture screenshot.
    Expected: page shows Korean statistics labels, including "통계" and "LLM 분석 컨텍스트".
    Evidence: .omo/evidence/task-3-browser-statistics-ko.png
  ```

  **Commit**: YES | Message: `feat(frontend): add dashboard statistics view` | Files: `frontend/src/App.tsx`, optional `frontend/src/StatisticsView.tsx`, `frontend/src/language.ts`, `frontend/src/App.css`

- [x] 4. Add frontend source-contract tests before UI implementation

  **What to do**:
  1. In `tests/test_frontend_auth_gate.py`, add failing tests before Task 3 production code:
     - `test_dashboard_fetches_statistics_endpoint`
     - `test_dashboard_has_statistics_navigation_and_llm_context_preview`
     - `test_dashboard_has_korean_statistics_copy`
  2. Assertions must be source-level and stable:
     - `fetch('/api/stats')`
     - `activeView`
     - `setActiveView('statistics')`
     - `Statistics`
     - Korean copy for statistics
     - No GPT endpoint or chat input string.
  3. Run the tests and capture RED before Task 3.

  **Must NOT do**:
  - Do not assert brittle full JSX blocks.
  - Do not require a new frontend test framework.
  - Do not weaken existing auth/incident/language tests.

  **Parallelization**: Can Parallel: YES | Wave 2 | Blocks: 3, 5 | Blocked By: schema decision from 1

  **References**:
  - Pattern: `tests/test_frontend_auth_gate.py:11` - `frontend_source()` helper.
  - Pattern: `tests/test_frontend_auth_gate.py:72` - language toggle source assertions.
  - Pattern: `tests/test_frontend_auth_gate.py:132` - finite label/copy assertions.

  **Acceptance Criteria**:
  - [ ] RED captured: `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py -k "statistics"`, failing because stats endpoint/view/copy strings are missing.
  - [ ] GREEN captured after Task 3: same command exits 0.
  - [ ] Existing `tests/test_frontend_auth_gate.py` tests still pass.

  **QA Scenarios**:
  ```
  Scenario: Source contract catches missing stats view
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_frontend_auth_gate.py -k "statistics" -q before frontend implementation
    Expected: exits non-zero with assertion failure mentioning missing fetch('/api/stats') or Statistics copy
    Evidence: .omo/evidence/task-4-frontend-stats-red.txt

  Scenario: Source contract passes after stats view
    Tool: bash
    Steps: .venv/bin/python -m pytest tests/test_frontend_auth_gate.py -k "statistics" -q after frontend implementation
    Expected: exits 0
    Evidence: .omo/evidence/task-4-frontend-stats-green.txt
  ```

  **Commit**: YES | Message: `test(frontend): cover statistics view contract` | Files: `tests/test_frontend_auth_gate.py`

- [x] 5. Run full validation and real-surface manual QA

  **What to do**:
  1. Run targeted tests:
     - `.venv/bin/python -m pytest tests/test_sqlite_repository.py tests/test_backend.py tests/test_frontend_auth_gate.py`
  2. Run build:
     - `npm --prefix frontend run build`
  3. Run full pytest if targeted checks pass:
     - `.venv/bin/python -m pytest`
  4. Start backend with built frontend:
     - `.venv/bin/python -m uvicorn apps.backend.main:app --host 127.0.0.1 --port 8000`
  5. Capture HTTP QA for `/api/stats`.
  6. Capture browser QA screenshots for statistics page in English and Korean.
  7. Tear down backend process and any browser/session resources.
  8. Confirm `git status --short` contains only intended files plus pre-existing `AGENTS.md` changes unless the user separately asks to handle those.

  **Must NOT do**:
  - Do not leave a backend server, browser context, tmux session, or bound port running.
  - Do not commit unless the user explicitly approves.
  - Do not report completion if manual browser QA is missing.

  **Parallelization**: Can Parallel: NO | Wave 3 | Blocks: Final | Blocked By: 1, 2, 3, 4

  **References**:
  - Command source: `AGENTS.md` and `SETUP.md`.
  - Frontend build source: `frontend/package.json`.
  - Backend launch source: `apps/backend/main.py`.

  **Acceptance Criteria**:
  - [ ] Targeted pytest command exits 0.
  - [ ] Full pytest exits 0 or pre-existing unrelated failures are documented with proof.
  - [ ] Frontend build exits 0.
  - [ ] HTTP `/api/stats` QA artifact exists and contains 200 status plus expected JSON.
  - [ ] Browser QA screenshots exist for English and Korean statistics views.
  - [ ] Cleanup receipt recorded: backend stopped and no QA process remains.

  **QA Scenarios**:
  ```
  Scenario: Adjacent dashboard regression
    Tool: Browser use
    Steps:
      1. Open http://127.0.0.1:8000.
      2. Sign in or sign up.
      3. Verify default Dashboard view still shows Latest readings, Blackbox timeline, Incident response, Liveness, and System log.
      4. Capture screenshot.
    Expected: all existing dashboard sections visible; no statistics-only regression
    Evidence: .omo/evidence/task-5-browser-dashboard-regression.png

  Scenario: Backend adjacent API regression
    Tool: HTTP call
    Steps:
      curl -i http://127.0.0.1:8000/api/health
      curl -i http://127.0.0.1:8000/api/readings/latest
      curl -i http://127.0.0.1:8000/api/alerts
    Expected: all return HTTP 200; response shapes remain existing top-level keys
    Evidence: .omo/evidence/task-5-http-adjacent-regression.txt
  ```

  **Commit**: YES | Message: `feat(stats): add dashboard statistics page` | Files: all files changed by Tasks 1-4

## Final Verification Wave

> ALL must APPROVE. Present consolidated results to user and get explicit approval before committing or pushing.

- [x] F1. Plan Compliance Audit
  - Verify all tasks were executed in order.
  - Verify every production change had a RED test first.
  - Verify no GPT/chat implementation slipped into the diff.

- [x] F2. Code Quality Review
  - Review backend aggregation for type safety, SQL correctness, and response stability.
  - Review frontend for strict TypeScript, no `any`, no new dependencies, no broad refactor.

- [x] F3. Real Manual QA
  - Verify HTTP evidence files.
  - Verify browser screenshots and action logs.
  - Verify cleanup receipts.

- [x] F4. Scope Fidelity Check
  - Confirm statistics page is delivered.
  - Confirm LLM integration remains future-ready only through `/api/stats.llm_context`.
  - Confirm existing dashboard/auth/incident views still work.

## Commit Strategy

- Do not commit automatically.
- If the user approves, stage only intended files.
- Recommended single commit after all validation:
  - `feat(stats): add dashboard statistics page`
- Include plan footer if committing:
  - `Plan: .omo/plans/statistics-page-before-llm.md`

## Success Criteria

- Backend stats endpoint exists and is tested RED->GREEN.
- Repository aggregation exists and is tested RED->GREEN.
- Frontend statistics view exists and is tested RED->GREEN.
- English/Korean statistics copy exists.
- Manual HTTP QA proves `/api/stats`.
- Manual browser QA proves the user-facing statistics page.
- No GPT API integration was implemented.
