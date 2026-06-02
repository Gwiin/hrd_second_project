# Pico SafeRoom Active Goal Plan

## Target outcome
- Support email/password signup and login.
- Support Google, Apple, and Kakao social login.
- Keep the login UI visually consistent with the Apple Liquid Glass dashboard.
- Run the system through either pywebview or a normal browser.
- Default runtime uses real Pico 2W boards through MQTT; the simulator remains separate.
- Identify a clear differentiation direction for the project beyond a generic IoT dashboard.

## Current evidence
- `ff0ef3e` on `main` added the auth backend, social OAuth callback flow, blurred auth gate, real-board launcher default, and setup docs.
- `apps.desktop.app` defaults to pywebview and supports `--open browser`.
- `apps.desktop.app` starts `apps.collector.mqtt_client` by default, not the simulator collector.
- `SETUP.md` and `SETUP.ko.md` document OAuth environment variables, desktop/browser launch, and separate simulator execution.
- Local rendered QA verified signup, visible sign-out, post-logout auth gate, and mobile auth layout. The WebSocket 404 found during QA was traced to a missing runtime dependency and fixed by adding `websockets`.

## Implementation checklist
- [x] Email/password signup, login, session cookie, and logout backend.
- [x] Google, Apple, Kakao OAuth start and callback exchange paths.
- [x] Blurred pre-login dashboard with Apple-style auth card.
- [x] Real Pico 2W MQTT collector as the launcher default.
- [x] Browser launch mode through `apps.desktop.app --open browser`.
- [x] Simulator documented as a separate development/test command.
- [x] Dashboard-visible logout action.
- [x] WebSocket runtime dependency included for Uvicorn browser runs.
- [x] Favicon route added to avoid browser resource 404 noise.
- [ ] Differentiation direction selected and translated into either UI, docs, or a buildable feature plan.
- [ ] Live OAuth provider credentials registered and tested outside mocked callback tests.
- [ ] Real four-board sensor bring-up verified with MQTT messages from hardware.

## Validation checks
- `.venv/bin/python -m pytest -v`
- `npm --prefix frontend run build`
- `git diff --check`
- Rendered auth/dashboard smoke test in browser or Playwright when UI changes.

## Open blockers
- Live Google/Apple/Kakao OAuth verification requires real provider console credentials and registered redirect URLs.
- Real hardware bring-up requires the four Pico 2W boards, sensors, Wi-Fi settings, and MQTT broker reachable from the devices.
