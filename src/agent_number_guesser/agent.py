from google.adk.agents import LlmAgent

MODEL = "gemini-3-flash-preview"

agent_number_guesser = LlmAgent(
    name="NumberGuesser",
    model=MODEL,
    description="You are an agent that guesses a number between 1 and 100 based on user hints.",
    instruction="",
)
root_agent = agent_number_guesser