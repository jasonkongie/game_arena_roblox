import random
from abc import ABC, abstractmethod
from typing import Callable

import re
import os
import hashlib

from fschat.conversation_game import Conversation
from fastchat.model.model_adapter import get_conversation_template
from utils import get_model_list


def generate_hash(text: str) -> str:
    """Generate a 4-character hash from a given string."""
    return hashlib.md5(text.encode()).hexdigest()[:4]

def question_header_in_output_stream(s):
    pattern = r'question \d+:'
    #if len(re.findall(pattern, s.lower())) !=0 and int(list(re.findall(number, s.lower()))[0]) == n:
    if len(re.findall(pattern, s.lower())) !=0:
        return True
    else:
        return False

def guess_in_output_stream(s):
    pattern = r"my guess of the word is:"
    if len(re.findall(pattern, s.lower())) != 0:
        return True
    else:
        return False


class BaseGame(ABC):
    def __init__(self, max_rounds: int) -> None:

        self.max_rounds = max_rounds
        # self.save_path = save_path #former parameter
        # self.conversation = [] #we don't save conversation here. We use fschat/conversation_game.py
        
        models, _, api_endpoint_info = get_model_list(
            'src/config/api_endpoint.json', multimodal=False
        )
        self.model_name = random.choice(models)
        self.model_api_info = api_endpoint_info[self.model_name]
        self.conversation = get_conversation_template(self.model_name)
        self.round = 0
        self.game_over = False
        self.game_status = None
        self.system_prompt = None  # To be set by subclasses
        # self.game_name = ""
        # self.game_rule = ""
        # self.game_start = False
        # self.generate_next_llm_query = False
        # self.next_llm_query_type = None
        
        self.available_levels = []
        self.game_level = None


    def initialize_game(self, conversation: Conversation) -> None:
        conversation.append_message(conversation.roles[0], self.first_user_message)

    def generation_response(
        self,
        type: str,
        stream_iter_fn: Callable,
        conversation: Conversation,
        # model_name: str,
        # model_api_info: dict,
        temperature: float = 0.0,
        top_p: float = 1.0,
        max_new_tokens: int = 1024,
        state=None,
        use_recommended_config: bool = False,
    ) -> str:
        if use_recommended_config:
            recommended_config = self.model_api_info.get("recommended_config", None)
            if recommended_config is not None:
                temperature = recommended_config.get("temperature", 0.0)
                top_p = recommended_config.get("top_p", 1.0)
        # Generating new question
        print(self.model_name)
        prefix = None
        if type == 'question':
            prefix = f'Question {self.round + 1}:'
        elif type == 'answer':
            prefix = ' '
        elif type == 'taboo_guess':
            prefix = 'my guess of the word is:'
        else:
            raise NotImplementedError(f"response type: {type} is not implemented.")
        
        # if 'mistral' in self.model_name:
        #     conversation.append_message(
        #         conversation.roles[1], prefix
        #     )
        # else:
        #     conversation.append_message(
        #         conversation.roles[1], None
        #     )


        stream_iter = stream_iter_fn(
            conversation,
            self.model_name,
            self.model_api_info,
            temperature=temperature,
            top_p=top_p,
            max_new_tokens=max_new_tokens,
            state=state,
        )
        output = ""
        # print(stream_iter)
        for data in stream_iter:
            print(data)
            assert data["error_code"] == 0
            # Update the output with the latest text from the API
            output = data["text"].strip()

        # Post-process the output based on the type
        if type == 'question' and self.round + 1 < self.max_rounds:
            if question_header_in_output_stream(output):
                #conversation.update_last_message(output)
                print("prefix:")
                print(prefix)
                output = output[12:]        # FIXME (lanxiang): use regular expression to strip 'question #:'

            output = prefix + ' ' + output
        elif type == 'taboo_guess':
            if not guess_in_output_stream(output):
                output = prefix + ' ' + output
        conversation.update_last_message(output)
        
        self.round += 1
        return output

     # def update_conversation_with_user_choice(
    def update_user_conversation(
        self, conversation: Conversation, user_choice: str
    ) -> None:
        # conversation.roles[0] == "USER"
        # conversation.roles[1] == "ASSISTANT"
        conversation.append_message(conversation.roles[0], user_choice)

    def update_AI_conversation(
        self, conversation: Conversation, user_choice: str
    ) -> None:
        # conversation.roles[0] == "USER"
        # conversation.roles[1] == "ASSISTANT"
        conversation.append_message(conversation.roles[1], user_choice)


    def reach_max_round(self) -> bool:
        if self.round >= self.max_round:
            return True
        return False
    
    # @abstractmethod
    # def is_llm_giving_answer(self, conversation: Conversation) -> bool:
    #     pass
    
    # def is_llm_triggering_termination(self, conversation: Conversation) -> bool:
    #     pass
    
    # def is_llm_illegal_input(self, input_text: str) -> bool:
    #     pass