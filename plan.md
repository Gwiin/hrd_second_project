# Smart Indoor Safety Monitoring Documentation Plan

## Target outcome
- Adopt topic 1: smart indoor environmental safety monitoring system.
- Write a new project plan and technical specification.
- Reflect required constraints from `doc/2nd_project.md`.
- Use selected optional items enough to make the topic technically rich without over-scoping MVP.

## Success criteria
- Required constraints are clearly addressed:
  - Raspberry Pi Pico 2W device
  - pywebview desktop dashboard
  - multi-process micro-architecture
- Recommended optional items are included:
  - MQTT, WebSocket, SQLite, FastAPI
  - SensorEvent normalization
  - device registry, heartbeat, alert, logs
  - optional Matter/Mobius/RTOS/C++ core roadmap
- Documents are saved under `doc/`.
- Old generated planning/technical docs are replaced with the new topic docs.

## Relevant files
- `AGENTS.md`
- `doc/2nd_project.md`
- `doc/project_plan.md`
- `doc/technical_spec.md`

## Checklist
- [x] Re-check project constraints.
- [x] Confirm retained files.
- [x] Write project plan.
- [x] Write technical specification.
- [x] Validate required constraints and unresolved placeholders.

## Open items
- `openssh_setup.log` is still locked by the previous elevated OpenSSH setup process and cannot be removed until that process exits or is terminated.
