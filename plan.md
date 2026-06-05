# Pico SafeRoom Technical Spec Artifact Plan

## Target outcome
- Create a current-project technical specification based on the example project spec structure.
- Include project-specific flowchart, system architecture, and DB schema images.
- Keep existing project docs untouched unless directly referenced.

## Success criteria
- Technical spec covers project name, period, roles, goals, stack, detailed implementation, diagrams, core code, flowchart, and references.
- Diagrams are stored as reusable image files and linked from the spec.
- Claims are grounded in inspected project files such as `README.ko.md`, `apps/backend/main.py`, `apps/backend/db/sqlite_repository.py`, `apps/collector/mqtt_parser.py`, and schema files.
- Generated files pass basic Markdown/link/XML validation.

## Relevant files
- `doc/project_technical_spec_2026-06-05.md`
- `doc/assets/saferoom_flowchart.svg`
- `doc/assets/saferoom_system_architecture.svg`
- `doc/assets/saferoom_db_schema.svg`

## Implementation checklist
- [x] Inspect example PDF structure.
- [x] Inspect current project docs and code.
- [x] Write current-project technical spec.
- [x] Create three SVG diagram images.
- [x] Validate generated Markdown links and SVG XML.

## Validation checks
- `python3` XML parse for generated SVGs.
- `python3` Markdown asset link check.
- `git diff --check`.

## Blockers
- None.
