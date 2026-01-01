from google.adk.apps.app import App
from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from google.adk.agents.context_cache_config import ContextCacheConfig

from agent_react_number_guesser.guess_number import guess_number
from common.ai_model import GEMINI_MODEL
from common.otel_plugin import OtelTracingPlugin

agent_react_number_guesser = LlmAgent(
    name="NumberGuesser",
    model=GEMINI_MODEL,
    description="You are an agent that guesses a number between 1 and 100 based on user hints.",
    instruction="""
When the user says 'play', start the number guessing game.
Generate a random number between 0 and 100. 
Call the guess_number tool with the number to verify if it's correct.
The tool will return whether the number is bigger, smaller, or correct.
Continue generating new numbers based on tool responses and use the tool to 
verify until they guess the correct number.
""",
    generate_content_config=GenerateContentConfig(
        temperature=0.0,
        top_p=0.95,
    ),
    tools=[guess_number],
)
# root_agent = agent_react_number_guesser

app = App(
    name="agent_react_number_guesser",
    root_agent=agent_react_number_guesser,
    plugins=[OtelTracingPlugin()],
    context_cache_config=ContextCacheConfig(
        min_tokens=4096,
        ttl_seconds=600,  # 10 mins for research sessions
        cache_intervals=3,  # Maximum invocations before cache refresh
    ),
)
