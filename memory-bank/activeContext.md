# Active Context

## Current Task
Implementing the Claude-style Agent Skills PoC in Google ADK.

## Status
- [x] Initialized `.clinerules` with identity and protocol definitions.
- [x] Created `memory-bank/` directory with all core files.
- [x] Verified Memory Bank protocol via smoke test on `smoke-test-memory-bank` branch.
- [x] Implemented structured logging in `NumberGuesser` agent.
- [x] **Claude-style Agent Skills PoC**:
    - [x] Implemented `AgentSkillRegistry` with BM25 hybrid search.
    - [x] Implemented `AgentToolRegistry` for decorator-based tool management.
    - [x] Developed `DynamicSkillToolset` for runtime tool injection based on session state.
    - [x] Created `InstructionProvider` for dynamic prompt augmentation.
    - [x] Integrated with `dummy_fastapi_service` for user/team management.
    - [x] Documented architecture and lifecycle in `src/agent_with_skills_register_user/README.md`.

## Active Decisions
- Adopting the 4-layer architecture guideline from `docs/adk-system-infrastructure-design-guideline.md` as a core system pattern.
- Using `uv` as the primary tool for environment management.
- Ensuring all future agent modifications follow the DDD and SOLID principles as mandated by the constitution.
- Using `structlog` for structured logging in agents, capturing `correlation_id` via `StructuredLoggingPlugin`.
- **Testing Policy**: Unit tests are mandatory for all Python functions and tools (e.g., plugins), but not for agents themselves.

## Next Steps
1. Request permission to commit and push the unit tests and updated `.clinerules`.
2. Confirm completion with user.
