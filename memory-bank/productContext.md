# Product Context

This project serves as a reference implementation for building AI agents that move beyond "creative writing" and into rigorous software engineering.

## Why this project exists
The AI agent space is often dominated by proof-of-concepts that lack robustness. This project provides a sample of how to use Google ADK to build agents that are maintainable, observable, and reliable.

## Problems it solves
- **Complexity Management**: Uses "Progressive Disclosure" to prevent LLM context saturation.
- **Reliability**: Employs "Defensive Design" and "Tool Contracts".
- **Observability**: Integrates OpenTelemetry for tracing agent thought processes and actions.
- **Architectural Rigor**: Follows a 4-layer architecture (Meta-governance, Observability, Logic, Tool Contracts).

## How it works
- Agents are built using the Google ADK framework.
- They interact with a companion FastAPI service to simulate real-world API interactions.
- Traces are exported via OpenTelemetry for debugging and monitoring.
- Explicit state machine transitions (FSM-based logic) are used for complex flows.
