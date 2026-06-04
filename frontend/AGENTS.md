# FRONTEND KNOWLEDGE

## OVERVIEW

Vite + React + TypeScript dashboard for auth, device liveness, readings, alerts, WebSocket updates, language toggle, and incident response.

## WHERE TO LOOK

| Task | Location | Notes |
| --- | --- | --- |
| Main dashboard/auth/realtime UI | `src/App.tsx` | Large central component; keep edits scoped. |
| Incident replay and acknowledgement | `src/IncidentResponsePanel.tsx` | Calls replay and ack endpoints. |
| English/Korean copy | `src/language.ts` | Add matching keys for both languages. |
| Styling | `src/App.css` | Single app stylesheet. |
| Dev proxy/build config | `vite.config.ts`, `package.json` | `/api` and `/internal` proxy to backend port 8000. |

## CONVENTIONS

- Use strict TypeScript; avoid weakening types or adding `any`.
- Build command is `npm --prefix frontend run build`, which runs `tsc` before Vite.
- There is no JS test runner; frontend behavior is partly enforced by `tests/test_frontend_auth_gate.py`.
- Keep fetch calls relative (`/api/...`, `/internal/...`) so Vite proxy and backend static serving both work.
- Use `credentials: 'include'` for auth/session requests.
- When adding visible copy, update `copyByLanguage` for both `en` and `ko`.

## ANTI-PATTERNS

- Do not add new dashboard text only in JSX when it belongs in `language.ts`.
- Do not break source-level assertions in `tests/test_frontend_auth_gate.py`.
- Do not rely on the Vite dev server for production routing; backend serves built `frontend/dist`.

## VALIDATION

```bash
npm --prefix frontend run build
.venv/bin/python -m pytest tests/test_frontend_auth_gate.py
```
