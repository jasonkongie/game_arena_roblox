# games/text_generation.py

import openai
from config import config

# Load configurations
MODEL_CONFIG = config["Model"]
GENERATION_CONFIG = config["Generation"]

# Set up OpenAI API key
openai.api_key = MODEL_CONFIG["openai_api_key"]

def generate_ai_response(game):
    # Build the conversation
    messages = [{"role": "system", "content": game.system_prompt}] + game.conversation

    # Prepare API parameters
    api_params = {
        "model": MODEL_CONFIG["model_name"],
        "messages": messages,
        "temperature": GENERATION_CONFIG.get("temperature", 1.0),
        "max_tokens": GENERATION_CONFIG.get("max_tokens", 150),
        "top_p": GENERATION_CONFIG.get("top_p", 1.0),
        "frequency_penalty": GENERATION_CONFIG.get("frequency_penalty", 0.0),
        "presence_penalty": GENERATION_CONFIG.get("presence_penalty", 0.0),
    }

    # Remove parameters that are None
    api_params = {k: v for k, v in api_params.items() if v is not None}

    # Call OpenAI API
    response = openai.ChatCompletion.create(**api_params)

    # Extract AI's message
    ai_message = response.choices[0].message.content.strip()
    return ai_message