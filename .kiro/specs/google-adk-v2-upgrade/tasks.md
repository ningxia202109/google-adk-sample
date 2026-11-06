# Implementation Plan: google-adk v2 Upgrade

## Overview

Upgrade `google-adk` from `>=1.22.0` to `>=2.0.0` by bumping the version constraint, syncing dependencies, verifying all import paths and API compatibility, and adding a dedicated compatibility test suite. The upgrade is low-risk — no application code changes are expected, but all compatibility points must be verified and tested before the upgrade is considered complete.

## Tasks

- [x] 1. Bump dependency version and sync
  - [x] 1.1 Update `pyproject.toml` and regenerate `uv.lock`
    - In `pyproject.toml`, change `"google-adk>=1.22.0"` to `"google-adk>=2.0.0"` in the `dependencies` list
    - Run `uv add "google-adk>=2.0.0"` to apply the change and regenerate `uv.lock`
    - Confirm the installed version by running `python -c "import google.adk; print(google.adk.__version__)"` — output must start with `2.`
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 9.1, 9.2, 9.3, 9.4_

- [x] 2. Verify ADK import paths under ADK 2.0
  - [x] 2.1 Verify all 11 ADK import paths resolve without `ImportError`
    - Attempt each of the following imports in the project virtual environment and confirm no `ImportError` is raised:
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
    - If any path raises `ImportError`, update the affected source file(s) in `src/` to use the new ADK 2.0 path before proceeding
    - _Requirements: 8.1, 8.2, 8.3_

- [x] 3. Verify plugin callback compatibility
  - [x] 3.1 Confirm `OtelTracingPlugin` and `StructuredLoggingPlugin` callback signatures are compatible with ADK 2.0
    - Inspect the installed ADK 2.0 `BasePlugin` source at `.venv/lib/python3.11/site-packages/google/adk/plugins/base_plugin.py` and confirm `before_run_callback` and `after_run_callback` still accept `invocation_context: InvocationContext`
    - If the signature has changed, update `src/common/otel_plugin.py` and `src/common/logging_plugin.py` to match the new signature
    - Confirm `InvocationContext` still exposes `invocation_id` and `agent.name` attributes; update plugin attribute access if needed
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [x] 4. Verify `DynamicSkillToolset.get_tools` signature compatibility
  - [x] 4.1 Confirm `BaseToolset.get_tools` abstract method signature is unchanged in ADK 2.0
    - Inspect the installed ADK 2.0 `BaseToolset` source at `.venv/lib/python3.11/site-packages/google/adk/tools/base_toolset.py` and confirm `get_tools` still accepts `readonly_context: Optional[ReadonlyContext] = None`
    - If the signature has changed, update `DynamicSkillToolset.get_tools` in `src/agent_with_skills_register_user/tools.py` to match
    - _Requirements: 3.3, 3.4_

- [x] 5. Verify `ContextCacheConfig` and `LiteLlm` constructors
  - [x] 5.1 Confirm `ContextCacheConfig` constructor accepts existing keyword arguments
    - Inspect the installed ADK 2.0 `ContextCacheConfig` source and confirm `ContextCacheConfig(min_tokens=4096, ttl_seconds=600, cache_intervals=3)` is still valid
    - If the constructor signature has changed, update `src/agent_react_number_guesser/agent.py` and `src/agent_progressive_disclosure/agent.py` to use the new parameters
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 5.2 Confirm `LiteLlm` constructor accepts existing keyword arguments
    - Inspect the installed ADK 2.0 `LiteLlm` source and confirm `LiteLlm(model=..., api_key=..., api_base=...)` is still valid
    - If the import path or constructor signature has changed, update `src/common/ai_model.py`
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 6. Checkpoint — verify environment before writing tests
  - Ensure all source modules import cleanly: run `python -c "import sys; sys.path.insert(0, 'src'); from agent_react_number_guesser.agent import app; from agent_progressive_disclosure.agent import app; from agent_pd_troubleshooting.agent import app; from agent_with_skills_register_user.agent import app; print('OK')"` from the project root
  - Resolve any remaining `ImportError` or `TypeError` before proceeding to test creation
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Create `tests/test_adk_v2_compatibility.py`
  - [x] 7.1 Implement `test_all_adk_imports_succeed`
    - Write a test that imports all 11 ADK paths from the verification table in the design and asserts each import succeeds without raising `ImportError`
    - Use `importlib.import_module` or direct import statements inside the test body
    - _Requirements: 8.1_
  - [x] 7.2 Implement `test_context_cache_config_constructor`
    - Write a test that instantiates `ContextCacheConfig(min_tokens=4096, ttl_seconds=600, cache_intervals=3)` and asserts no `TypeError` is raised
    - _Requirements: 4.2_
  - [x] 7.3 Implement `test_litellm_constructor`
    - Write a test that instantiates `LiteLlm(model="test/model", api_key="test", api_base="https://example.com")` and asserts no `TypeError` is raised
    - _Requirements: 5.2_
  - [x] 7.4 Implement `test_otel_plugin_before_run_callback`
    - Write an async test that instantiates `OtelTracingPlugin`, creates a `MagicMock` for `InvocationContext`, and calls `before_run_callback(invocation_context=mock_ctx)`
    - Assert no `AttributeError` or `TypeError` is raised
    - _Requirements: 2.1_
  - [x] 7.5 Implement `test_otel_plugin_after_run_callback`
    - Write an async test that calls `after_run_callback(invocation_context=mock_ctx)` on an `OtelTracingPlugin` instance
    - Patch `provider.force_flush` and assert it is called exactly once
    - _Requirements: 2.2_
  - [x] 7.6 Implement `test_dynamic_skill_toolset_no_active_skill`
    - Write an async test that calls `DynamicSkillToolset().get_tools(readonly_context=mock_ctx)` where `mock_ctx.state.get("active_skill")` returns `None`
    - Assert exactly 3 tools are returned (`search_skills`, `load_skill`, `complete_skill`)
    - _Requirements: 3.1_
  - [x] 7.7 Implement `test_dynamic_skill_toolset_with_active_skill`
    - Write an async test that calls `DynamicSkillToolset().get_tools(readonly_context=mock_ctx)` where `mock_ctx.state.get("active_skill")` returns a valid skill name that exists in the registry
    - Assert more than 3 tools are returned (base 3 + skill-specific tools from the skill's frontmatter)
    - _Requirements: 3.2_

- [x] 8. Create `tests/test_pyproject_version.py`
  - [x] 8.1 Implement `test_google_adk_lower_bound_is_v2`
    - Write a test that reads `pyproject.toml` from the project root and asserts the string `"google-adk>=2.0.0"` is present in the `dependencies` list
    - _Requirements: 1.1, 9.1_
  - [x] 8.2 Implement `test_google_adk_no_upper_bound`
    - Write a test that parses `pyproject.toml` and asserts no dependency entry for `google-adk` contains a `<` or `<=` version constraint
    - _Requirements: 9.2_
  - [x] 8.3 Implement `test_google_adk_no_compatible_release_operator`
    - Write a test that parses `pyproject.toml` and asserts no dependency entry for `google-adk` uses the `~=` compatible release operator
    - _Requirements: 9.3_

- [x] 9. Final checkpoint — run full test suite
  - Run `uv run pytest` from the project root and confirm zero failures and zero errors
  - Confirm `tests/common/test_logging_plugin.py` passes (covers Requirements 2.3, 2.4, 2.5)
  - Confirm `tests/test_agent_with_skills_registry.py` passes (covers Requirement 7.3)
  - Confirm `tests/test_adk_v2_compatibility.py` passes (covers Requirements 2.1, 2.2, 3.1, 3.2, 4.2, 5.2, 8.1)
  - Confirm `tests/test_pyproject_version.py` passes (covers Requirements 1.1, 9.1, 9.2, 9.3)
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks 2–5 are verification tasks: if the ADK 2.0 API is unchanged (as the design predicts), no source edits are needed. The tasks exist to catch any unexpected breaking changes.
- The design explicitly opts out of ADK 2.0 automatic retry (`RetryConfig`). All `except Exception as e: return f"Error: {str(e)}"` blocks in tool functions are preserved unchanged (Requirement 6.2).
- No `BaseException` catches exist in the codebase — this must remain true to avoid trapping `NodeInterruptedError` (Requirement 6.4).
- Use `uv add "google-adk>=2.0.0"` (not `pip install`) to update the dependency per project conventions.
- When inspecting ADK 2.0 source, look in `.venv/lib/python3.11/site-packages/google/adk/` (adjust Python version if needed).
- `ContextCacheConfig` is marked `@experimental` in ADK — if it moves or is removed, update both `agent_react_number_guesser/agent.py` and `agent_progressive_disclosure/agent.py`.

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1.1"] },
    { "id": 1, "tasks": ["2.1"] },
    { "id": 2, "tasks": ["3.1", "4.1", "5.1", "5.2"] },
    { "id": 3, "tasks": ["7.1", "7.2", "7.3", "7.4", "7.5", "7.6", "7.7", "8.1", "8.2", "8.3"] }
  ]
}
```
