from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from config import config
import json
import numpy as np
MODEL_CONFIG = config["Model"]
QUANTIZATION_CONFIG = config["Quantization"]
GENERATION_CONFIG = config["Generation"]
TEMPLATE_TOKENIZATION_CONFIG = config["TemplateTokenization"]
MODEL_PATH = MODEL_CONFIG["pretrained_model_name_or_path"]
JSON_PATH = "../GenerationTemplates/template.json"
Model = None
Tokenizer = None
Template = []
BNBConfig = None



def LoadModel():
    global Model
    global Tokenizer
    global Template
    global BNBConfig

    #Set up Bits and Bytes config
    BNBConfig = BitsAndBytesConfig(**QUANTIZATION_CONFIG["BitsAndBytesConfig"])

    # Load model
    Model = AutoModelForCausalLM.from_pretrained(**MODEL_CONFIG, quantization_config=BNBConfig)

    #Set up tokenizer
    Tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=MODEL_PATH)

    Tokenizer.pad_token = Tokenizer.eos_token
    # Load template
    with open(JSON_PATH, 'rb') as file:
        Template = json.load(file)


def GenerateText(History):
    TokenizedChat = Tokenizer.apply_chat_template(**TEMPLATE_TOKENIZATION_CONFIG, conversation=np.concatenate((Template, History))).to("cuda")
    InputLen = TokenizedChat.shape[1]
    GeneratedIds = Model.generate(**GENERATION_CONFIG, inputs=TokenizedChat, pad_token_id=Tokenizer.eos_token_id)
    Output = Tokenizer.batch_decode(sequences = GeneratedIds[:, InputLen:], skip_special_tokens=True)[0]
    return Output


def GenerateModelInput(messages):
    resultstring = ""
    for message in messages:
        nickname = message["nickname"]
        content = message["content"]
        resultstring += f"\n{nickname}: {content}"
    return [{"role": "user", "content": resultstring}]