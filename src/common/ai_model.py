import os
from google.adk.models.lite_llm import LiteLlm

GEMINI_MODEL = "gemini-3-flash-preview"

OPENROUTE_MODEL = LiteLlm(
    # Specify the OpenRouter model using 'openrouter/' prefix
    model="openrouter/xiaomi/mimo-v2-flash",
    # Explicitly provide the API key from environment variables
    api_key=os.getenv("OPENROUTER_API_KEY"),
    # Explicitly provide the OpenRouter API base URL
    api_base="https://openrouter.ai/api/v1",
)
