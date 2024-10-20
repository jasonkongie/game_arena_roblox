# TextGeneration.py

import openai
from config import config
import json

# Load configurations
MODEL_CONFIG = config["Model"]
GENERATION_CONFIG = config["Generation"]
JSON_PATH = "./GenerationTemplates/template.json"  # Adjust the path if necessary
Template = []

def LoadModel():
    global Template
    # Set up OpenAI API key
    openai.api_key = MODEL_CONFIG["openai_api_key"]

    # Load template (system prompts)
    with open(JSON_PATH, 'r') as file:
        Template = json.load(file)

def GenerateText(conversation_history):
    # Build the conversation by combining the template and history
    conversation = Template + conversation_history

    # Make the API call to OpenAI
    response = openai.ChatCompletion.create(
        model=MODEL_CONFIG["model_name"],
        messages=conversation,
        temperature=GENERATION_CONFIG.get("temperature", 1.0),
        max_tokens=GENERATION_CONFIG.get("max_tokens", 150),
        top_p=GENERATION_CONFIG.get("top_p", 1.0),
        frequency_penalty=GENERATION_CONFIG.get("frequency_penalty", 0.0),
        presence_penalty=GENERATION_CONFIG.get("presence_penalty", 0.0),
    )
    # Extract the assistant's reply
    Output = response['choices'][0]['message']['content'].strip()
    return Output

def GenerateModelInput(messages):
    result = []
    for message in messages:
        nickname = message["nickname"]
        content = message["content"]
        # Map nickname to role
        if nickname.lower() == "assistant":
            role = "assistant"
        elif nickname.lower() == "system":
            role = "system"
        else:
            role = "user"
        result.append({"role": role, "content": content})
    return result