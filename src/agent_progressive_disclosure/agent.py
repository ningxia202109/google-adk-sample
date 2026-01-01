from google.adk.apps.app import App
from google.adk.agents import LlmAgent, LoopAgent
from google.genai.types import GenerateContentConfig
from google.adk.agents.context_cache_config import ContextCacheConfig

from common.ai_model import GEMINI_MODEL
from common.dummy_service_tools import (
    retrieve_service_documentation,
    execute_api_request,
)
from opentelemetry import trace
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from common.otel_config import provider, exporter

# Use BatchSpanProcessor for production-like environments (e.g., web server)
# to ensure spans are exported in the background without blocking.
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)


agent_planner = LlmAgent(
    name="agent_planner",
    model=GEMINI_MODEL,
    description="You are a planning and validation agent that manages task decomposition and verification.",
    instruction="""
1. **Analyze Goal**: Read the user's question and detect the overall goal.
2. **Review History & Validate**: Examine the previous interaction history. 
   - If a sub-task was just performed by the executor, validate the result. Does it indicate success? Does it provide the data needed for the next step?
   - If a result is an error or unexpected, plan a corrective sub-task or explain the issue.
3. **Determine Next Step**: Based on the validation, determine the NEXT single sub-task. If the overall goal is met and validated, provide a final response to the user.
4. **Retrieve Documentation**: Use the `retrieve_service_documentation` tool to fetch the API specs. This is your ONLY tool.
5. **DO NOT** attempt to call any other functions or API endpoints directly. 
6. **Progressive Disclosure**: Identify ONLY the relevant API endpoint and its parameters for the CURRENT sub-task.
7. **Execution Context**: Output ONLY the current sub-task description and that specific API specification in the `execution_context`.
8. **Final Validation**: Before finishing the entire task, ensure the final state has been verified (e.g., if a user was added, the response confirms they are now in the group).
""",
    tools=[retrieve_service_documentation],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        top_p=0.95,
    ),
    output_key="execution_context",
)


agent_executor = LlmAgent(
    name="agent_executor",
    model=GEMINI_MODEL,
    include_contents="none",
    description="You are an execution agent that performs a single API call based on a provided plan.",
    instruction="""
1. Read the `execution_context` provided by the planner, which contains a single sub-task and its API spec.
2. Use the `execute_api_request` tool to perform the exact API request described in the `execution_context`.
3. Report the raw result of the API call in `execution_result`.
4. Do not attempt to perform subsequent tasks; focus only on the one provided. Control will return to the planner for the next step.

<execution_context>
{execution_context}
</execution_context>
""",
    tools=[execute_api_request],
    output_key="execution_result",
)

agent_progressive_disclosure = LoopAgent(
    name="agent_progressive_disclosure",
    sub_agents=[agent_planner, agent_executor],
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
