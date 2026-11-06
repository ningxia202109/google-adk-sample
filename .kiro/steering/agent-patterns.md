# Agent Development Patterns

This project implements four distinct agent patterns using Google ADK. When building a new agent, pick the pattern that best fits the use case.

---

## Pattern 1: ReAct (Reasoning + Acting)

**When to use**: Single-agent tasks requiring iterative tool use with self-correction.

**Reference**: `src/agent_react_number_guesser/`

**Structure**:
```python
agent = LlmAgent(
    name="MyReActAgent",
    model=GEMINI_MODEL,
    instruction="...",  # Must include FSM with IDLE / ACTIVE states
    tools=[my_tool],
    generate_content_config=GenerateContentConfig(temperature=0.0),
)
app = App(name="...", root_agent=agent, plugins=[OtelTracingPlugin()])
```

**Key characteristics**:
- Single `LlmAgent` with one or more tools
- Instruction encodes the full FSM: state transitions driven by tool output keywords
- `temperature=0.0` for deterministic reasoning
- `ContextCacheConfig` recommended for long iterative sessions

**FSM template**:
```
STATE: [IDLE]       → wait for trigger
STATE: [ACTIVE]     → parse history → validate bounds → execute tool → loop
STATE: [COMPLETE]   → celebrate → transition to IDLE
```

---

## Pattern 2: Progressive Disclosure (Planner + Executor Loop)

**When to use**: Multi-step tasks against an external API where each step depends on the previous result.

**Reference**: `src/agent_progressive_disclosure/`

**Structure**:
```python
planner = LlmAgent(
    name="agent_planner",
    tools=[retrieve_service_documentation],
    output_key="execution_context",   # writes plan to session state
)
executor = LlmAgent(
    name="agent_executor",
    include_contents="none",          # stateless — only reads execution_context
    instruction="...\n<execution_context>\n{execution_context}\n</execution_context>",
    tools=[execute_api_request],
    output_key="execution_result",
)
root = LoopAgent(
    name="root",
    sub_agents=[planner, executor],
    max_iterations=5,
)
```

**Key characteristics**:
- Planner owns API documentation retrieval; executor owns API execution
- `include_contents="none"` on executor prevents context pollution
- Session state (`output_key` / `{var?}`) is the only communication channel between agents
- Planner validates executor output before proceeding to next step
- Set `max_iterations` conservatively to prevent runaway loops

**Data flow**:
```
User → Planner(docs) → execution_context → Executor(api call) → execution_result → Planner(validate) → ...
```

---

## Pattern 3: PlanReActPlanner + AgentTool (Hierarchical)

**When to use**: Complex workflows where a strategic planner must delegate isolated execution to a sub-agent, with strict read/write separation.

**Reference**: `src/agent_pd_troubleshooting/`

**Structure**:
```python
executor = LlmAgent(
    name="executor",
    include_contents="none",
    tools=[execute_api_request],
    output_key="execution_report",
)
planner = LlmAgent(
    name="planner",
    planner=PlanReActPlanner(),       # structured plan-then-act reasoning
    tools=[
        search_knowledge_base,
        retrieve_service_documentation,
        AgentTool(agent=executor),    # executor wrapped as a tool
    ],
)
```

**Key characteristics**:
- `PlanReActPlanner` forces the planner to produce an explicit plan before acting
- `AgentTool` wraps the executor agent as a callable tool — planner sees it as a black box
- Planner is READ-ONLY by policy (only GET requests); executor handles mutations
- Executor uses `include_contents="none"` + `temperature=0.0` for deterministic, isolated runs
- Mock knowledge base (`search_issue_by_symptom`) simulates VectorDB semantic search

**Safety rule**: Enforce in the planner's instruction:
```
READ-ONLY Policy: FORBIDDEN from POST/PUT/DELETE. Only GET is allowed in planner steps.
```

---

## Pattern 4: Dynamic Skills (Claude-style Skill Loading)

**When to use**: A single agent needs to handle diverse task domains without loading all tools/context upfront.

**Reference**: `src/agent_with_skills_register_user/`

**Core components**:

| Component | Class | Responsibility |
|-----------|-------|----------------|
| Skill files | `skills/*.md` | Markdown with frontmatter (`name`, `description`, `tools`) + natural language guidance |
| Skill registry | `SkillRegistry` | Parses skill files, builds BM25 index, exposes `search_skills()` / `get_skill()` |
| Tool registry | `ToolRegistry` | Decorator-based registration (`@tool_registry.register_tool`), resolves tools by name |
| Dynamic toolset | `DynamicSkillToolset(BaseToolset)` | Returns base tools + skill-specific tools based on `session.state["active_skill"]` |
| Instruction provider | `async def skill_instruction_provider(ctx)` | Injects active skill markdown content into the prompt at runtime |

**Skill file format** (`skills/my_skill.md`):
```markdown
---
name: my skill name
description: One-line description used for BM25 search indexing.
tools: tool_func_a, tool_func_b
---

# My Skill
Natural language guidance for the agent...

## Guidance
Step-by-step instructions...

## guardrails
- Safety constraints...
```

**Skill lifecycle**:
```
search_skills(query) → load_skill(name) → state["active_skill"] = name
    → DynamicSkillToolset injects tools
    → skill_instruction_provider injects skill content into prompt
    → agent executes task
    → complete_skill() → state["active_skill"] = None
```

**Adding a new skill**:
1. Create `skills/skill_<name>.md` with valid frontmatter
2. Implement tool functions in `tools.py` and decorate with `@tool_registry.register_tool`
3. List the tool function names in the skill's `tools:` frontmatter field
4. No code changes needed — `SkillRegistry.refresh()` picks up new files automatically

---

## Choosing a Pattern

```
Is the task a single iterative loop with one tool?
  └─ YES → Pattern 1: ReAct

Does the task require multiple sequential API calls with validation between steps?
  └─ YES → Pattern 2: Progressive Disclosure (LoopAgent)

Does the task require strategic planning with isolated, safe execution?
  └─ YES → Pattern 3: PlanReActPlanner + AgentTool

Does the agent need to handle many different task domains dynamically?
  └─ YES → Pattern 4: Dynamic Skills
```

---

## Common ADK Extension Points

| Extension Point | Class to Subclass | Use Case |
|----------------|-------------------|----------|
| Plugin | `BasePlugin` | Cross-cutting concerns (logging, tracing) via `before_run_callback` / `after_run_callback` |
| Toolset | `BaseToolset` | Dynamic tool injection based on runtime state |
| Instruction Provider | `async def fn(ctx: ReadonlyContext) -> str` | Context-aware prompt augmentation |
| Planner | `PlanReActPlanner` | Structured plan-before-act reasoning for complex agents |
| Agent as Tool | `AgentTool(agent=...)` | Encapsulate a sub-agent as a callable tool |
