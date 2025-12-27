from google.adk.agents import LlmAgent

from agent_number_guesser.guess_number import guess_number

MODEL = "gemini-3-flash-preview"

agent_number_guesser = LlmAgent(
    name="NumberGuesser",
    model=MODEL,
    description="You are an agent that guesses a number between 1 and 100 based on user hints.",
    instruction="""
When the user says 'play', start the number guessing game.
Generate a random number between 0 and 100. 
Call the guess_number tool with the number to verify if it's correct.
The tool will return whether the number is bigger, smaller, or correct.
Continue generating new numbers based on tool responses and use the tool to 
verify until they guess the correct number.
""",
    tools=[guess_number],
)
root_agent = agent_number_guesser
