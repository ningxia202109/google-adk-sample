from google.adk.tools import AgentTool
from google.adk.apps.app import App
from google.adk.agents import LlmAgent
from google.adk.planners import PlanReActPlanner
from google.genai.types import GenerateContentConfig

from common.ai_model import GEMINI_MODEL
from common.dummy_service_tools import (
    retrieve_service_documentation,
    execute_api_request,
)

# Mock troubleshooting database
TROUBLESHOOTING_GUIDES = [
    {
        "symptom": "one user cannot join a team",
        "guide": """
## symptom: one user cannot join a team.
## troubleshooting steps:
1. check if the user exists
2. check if team exists
3. check if user's habits match team
""",
    }
]


def search_issue_by_symptom(symptom_description: str) -> str:
    """
    [MOCK] Performs a semantic similarity search against a Vector Database.

    In a production environment, this tool would:
    1. Convert the `symptom_description` into an embedding vector.
    2. Query a VectorDB (e.g., Pinecone, Milvus, Vertex AI Vector Search).
    3. Return the most relevant troubleshooting guides based on cosine similarity.

    Args:
        symptom_description: A natural language description of the issue.

    Returns:
        The content of the matched troubleshooting guide.
    """
    # Mock logic: Simple keyword matching simulating semantic hit
    print(f">> [VectorDB Search] Querying embedding for: '{symptom_description}'")
    for entry in TROUBLESHOOTING_GUIDES:
        if (
            entry["symptom"].lower() in symptom_description.lower()
            or symptom_description.lower() in entry["symptom"].lower()
        ):
            return entry["guide"]

    return "No relevant troubleshooting guide found in the Knowledge Base."


agent_troubleshooter = LlmAgent(
    name="agent_troubleshooter",
    model=GEMINI_MODEL,
    description="Responsible for executing the troubleshooting steps using API calls.",
    instruction="""
1. Read and understand the `troubleshooting_guide` provided by the previous agent.
2. Perform troubleshooting by following the steps in the guide.
3. Use the `execute_api_request` tool to call the necessary APIs as described in the guide.
4. Generate a comprehensive report of the troubleshooting process, including the steps taken, API responses, and the final result.
""",
    tools=[execute_api_request],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
    ),
    output_key="troubleshooting_report",
)

agent_retrieve_troubleshooting_guide = LlmAgent(
    name="agent_retrieve_troubleshooting_guide",
    model=GEMINI_MODEL,
    planner=PlanReActPlanner(),
    description="Responsible for understanding user request and retrieving relevant troubleshooting guides and API specs.",
    instruction="""
# Role
You are a Senior Expert Planner for system troubleshooting. Your goal is to create a safe, step-by-step execution plan and then use "agent_troubleshooter" to execute it.

# Critical Safety Restrictions
1. **READ-ONLY Policy**: You are strictly FORBIDDEN from generating plans that modify data.
2. **Allowed Methods**: You may only inspect the system using `GET` requests (via `execute_api_request` if needed to verify current state) or use documentation tools.
3. **Prohibited Methods**: Do NOT include `POST`, `PUT`, `DELETE`, or `PATCH` actions in your own reasoning steps. These are reserved for the executor agent.

# Workflow
1. **Analyze**: Understand the user's reported symptom.
2. **Retrieve Context**: 
   - Use `search_issue_by_symptom` to find similar past issues (simulating Vector Search).
   - Use `retrieve_service_documentation` to understand the API contracts.
3. **Plan**: Generate a detailed troubleshooting guide.
   - The plan must be executable by the "agent_troubleshooter".
   - The plan should explicitly list which API endpoints to call.
4. **Troubleshoot**: Use `agent_troubleshooter` to do troubleshooting with the troubleshooting guide you generated.

# Valid Issue Symptom
"one user cannot join a team"
""",
    tools=[
        search_issue_by_symptom,
        retrieve_service_documentation,
        AgentTool(agent=agent_troubleshooter),
    ],
    output_key="troubleshooting_guide",
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
    ),
)

root_agent = agent_retrieve_troubleshooting_guide

app = App(
    name="agent_pd_troubleshooting",
    root_agent=root_agent,
)
