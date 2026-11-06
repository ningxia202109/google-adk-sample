"""Compatibility checks for the google-adk 2.x upgrade.

Covers the ADK import paths, constructor signatures and callback/toolset
contracts that this project depends on.
"""

import asyncio
import importlib
from unittest.mock import MagicMock, patch

ADK_IMPORTS = [
    ("google.adk.apps.app", "App"),
    ("google.adk.agents", "LlmAgent"),
    ("google.adk.agents", "LoopAgent"),
    ("google.adk.agents.readonly_context", "ReadonlyContext"),
    ("google.adk.agents.invocation_context", "InvocationContext"),
    ("google.adk.agents.context_cache_config", "ContextCacheConfig"),
    ("google.adk.plugins.base_plugin", "BasePlugin"),
    ("google.adk.tools", "FunctionTool"),
    ("google.adk.tools", "BaseTool"),
    ("google.adk.tools.base_toolset", "BaseToolset"),
    ("google.adk.tools", "AgentTool"),
    ("google.adk.planners", "PlanReActPlanner"),
    ("google.adk.models.lite_llm", "LiteLlm"),
]


def test_all_adk_imports_succeed():
    for module_path, name in ADK_IMPORTS:
        module = importlib.import_module(module_path)
        assert hasattr(module, name), f"{module_path} has no attribute {name}"


def test_context_cache_config_constructor():
    from google.adk.agents.context_cache_config import ContextCacheConfig

    ContextCacheConfig(min_tokens=4096, ttl_seconds=600, cache_intervals=3)


def test_litellm_constructor():
    from google.adk.models.lite_llm import LiteLlm

    LiteLlm(model="test/model", api_key="test", api_base="https://example.com")


def test_otel_plugin_before_run_callback():
    from src.common.otel_plugin import OtelTracingPlugin

    plugin = OtelTracingPlugin()
    mock_ctx = MagicMock()
    result = asyncio.run(plugin.before_run_callback(invocation_context=mock_ctx))
    assert result is None


def test_otel_plugin_after_run_callback():
    from src.common.otel_plugin import OtelTracingPlugin

    plugin = OtelTracingPlugin()
    mock_ctx = MagicMock()
    with patch("src.common.otel_plugin.provider.force_flush") as mock_flush:
        asyncio.run(plugin.after_run_callback(invocation_context=mock_ctx))
    mock_flush.assert_called_once()


def test_dynamic_skill_toolset_no_active_skill():
    from agent_with_skills_register_user.tools import DynamicSkillToolset

    mock_ctx = MagicMock()
    mock_ctx.state.get.return_value = None
    tools = asyncio.run(DynamicSkillToolset().get_tools(readonly_context=mock_ctx))
    assert len(tools) == 3
    assert {t.name for t in tools} == {"search_skills", "load_skill", "complete_skill"}


def test_dynamic_skill_toolset_with_active_skill():
    from agent_with_skills_register_user.tools import DynamicSkillToolset, registry

    skill_name = next(
        name for name, skill in registry.skills.items() if skill.metadata.tools
    )
    mock_ctx = MagicMock()
    mock_ctx.state.get.side_effect = lambda key, default=None: (
        skill_name if key == "active_skill" else default
    )
    tools = asyncio.run(DynamicSkillToolset().get_tools(readonly_context=mock_ctx))
    assert len(tools) > 3
