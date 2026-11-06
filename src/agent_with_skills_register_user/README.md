# Agent with Dynamic Skills (Claude-style PoC)

This agent demonstrates a Proof of Concept (PoC) for implementing dynamic, markdown-driven "Skills" within the Google Agent Development Kit (ADK), inspired by Claude's agent skills.

## Architecture Overview

The system allows an agent to discover, load, and off-load specialized capabilities (instructions and tools) at runtime without modifying the agent's core code.

### Core Components

1.  **Agent Skill Registry (`agent_skill_registry.py`)**: 
    -   Indexes markdown files in the `skills/` directory.
    -   Parses YAML frontmatter for metadata (name, description, required tools).
    -   Implements a **Hybrid Search** using BM25 (Best Matching 25) ranking and substring matching for robust skill discovery.

2.  **Agent Tool Registry (`agent_tool_registry.py`)**:
    -   Provides a central repository for all available Python tool functions.
    -   Uses a decorator pattern (`@tool_registry.register_tool`) for easy registration of service-specific tools.

3.  **Dynamic Skill Toolset (`tools.py`)**:
    -   A custom implementation of ADK's `BaseToolset`.
    -   Intercepts the tool resolution process at runtime.
    -   Checks the ADK session state for an `active_skill` and dynamically injects the tools requested by that skill from the tool registry.

4.  **Dynamic Instruction Provider (`agent.py`)**:
    -   Uses ADK's `InstructionProvider` (callable instruction) feature.
    -   If a skill is active, it fetches the markdown content from the registry and appends it to the base system instructions.

## Skill Lifecycle

### 1. Register
-   **Tools**: Decorated with `@tool_registry.register_tool` in `tools.py`.
-   **Skills**: Created as `.md` files in the `skills/` folder following the `Agent Skill Format`.

### 2. Load
-   The agent uses the `search_skills` tool to find a relevant skill based on user intent.
-   The agent calls `load_skill(skill_name=...)`, which sets `active_skill` in the **ADK Session State**.
-   On the next turn:
    -   The `InstructionProvider` injects the skill's guidance into the prompt.
    -   The `DynamicSkillToolset` makes the specialized API tools available.

### 3. Off-load
-   Once the task is complete, the agent calls `complete_skill()`.
-   The `active_skill` is set to `None` in the session state.
-   The agent returns to its base state with only the **permanent basic tools** available.

## ADK Features Used

-   **`LlmAgent` with Callable `instruction`**: Enables runtime prompt engineering.
-   **`BaseToolset` & `DynamicSkillToolset`**: Custom implementation of `get_tools` that allows context-aware tool injection based on the current session state. This agent includes **permanent basic tools** (`search_skills`, `load_skill`, `complete_skill`) that are always available and never off-loaded.
-   **Session State (`ctx.state`)**: Used as the source of truth for the active capability.
-   **ReAct Pattern**: The agent reasons about which skill to load and when to off-load it.

## How to Run

1.  Ensure the dummy service is running (if applicable).
2.  Run the agent using the ADK CLI:
    ```bash
    PYTHONPATH=src uv run adk run src/agent_with_skills_register_user/agent.py
    ```
3.  Example Query: *"I want to register a new user named Bob with email bob@example.com, his habit is swim"*

## Skill Format Example

```markdown
---
name: register user
description: Specialized skill for registering and managing users.
tools: get_users, create_user, update_user
---
# Register User Skill
[Specialized instructions and guidance...]
```
