# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Install dependencies
uv sync

# Activate virtual environment
. ./.venv/bin/activate

# Lint and auto-fix
uv run ruff check --fix <path>

# Run unit tests
uv run pytest

# Run integration tests (starts FastAPI service)
./start.sh

# Run a single agent interactively
adk run src/agent_react_number_guesser/agent.py

# Add a dependency
uv add <package>
```

Inspect installed ADK source when in doubt about internal class interfaces:
`.venv/lib/python3.12/site-packages` or `.venv/lib64/python3.12/site-packages`

## Architecture

### Project Structure

Each agent lives in its own `src/agent_*/` directory and exposes a Google ADK `App` object. Shared utilities are in `src/common/` (AI model config, OTEL plugin, structured logging plugin). A companion `dummy_fastapi_service/` provides REST endpoints the agents call during demos.

### 4-Layer System Instruction Pattern

Every agent's `instruction` string (or `InstructionProvider` callable) is structured as four strict layers in order:

| Layer | Purpose |
|-------|---------|
| **[0] Meta-Layer** | Agent identity, scope rejection, prompt-injection defense |
| **[1] Observability** | Mandatory `<thought_process>` XML before every tool call or answer |
| **[2] FSM Logic** | Explicit state machine: Trigger → State → Action → Transition |
| **[3] Tool Contracts** | Pre/post-condition rules for each tool, semantic-logic mapping |

Refer to [docs/adk-system-infrastructure-design-guideline.md](docs/adk-system-infrastructure-design-guideline.md) as the canonical reference.

### Variable Syntax in Prompts

| Syntax | Use | Source |
|--------|-----|--------|
| `{var?}` | Runtime injection from Python (null-safe) | External environment |
| `<var>` | LLM-internal chain-of-thought variables | Model inference only |

**Never** use bare `{}` for LLM-internal variables — this is a common bug.

### Agent Patterns

- **ReAct** (`agent_react_number_guesser`): Think → Act → Observe → Rethink loop.
- **Progressive Disclosure** (`agent_progressive_disclosure`, `agent_pd_troubleshooting`): Planner + Executor coordinated by `LoopAgent`; each step discloses only the relevant API docs/context to the executor.
- **Dynamic Skills** (`agent_with_skills_register_user`): Runtime skill loading via `AgentSkillRegistry` (BM25 search over markdown files), `DynamicSkillToolset` (injects tools based on session state), and `InstructionProvider` (augments base prompt with active skill content). Skills are markdown files in `src/agent_with_skills_register_user/skills/`.

### Common Components (`src/common/`)

- `ai_model.py` — defines `GEMINI_MODEL` constant and `OPENROUTE_MODEL` (LiteLLM wrapper); import from here rather than hardcoding model strings.
- `otel_plugin.py` — `OtelTracingPlugin` exports spans to `http://localhost:5000/v1/traces`; requires a running OTLP collector.
- `logging_plugin.py` — `StructuredLoggingPlugin` adds `correlation_id` and `agent_name` to every log via `structlog`.

### Memory Bank Protocol

`memory-bank/` is the project's source of truth for persistent context (not code). Read `activeContext.md` and `projectbrief.md` before starting any significant task. Update `activeContext.md` and `progress.md` after completing work. If asked to "Update Memory Bank", review and reconcile all files in the directory against current codebase reality.

### Testing Policy

Unit tests are mandatory for all Python functions and tools (e.g., plugins, tool functions). Tests for agents themselves are not required.
