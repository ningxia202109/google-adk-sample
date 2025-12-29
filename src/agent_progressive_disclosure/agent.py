from google.adk.apps.app import App
from google.adk.agents import LlmAgent, LoopAgent
from google.genai.types import GenerateContentConfig
from google.adk.agents.context_cache_config import ContextCacheConfig

from common.ai_model import GEMINI_MODEL

agent_retrieve_execution_step = LlmAgent(
    name="agent_retrieve_execution_step",
    model=GEMINI_MODEL,
    description="You are a helpful assistant that retrieves relevant execution context based on user queries.",
    instruction="",
    # tools=[],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        top_p=0.95,
    ),
    output_key="execution_context",
)


agent_executer = LlmAgent(
    name="agent_executer",
    model=GEMINI_MODEL,
    include_contents="none",
    description="You are a helpful assistant that executes tasks based on the execution context.",
    instruction="""
Given the execution context, perform the necessary actions to complete the task.
<execution_context>
{execution_context}
</execution_context>
Provide a detailed response based on the execution context.
""",
    tools=[],
)

agent_progressive_disclosure = LoopAgent(
    name="agent_progressive_disclosure",
    sub_agents=[agent_retrieve_execution_step, agent_executer],
    max_iterations=3,
)

root_agent = agent_progressive_disclosure

app = App(
    name="agent_progressive_disclosure",
    root_agent=agent_progressive_disclosure,
    context_cache_config=ContextCacheConfig(
        min_tokens=4096,
        ttl_seconds=600,  # 10 mins for research sessions
        cache_intervals=3,  # Maximum invocations before cache refresh
    ),
)
