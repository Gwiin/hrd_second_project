# Statistics Graphs And LLM Placeholder Design

## Goal

Enhance the existing statistics and dashboard screens with visual room-level environment summaries and a non-functional LLM chat placeholder.

## Scope

In scope:
- Add room-by-room environment visuals to the existing Statistics tab.
- Show both latest room comparisons and a compact recent trend view.
- Add a dashboard chat-style panel as a future LLM placeholder.
- Keep English and Korean copy.

Out of scope:
- No GPT API integration.
- No `/api/chat` endpoint or frontend fetch.
- No API key, prompt template, model selector, streaming, embeddings, or real chat state.
- No new frontend dependency.

## Design

The Statistics tab will gain an environment section below the summary cards. It will use existing frontend data already fetched by the dashboard:
- `devices`
- `/api/readings/latest`
- `/api/timeline?limit=30`

The latest comparison view will render each room as a row with compact bar meters for temperature, humidity, light, gas, and motion. Missing readings will show a no-data state.

The recent trend view will use recent `reading` timeline events and render small SVG line charts by sensor. It will show a short empty state when there is not enough history.

The dashboard will gain a panel under the Blackbox timeline in the center column. It will look like a chat box, but all controls remain local-only and disabled/placeholder. The panel text will state that statistics-based LLM assistance is being prepared.

## Testing

Use the existing frontend source-contract test style:
- Assert statistics page has environment comparison and recent trend hooks.
- Assert the dashboard has an LLM chat placeholder.
- Assert no `/api/chat`, GPT API, API key, model selector, or real chat fetch exists.

Run:
- `.venv/bin/python -m pytest tests/test_frontend_auth_gate.py -q`
- `npm --prefix frontend run build`
- Browser QA for Statistics and Dashboard views.
