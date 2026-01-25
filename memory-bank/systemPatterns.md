# System Patterns

## 4-Layer Architecture
The project adheres to the `adk-system-infrastructure-design-guideline.md`:

1.  **L1: Meta-governance & Error Handling**: Global constraints and recovery logic.
2.  **L2: Observability & COT (Thought Traces)**: Detailed reasoning logs.
3.  **L3: FSM-based Logic**: Explicit state transitions and workflow management.
4.  **L4: Tool Contracts**: Precise definitions of how agents interact with the environment.

## Key Design Patterns

### ReAct (Reasoning + Acting)
- Used in `NumberGuesser Agent`.
- Loop: Think -> Act -> Observe -> Rethink.

### Progressive Disclosure
- Used in `Progressive Disclosure Agent` and `PD Troubleshooting Agent`.
- Pattern: Decompose task -> Disclose relevant sub-context -> Execute -> Verify.
- Benefits: Reduces LLM context window pressure and improves accuracy.

### Defensive Design
- Prompts are treated as production code.
- Variable scope isolation.
- Explicit state machine transitions.

## Directory Structure
- `src/`: Core agent implementations.
  - `common/`: Shared utilities (AI models, Otel, tools).
- `dummy_fastapi_service/`: Backend API for agent practice.
- `docs/`: Design guidelines and documentation.
- `memory-bank/`: Persistent project context.

## Technical Decisions
- **Domain-Driven Design (DDD)**: Logic organized around clear agent domains.
- **SOLID Principles**: Focused tool responsibilities and modular agent components.
- **Strict Typing**: Python type hints used throughout (checked by Ruff).
