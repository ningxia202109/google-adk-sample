# Coding Conventions

## Language & Tooling

- **Python >= 3.11** required
- **Package manager**: `uv` — use `uv add <package>` to add dependencies, never `pip install`
- **Linter/Formatter**: `ruff` — run `uv run ruff check --fix <path>` before committing
- **Testing**: `pytest` — run `uv run pytest`; tests live in `tests/`

## Dependency Rules

- Pin versions with `>=` lower bounds in `pyproject.toml` (e.g., `google-adk>=1.22.0`)
- Never hardcode model strings — always import from `src/common/ai_model.py`:
  ```python
  from common.ai_model import GEMINI_MODEL  # correct
  model = "gemini-3-flash-preview"          # wrong
  ```

## Agent Instruction (Prompt) Structure

Every agent `instruction` string **must** follow the 4-layer pattern in this exact order:

```
# [0] META-LAYER        — Identity, scope rejection, prompt-injection defense
# [1] OBSERVABILITY     — Mandatory <thought_process> XML before every action
# [2] FSM LOGIC         — Explicit state machine: Trigger → State → Action → Transition
# [3] TOOL CONTRACTS    — Pre/post-conditions for each tool, semantic-logic mapping
```

Refer to `docs/adk-system-infrastructure-design-guideline.md` as the canonical reference.

## Prompt Variable Syntax

| Syntax | Use | Source |
|--------|-----|--------|
| `{var?}` | Runtime injection from Python (null-safe) | External environment / session state |
| `<var>` | LLM-internal chain-of-thought variables | Model inference only |

**Never** use bare `{}` for LLM-internal variables — this causes Python string formatting errors.

## Agent File Layout

Each agent lives in its own `src/agent_<name>/` directory and must expose an `app` object:

```python
# Every agent module must have this
app = App(
    name="agent_name",
    root_agent=root_agent,
    plugins=[OtelTracingPlugin(), ...],
)
```

The `root_agent` variable is optional but conventional for `adk run` compatibility.

## Plugin Usage

Always attach observability plugins to the `App`:

```python
from common.otel_plugin import OtelTracingPlugin
from common.logging_plugin import StructuredLoggingPlugin

app = App(
    ...,
    plugins=[OtelTracingPlugin(), StructuredLoggingPlugin()],
)
```

`OtelTracingPlugin` is required for all agents. `StructuredLoggingPlugin` is recommended for agents that need correlation ID tracking.

## HTTP Clients

- Use `httpx.AsyncClient` for async tool functions (agents use async context)
- Use `httpx.Client` (sync) only in synchronous tool functions like those in `common/dummy_service_tools.py`
- Always call `response.raise_for_status()` and wrap in `try/except` returning an error string

```python
async def my_tool() -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error: {str(e)}"
```

## Testing Policy

- **Unit tests are mandatory** for all Python tool functions and plugin classes
- Tests for agent definitions (`LlmAgent`, `App`) are **not required**
- Test files go in `tests/` mirroring the `src/` structure
- Use `pytest` fixtures and mocking for HTTP calls (avoid real network calls in unit tests)

## Session State Keys

When using `output_key` or reading state in prompts, use snake_case keys and document them in the agent file:

```python
agent = LlmAgent(
    ...,
    output_key="execution_context",  # written to session state
)
# Consumed by next agent via: {execution_context} in instruction
```

## Pydantic Models

- Use `pydantic.BaseModel` for all data schemas
- Use `pydantic[email]` for email validation (`EmailStr`)
- Use `model_dump()` (not deprecated `.dict()`) for serialization
