# Active Context

## Current Task
Implementing the Claude-style Agent Skills PoC in Google ADK.

## Status
- [x] Initialized `.clinerules` with identity and protocol definitions.
- [x] Created `memory-bank/` directory with all core files.
- [x] Verified Memory Bank protocol via smoke test on `smoke-test-memory-bank` branch.
- [x] Implemented structured logging in `NumberGuesser` agent.
- [x] Scaffolding for `agent_with_skills_register_user` completed.
- [x] Implemented `SkillRegistry` for markdown skill parsing.
- [x] Implemented `DynamicSkillToolset` for runtime tool injection.
- [x] Created specialized skills for user registration and team assignment using the required markdown format.
- [x] Implemented dynamic instruction provider for skill content injection.
- [x] Verified `SkillRegistry` with unit tests.

## Active Decisions
- Adopting the 4-layer architecture guideline from `docs/adk-system-infrastructure-design-guideline.md` as a core system pattern.
- Using `uv` as the primary tool for environment management.
- Ensuring all future agent modifications follow the DDD and SOLID principles as mandated by the constitution.
- Using `structlog` for structured logging in agents, capturing `correlation_id` via `StructuredLoggingPlugin`.
- **Testing Policy**: Unit tests are mandatory for all Python functions and tools (e.g., plugins), but not for agents themselves.

## Next Steps
1. Request permission to commit and push the unit tests and updated `.clinerules`.
2. Confirm completion with user.
