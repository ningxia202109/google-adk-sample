from google.adk import Agent
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
    Searches the troubleshooting library for a guide matching the symptom description.

    Args:
        symptom_description: A description of the issue or symptom.

    Returns:
        The troubleshooting guide if a match is found, or a message indicating no guide was found.
    """
    # Mock similarity search
    for entry in TROUBLESHOOTING_GUIDES:
        if (
            entry["symptom"].lower() in symptom_description.lower()
            or symptom_description.lower() in entry["symptom"].lower()
        ):
            return entry["guide"]

    return "No relevant troubleshooting guide found in the library."


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

agent_retrieve_troubleshooting_guide = Agent(
    name="agent_retrieve_troubleshooting_guide",
    model=GEMINI_MODEL,
    planner=PlanReActPlanner(),
    description="Responsible for understanding user request and retrieving relevant troubleshooting guides and API specs.",
    instruction="""
# Instructions
1. Understand the user's troubleshooting request.
2. find "Valid Issue Symptom" for the user's issue.
3. Search for a relevant troubleshooting guide using the `search_issue_by_symptom` tool based on "Valid Issue Symptom".
4. Retrieve the `dummy-fastapi-service` API specification using the `retrieve_service_documentation` tool.
5. Based on the user's issue, the retrieved troubleshooting guide, and the API specification, generate a tailored troubleshooting plan.
6. Use the `agent_troubleshooter` tool to execute the troubleshooting plan.

# Valid Issue Symptom
"one user cannot join a team"

""",
    tools=[
        search_issue_by_symptom,
        retrieve_service_documentation,
        AgentTool(agent=agent_troubleshooter),
    ],
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
    ),
)

root_agent = agent_retrieve_troubleshooting_guide

app = App(
    name="agent_pd_troubleshooting",
    root_agent=root_agent,
)
