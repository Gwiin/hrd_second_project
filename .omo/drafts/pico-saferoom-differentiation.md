# Draft: Pico SafeRoom Differentiation

## Requirements (confirmed)
- User request: "I want to have 차별점 with other simillar projects in this project"
- Create a decision-complete `omo:ulw-plan` for differentiating the current Pico SafeRoom project from similar IoT safety dashboard projects.

## Technical Decisions
- Differentiation direction: Safety Incident Replay + Guided Response.
- Rationale: Similar projects commonly stop at MQTT sensor publishing, dashboards, and basic alerts. This repo already has real Pico 2W firmware, MQTT collector, FastAPI, SQLite, WebSocket, alerts, timeline, auth gate, and a polished dashboard. The most credible next differentiator is turning a raw alert into a response workflow with evidence, recommended action, and replayable incident context.
- Default scope: buildable software feature plan only; no new hardware actuator is required.
- Default language for plan: English, matching current instruction defaults.
- Test strategy: TDD for backend/data/API behavior; frontend static/behavior checks plus browser QA; agent-executed manual QA through HTTP and browser/tmux channels.

## Research Findings
- Repo identity: Pico SafeRoom is a local IoT safety monitoring project using four Raspberry Pi Pico 2W boards, MQTT, FastAPI, SQLite, WebSocket, React/Vite, and pywebview.
- Current docs: `README.ko.md:14` describes the real-sensor-to-dashboard flow; `doc/project_plan.md:20` lists current goals; `plan.md:28` already names differentiation as an unresolved checklist item.
- Current implementation: `apps/backend/main.py:56` exposes health/readings/devices/liveness/timeline/logs/alerts/auth/realtime endpoints; `apps/backend/store.py:133` computes safety state from gas and temperature thresholds.
- Current frontend: `frontend/src/App.tsx:175` owns the dashboard state surface and already consumes health, devices, readings, logs, alerts, timeline, liveness, and realtime WebSocket data.
- Current tests: `tests/test_backend.py:152` covers alert creation; `tests/test_backend.py:166` covers alert acknowledgement; `tests/test_backend.py:182` covers WebSocket reading events; `tests/test_frontend_auth_gate.py:9` covers frontend auth-gate expectations.
- External pattern: similar IoT/Pico projects commonly demonstrate MQTT publish/subscribe, sensor dashboards, smoke/gas alerts, or smartphone notifications, so a simple dashboard-only extension will not be differentiated enough.
- Memory constraint: prior user preference says fresh means moving away from passive monitoring/dashboard variants toward interaction, physical response, coordination, or proof-oriented validation.

## Open Questions
- None blocking. If the user later wants a stronger hardware differentiator, add an optional actuator/LED/buzzer command path as a follow-up plan.

## Scope Boundaries
- INCLUDE: incident snapshot model, response checklist/recommendation layer, incident replay API, alert acknowledgement with response note/evidence, dashboard incident panel, docs/demo script, tests, real-surface QA.
- EXCLUDE: new physical actuator wiring, external cloud notification services, AI/LLM assistant, new database engine, provider OAuth credential work, real four-board hardware bring-up.

## Skills Used
- `using-superpowers`: mandatory project skill gate.
- `omo:ulw-plan`: user explicitly requested strategic planning.
- GitHub/web research capability: used to inspect the referenced ecosystem and similar public project patterns.
- `explorer` subagent: read-only repo pattern and test-infra assessment.

## Clearance Check
- Core objective clearly defined: yes.
- Scope boundaries established: yes.
- No critical ambiguities remaining: yes.
- Technical approach decided: yes.
- Test strategy confirmed: yes, as default TDD plus manual QA.
- No blocking questions outstanding: yes.
