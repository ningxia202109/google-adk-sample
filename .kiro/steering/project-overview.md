# Project Overview

This is a **Google ADK (Agent Development Kit) sample project** demonstrating how to build enterprise-grade AI agent applications. It serves as a reference implementation for multiple agent patterns.

## Repository Layout

```
google-adk-sample/
├── src/
│   ├── common/                          # Shared infrastructure (models, plugins, tools)
│   ├── agent_react_number_guesser/      # ReAct pattern demo
│   ├── agent_progressive_disclosure/    # Planner+Executor loop demo
│   ├── agent_pd_troubleshooting/        # PlanReActPlanner + AgentTool demo
│   └── agent_with_skills_register_user/ # Dynamic skills (Claude-style) demo
├── dummy_fastapi_service/               # Companion REST backend (port 6060)
├── tests/                               # Unit tests (pytest)
├── docs/                                # Design guidelines and engineering constitution
├── memory-bank/                         # Persistent project context (Memory Bank Protocol)
└── docker-compose/                      # Docker Compose for local observability stack
```

## Running the Project

```bash
# Install dependencies
uv sync

# Activate virtual environment (Linux/macOS)
. ./.venv/bin/activate

# Start all services (FastAPI + ADK web UI)
./start.sh

# Run a single agent interactively
adk run src/agent_react_number_guesser/agent.py

# Run tests
uv run pytest

# Lint and auto-fix
uv run ruff check --fix src/
```

## Service Endpoints

| Service | Port | Purpose |
|---------|------|---------|
| ADK Web UI | 8000 | Interactive agent chat interface |
| FastAPI backend | 6060 | REST API used by agents (`/users`, `/teams`, `/openapi.json`) |
| OTLP collector | 5000 | OpenTelemetry trace receiver (MLflow) |

## Environment Variables

```bash
GOOGLE_API_KEY=your_key      # Required for Gemini models
OPENROUTER_API_KEY=your_key  # Required for OpenRouter/LiteLLM models
```

## Memory Bank Protocol

`memory-bank/` is the source of truth for persistent project context. Before starting any significant task, read `activeContext.md` and `projectbrief.md`. After completing work, update `activeContext.md` and `progress.md`.

## Resolving Unknown Library Usage

If you are unsure how to use an imported library or an internal ADK class, **do not guess**. Instead:

1. Locate the library source in the virtual environment:
   - `.venv/lib/python3.12/site-packages/<package_name>/`
   - or `.venv/lib64/python3.12/site-packages/<package_name>/`
2. Read and analyze the relevant source files (class definitions, method signatures, docstrings) to understand the correct usage.
3. Only then write or suggest code based on what you found.

This applies especially to `google-adk` internals (e.g., `BasePlugin`, `BaseToolset`, `InvocationContext`, `ReadonlyContext`, `ToolContext`) where the public API may differ from assumptions.
