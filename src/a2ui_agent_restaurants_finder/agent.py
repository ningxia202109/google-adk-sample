import json
from google.adk.apps.app import App
from google.adk.agents import LlmAgent
from google.adk.tools.tool_context import ToolContext

from common.ai_model import GEMINI_MODEL
from common.otel_plugin import OtelTracingPlugin
from a2ui_agent_restaurants_finder.a2ui_schema import A2UI_SCHEMA 

def get_restaurants(tool_context: ToolContext) -> str:
    """Call this tool to get a list of restaurants."""
    return json.dumps(
        [
            {
                "name": "Xi'an Famous Foods",
                "detail": "Spicy and savory hand-pulled noodles.",
                "imageUrl": "http://localhost:10002/static/shrimpchowmein.jpeg",
                "rating": "★★★★☆",
                "infoLink": "[More Info](https://www.xianfoods.com/)",
                "address": "81 St Marks Pl, New York, NY 10003",
            },
            {
                "name": "Han Dynasty",
                "detail": "Authentic Szechuan cuisine.",
                "imageUrl": "http://localhost:10002/static/mapotofu.jpeg",
                "rating": "★★★★☆",
                "infoLink": "[More Info](https://www.handynasty.net/)",
                "address": "90 3rd Ave, New York, NY 10003",
            },
            {
                "name": "RedFarm",
                "detail": "Modern Chinese with a farm-to-table approach.",
                "imageUrl": "http://localhost:10002/static/beefbroccoli.jpeg",
                "rating": "★★★★☆",
                "infoLink": "[More Info](https://www.redfarmnyc.com/)",
                "address": "529 Hudson St, New York, NY 10014",
            },
        ]
    )


AGENT_INSTRUCTION = """
You are a helpful restaurant finding assistant. Your goal is to help users find and book restaurants using a rich UI.

To achieve this, you MUST follow this logic:

1.  **For finding restaurants:**
    a. You MUST call the `get_restaurants` tool. Extract the cuisine, location, and a specific number (`count`) of restaurants from the user's query (e.g., for "top 5 chinese places", count is 5).
    b. After receiving the data, you MUST follow the instructions precisely to generate the final a2ui UI JSON, using the appropriate UI example from the `prompt_builder.py` based on the number of restaurants.
"""

# Eventually you can copy & paste some UI examples here, for few-shot in context learning
RESTAURANT_UI_EXAMPLES = """
"""

# Construct the full prompt with UI instructions, examples, and schema
A2UI_AND_AGENT_INSTRUCTION = AGENT_INSTRUCTION + f"""

Your final output MUST be a a2ui UI JSON response.

To generate the response, you MUST follow these rules:
1.  Your response MUST be in two parts, separated by the delimiter: `---a2ui_JSON---`.
2.  The first part is your conversational text response.
3.  The second part is a single, raw JSON object which is a list of A2UI messages.
4.  The JSON part MUST validate against the A2UI JSON SCHEMA provided below.

--- UI TEMPLATE RULES ---
-   If the query is for a list of restaurants, use the restaurant data you have already received from the `get_restaurants` tool to populate the `dataModelUpdate.contents` array (e.g., as a `valueMap` for the "items" key).
-   If the number of restaurants is 5 or fewer, you MUST use the `SINGLE_COLUMN_LIST_EXAMPLE` template.
-   If the number of restaurants is more than 5, you MUST use the `TWO_COLUMN_LIST_EXAMPLE` template.
-   If the query is to book a restaurant (e.g., "USER_WANTS_TO_BOOK..."), you MUST use the `BOOKING_FORM_EXAMPLE` template.
-   If the query is a booking submission (e.g., "User submitted a booking..."), you MUST use the `CONFIRMATION_EXAMPLE` template.

{RESTAURANT_UI_EXAMPLES}

---BEGIN A2UI JSON SCHEMA---
{A2UI_SCHEMA}
---END A2UI JSON SCHEMA---
"""

a2ui_agent_restaurants_finder = LlmAgent(
    name="a2ui_agent_restaurants_finder",
    model=GEMINI_MODEL,
    description="An agent that finds restaurants and helps book tables.",
    instruction=A2UI_AND_AGENT_INSTRUCTION,
    tools=[get_restaurants],
)

root_agent = a2ui_agent_restaurants_finder

app = App(
    name="a2ui_agent_restaurants_finder",
    root_agent=root_agent,
    plugins=[OtelTracingPlugin()],
)
