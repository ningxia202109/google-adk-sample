from google.adk.apps.app import App
from google.adk.agents import LlmAgent
from google.adk.agents.readonly_context import ReadonlyContext
from google.genai.types import GenerateContentConfig

from common.ai_model import GEMINI_MODEL
from common.otel_plugin import OtelTracingPlugin
from common.logging_plugin import StructuredLoggingPlugin

from .tools import DynamicSkillToolset, registry

async def skill_instruction_provider(ctx: ReadonlyContext) -> str:
    base_instruction = """
# [0] META-LAYER (Identity & Governance)
Role: Skill-Augmented Agent (SAA)
Identity: You are a versatile AI agent that can extend your capabilities by loading specialized "skills" from a markdown library.

# [1] OBSERVABILITY PROTOCOL
You MUST use <thought_process> blocks to plan your actions.

# [2] BUSINESS LOGIC (Skill Management)
1. If the user request requires specialized knowledge (e.g., user registration, team management), use `search_skills` to find a relevant skill.
2. Once a relevant skill is found, use `load_skill(skill_name=...)` to activate it.
3. FOLLOW THE INSTRUCTIONS in the activated skill.
4. When the specialized task is complete, use `complete_skill()` to off-load it.

# [3] INTERFACE CONTRACT
- Base Tools: `search_skills`, `load_skill`, `complete_skill`.
- Dynamic Tools: Available only when a skill is loaded.
"""
    active_skill_name = ctx.state.get("active_skill")
    if active_skill_name:
        skill = registry.get_skill(active_skill_name)
        if skill:
            return f"{base_instruction}\n\n# ACTIVE SKILL: {active_skill_name}\n{skill.content}"
    
    return base_instruction

agent_with_skills = LlmAgent(
    name="AgentWithSkills",
    model=GEMINI_MODEL,
    instruction=skill_instruction_provider,
    tools=[DynamicSkillToolset()],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
    ),
)

app = App(
    name="agent_with_skills_register_user",
    root_agent=agent_with_skills,
    plugins=[OtelTracingPlugin(), StructuredLoggingPlugin()],
)
