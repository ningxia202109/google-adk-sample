from google.adk.agents import LlmAgent, LoopAgent
from common.ai_model import GEMINI_MODEL

agent_retrieve_execution_step = LlmAgent(
    name="agent_retrieve_execution_step",
    model=GEMINI_MODEL,
    description="You are a helpful assistant that retrieves relevant execution context based on user queries.",
    instruction="""

""",
    tools=[],
    output_key="execution_context",
)


agent_executer = LlmAgent(
    name="agent_executer",
    model=GEMINI_MODEL,
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
