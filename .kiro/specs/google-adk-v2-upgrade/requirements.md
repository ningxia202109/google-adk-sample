# Requirements Document

## Introduction

This feature upgrades the `google-adk` dependency from `>=1.22.0` to `>=2.0.0` (latest stable: `2.0.0`, released 2026-05-19). ADK 2.0 is a GA release that introduces a graph-based Workflow Runtime, a new Task API for structured agent-to-agent delegation, and several breaking changes to the agent execution model, plugin callback signatures, and event schema.

The project currently uses ADK 1.x APIs across four agent patterns (ReAct, Progressive Disclosure, PlanReActPlanner+AgentTool, Dynamic Skills) and shared infrastructure (OtelTracingPlugin, StructuredLoggingPlugin, DynamicSkillToolset). This upgrade must preserve all existing agent behaviors while migrating any incompatible API usage to ADK 2.0 equivalents.

---

## Glossary

- **ADK**: Google Agent Development Kit — the Python framework powering all agents in this project.
- **ADK_1x**: The current installed version of google-adk, pinned at `>=1.22.0`.
- **ADK_2x**: The target version of google-adk, `>=2.0.0` (latest: `2.0.0`).
- **Upgrade_Script**: The automated migration process that updates `pyproject.toml` and resolves dependency conflicts.
- **Plugin**: A class subclassing `BasePlugin` that hooks into the agent lifecycle via callback methods.
- **Toolset**: A class subclassing `BaseToolset` that dynamically provides tools to an agent at runtime.
- **InvocationContext**: The ADK context object passed to plugin callbacks, carrying invocation metadata.
- **CallbackContext**: The ADK 2.0 context object used in agent-level plugin callbacks (`before_agent_callback`, `after_agent_callback`).
- **BaseNode**: The ADK 2.0 base class that `BaseAgent` now subclasses, enabling agents to participate in the graph-based Workflow Runtime.
- **Workflow_Runtime**: The ADK 2.0 graph-based execution engine that replaces the hierarchical agent executor.
- **ContextCacheConfig**: ADK configuration object for context caching, used in `agent_react_number_guesser` and `agent_progressive_disclosure`.
- **DynamicSkillToolset**: The project's custom `BaseToolset` subclass that injects skill-specific tools based on session state.
- **OtelTracingPlugin**: The project's custom `BasePlugin` subclass for OpenTelemetry tracing.
- **StructuredLoggingPlugin**: The project's custom `BasePlugin` subclass for structured JSON logging.
- **LiteLlm**: The ADK model wrapper for LiteLLM-compatible models (e.g., OpenRouter).
- **uv**: The package manager used in this project (`uv add`, `uv sync`).

---

## ADK 2.0 New Features Summary

The following ADK 2.0 features are available for optional adoption after the upgrade:

1. **Graph-based Workflow Runtime**: Compose deterministic execution flows with routing, fan-out/fan-in, loops, retry, and human-in-the-loop support using the new `Workflow` class.
2. **Task API**: Structured agent-to-agent delegation with multi-turn task mode, single-turn controlled output, and mixed delegation patterns.
3. **Dynamic Workflows**: Code-based logic for complex iterative loops and decision-based branching.
4. **Collaborative Workflows**: Coordinator agents with multiple sub-agents working together.
5. **Automatic Retries**: The framework now automatically catches exceptions to enable retries via `RetryConfig(max_attempts=N)`.
6. **Human-in-the-Loop (HITL)**: Native pause/resume support for workflows requiring human input.
7. **New Plugin Callbacks**: Additional hooks including `on_user_message_callback`, `before_agent_callback`, `after_agent_callback`, `on_model_error_callback`, `on_tool_error_callback`, `on_event_callback`.
8. **`Agent` alias**: `LlmAgent` can now be imported as `Agent` from `google.adk`.

---

## ADK 2.0 Breaking Changes Analysis

The following breaking changes from the [official ADK 2.0 migration guide](https://adk.dev/2.0/) have been analyzed against this project's codebase:

### BC-1: BaseAgent now subclasses BaseNode
**Impact on this project**: None. The project does not subclass `BaseAgent` directly. All agents are constructed using `LlmAgent(...)` and `LoopAgent(...)` as instances, not subclasses. No custom `_run_async_impl()` overrides exist.

### BC-2: Custom `_run_async_impl()` overrides are silently bypassed
**Impact on this project**: None. No files in `src/` override `_run_async_impl()` or `generate_content()`.

### BC-3: Direct session event appending (`context.session.events.append(...)`) is unsafe
**Impact on this project**: None. The project does not manually append events to sessions.

### BC-4: Broad `except Exception:` blocks in tools mask automatic retry
**Impact on this project**: Moderate. All tool functions in `src/common/dummy_service_tools.py` and `src/agent_with_skills_register_user/tools.py` use `except Exception as e: return f"Error: {str(e)}"`. This pattern prevents ADK 2.0's automatic retry from triggering. The project must decide whether to adopt retry behavior or preserve the current error-string return pattern.

### BC-5: Catching `BaseException` traps `NodeInterruptedError`
**Impact on this project**: None. No tool functions catch `BaseException`.

### BC-6: Event schema adds `node_info` and `output` fields
**Impact on this project**: None. The project uses `InMemorySessionService` (not a custom session database with rigid columns). No downstream JSON schema validators with `additionalProperties: false` are present.

### BC-7: Plugin callback signature changes
**Impact on this project**: Requires investigation. ADK 2.0 docs show that `before_run_callback` and `after_run_callback` on `BasePlugin` retain the same `invocation_context: InvocationContext` signature. However, the new agent-level callbacks (`before_agent_callback`, `after_agent_callback`) use `CallbackContext` instead of `InvocationContext`. The project's plugins use `before_run_callback` and `after_run_callback`, which appear compatible. Verification against the installed ADK 2.0 source is required.

---

## Requirements

### Requirement 1: Dependency Version Upgrade

**User Story:** As a developer, I want to upgrade `google-adk` to version `2.0.0`, so that the project benefits from the new Workflow Runtime, Task API, and security fixes included in ADK 2.0.

#### Acceptance Criteria

1. THE `pyproject.toml` SHALL specify `google-adk>=2.0.0` as the lower bound for the `google-adk` dependency.
2. WHEN `uv sync` is executed after updating `pyproject.toml`, THE `Upgrade_Script` SHALL resolve all transitive dependencies without version conflicts.
3. WHEN `python -c "import google.adk; print(google.adk.__version__)"` is executed in the project virtual environment, THE output SHALL begin with `2.`.
4. THE `uv.lock` file SHALL be regenerated to reflect the ADK_2x dependency resolution.

---

### Requirement 2: Plugin Callback Compatibility

**User Story:** As a developer, I want the `OtelTracingPlugin` and `StructuredLoggingPlugin` to work correctly under ADK 2.0, so that observability and structured logging continue to function without modification.

#### Acceptance Criteria

1. WHEN `OtelTracingPlugin` is instantiated and its `before_run_callback` is invoked with a mock `InvocationContext`, THE `OtelTracingPlugin` SHALL execute without raising an `AttributeError` or `TypeError`.
2. WHEN `OtelTracingPlugin.after_run_callback` is invoked, THE `OtelTracingPlugin` SHALL call `provider.force_flush()` without error.
3. WHEN `StructuredLoggingPlugin.before_run_callback` is invoked with a mock `InvocationContext` containing `invocation_id` and `agent.name`, THE `StructuredLoggingPlugin` SHALL bind `correlation_id` to the structlog context and log `agent_run_started`.
4. WHEN `StructuredLoggingPlugin.after_run_callback` is invoked, THE `StructuredLoggingPlugin` SHALL log `agent_run_completed` and clear structlog context variables.
5. IF the `InvocationContext` passed to `StructuredLoggingPlugin.before_run_callback` does not have an `invocation_id` attribute, THEN THE `StructuredLoggingPlugin` SHALL use `"unknown"` as the `correlation_id` without raising an exception.
6. WHERE the ADK_2x `BasePlugin` interface changes the signature of `before_run_callback` or `after_run_callback`, THE `OtelTracingPlugin` and `StructuredLoggingPlugin` SHALL be updated to match the new signature before the upgrade is considered complete.

---

### Requirement 3: DynamicSkillToolset Compatibility

**User Story:** As a developer, I want the `DynamicSkillToolset` to work correctly under ADK 2.0, so that the Dynamic Skills agent pattern continues to inject skill-specific tools based on session state.

#### Acceptance Criteria

1. WHEN `DynamicSkillToolset.get_tools` is called with a `ReadonlyContext` where `state["active_skill"]` is `None`, THE `DynamicSkillToolset` SHALL return exactly the three base tools: `search_skills`, `load_skill`, and `complete_skill`.
2. WHEN `DynamicSkillToolset.get_tools` is called with a `ReadonlyContext` where `state["active_skill"]` is a valid skill name, THE `DynamicSkillToolset` SHALL return the three base tools plus the tools listed in that skill's frontmatter.
3. WHERE the ADK_2x `BaseToolset` interface changes the signature of `get_tools`, THE `DynamicSkillToolset` SHALL be updated to match the new signature.
4. WHEN `DynamicSkillToolset` is registered as a tool in `LlmAgent`, THE agent SHALL be constructable without raising an `ImportError` or `TypeError` under ADK_2x.

---

### Requirement 4: ContextCacheConfig Compatibility

**User Story:** As a developer, I want `ContextCacheConfig` to remain functional under ADK 2.0, so that context caching continues to work in `agent_react_number_guesser` and `agent_progressive_disclosure`.

#### Acceptance Criteria

1. WHEN `from google.adk.agents.context_cache_config import ContextCacheConfig` is executed under ADK_2x, THE import SHALL succeed without raising an `ImportError`.
2. WHEN `ContextCacheConfig(min_tokens=4096, ttl_seconds=600, cache_intervals=3)` is instantiated under ADK_2x, THE `ContextCacheConfig` SHALL be constructable without raising a `TypeError`.
3. WHERE the ADK_2x `ContextCacheConfig` constructor signature changes, THE `agent_react_number_guesser` and `agent_progressive_disclosure` agent files SHALL be updated to use the new constructor parameters.

---

### Requirement 5: LiteLlm Model Integration Compatibility

**User Story:** As a developer, I want the `LiteLlm` model wrapper to remain importable and functional under ADK 2.0, so that OpenRouter-based models continue to work.

#### Acceptance Criteria

1. WHEN `from google.adk.models.lite_llm import LiteLlm` is executed under ADK_2x, THE import SHALL succeed without raising an `ImportError`.
2. WHEN `LiteLlm(model="openrouter/xiaomi/mimo-v2-flash", api_key=..., api_base=...)` is instantiated under ADK_2x, THE `LiteLlm` SHALL be constructable without raising a `TypeError`.
3. WHERE the ADK_2x `LiteLlm` import path changes, THE `src/common/ai_model.py` file SHALL be updated to use the new import path.

---

### Requirement 6: Tool Exception Handling Review

**User Story:** As a developer, I want to review and update tool exception handling patterns to be compatible with ADK 2.0's automatic retry mechanism, so that the project can optionally benefit from retry behavior without breaking existing error-string return contracts.

#### Acceptance Criteria

1. THE project SHALL document the decision on whether to adopt ADK 2.0 automatic retry (`RetryConfig`) or preserve the current `except Exception as e: return f"Error: {str(e)}"` pattern for each tool function.
2. IF the decision is to preserve the current error-string return pattern, THEN THE tool functions in `src/common/dummy_service_tools.py` and `src/agent_with_skills_register_user/tools.py` SHALL retain their existing `try/except` blocks unchanged.
3. IF the decision is to adopt ADK 2.0 automatic retry, THEN THE tool functions SHALL allow `httpx.HTTPStatusError` and `httpx.ConnectError` to propagate, and THE `App` objects SHALL be configured with an appropriate `RetryConfig`.
4. THE tool functions SHALL NOT catch `BaseException` under any circumstances, as this would trap `NodeInterruptedError` and break ADK 2.0 Human-in-the-Loop support.

---

### Requirement 7: Test Suite Validation

**User Story:** As a developer, I want all existing unit tests to pass after the ADK 2.0 upgrade, so that I have confidence the migration has not introduced regressions.

#### Acceptance Criteria

1. WHEN `uv run pytest` is executed after the upgrade, THE test suite SHALL report zero failures and zero errors.
2. THE `tests/common/test_logging_plugin.py` tests SHALL pass, verifying that `StructuredLoggingPlugin.before_run_callback` and `after_run_callback` behave correctly under ADK_2x.
3. THE `tests/test_agent_with_skills_registry.py` tests SHALL pass, verifying that `SkillRegistry` loading, searching, and retrieval are unaffected by the ADK upgrade (this module has no ADK dependency).
4. WHERE existing tests mock `InvocationContext` from `google.adk.agents.invocation_context`, THE mocks SHALL remain valid under ADK_2x or be updated to reflect any interface changes.

---

### Requirement 8: Import Path Verification

**User Story:** As a developer, I want all ADK import paths used in the project to remain valid under ADK 2.0, so that no `ImportError` occurs at module load time.

#### Acceptance Criteria

1. THE following import paths SHALL be verified as valid under ADK_2x and updated if they have changed:
   - `from google.adk.apps.app import App`
   - `from google.adk.agents import LlmAgent, LoopAgent`
   - `from google.adk.agents.readonly_context import ReadonlyContext`
   - `from google.adk.agents.invocation_context import InvocationContext`
   - `from google.adk.agents.context_cache_config import ContextCacheConfig`
   - `from google.adk.plugins.base_plugin import BasePlugin`
   - `from google.adk.tools import FunctionTool, BaseTool`
   - `from google.adk.tools.base_toolset import BaseToolset`
   - `from google.adk.tools import AgentTool`
   - `from google.adk.planners import PlanReActPlanner`
   - `from google.adk.models.lite_llm import LiteLlm`
2. WHEN each agent module (`agent_react_number_guesser`, `agent_progressive_disclosure`, `agent_pd_troubleshooting`, `agent_with_skills_register_user`) is imported under ADK_2x, THE import SHALL succeed without raising an `ImportError`.
3. WHERE an import path has changed in ADK_2x, THE affected source files SHALL be updated to use the new path before the upgrade is considered complete.

---

### Requirement 9: Dependency Version Pinning

**User Story:** As a developer, I want the upgraded dependency to be pinned with a clear lower bound, so that the project does not accidentally regress to ADK 1.x in future dependency resolutions.

#### Acceptance Criteria

1. THE `pyproject.toml` SHALL specify `google-adk>=2.0.0` using the `>=` lower-bound convention consistent with the project's existing dependency pinning style.
2. THE `pyproject.toml` SHALL NOT use an upper bound (e.g., `<3.0.0`) unless a specific incompatibility with a future ADK version is identified during the upgrade.
3. THE `pyproject.toml` SHALL NOT use the compatible release operator (`~=2.0.0`) as this would prevent minor version upgrades within the 2.x series.
4. WHEN `uv add "google-adk>=2.0.0"` is executed, THE `uv.lock` file SHALL be updated to pin the resolved version of `google-adk` to `2.0.0` or higher.
