



# src/games/akinator/akinator_game.py

from src.games.base_game import BaseGame
import random
import json
import os
import re
from fschat.conversation_game import Conversation


# paths to the JSON files
LEVEL_DATA_FILES = {
    1: "./assets/level1_applicances.json",
    2: "./assets/level2_instruments.json",
    3: "./assets/level3_animals.json"
}

def load_prompts(prompt_file_path):
    with open(prompt_file_path, 'r') as f:
        return json.load(f)

class AkinatorGame(BaseGame):
    
    def __init__(self, level: int):
        #add level
        self.level = level
        max_round_dict = {1: 20, 2: 15, 3: 10}
        max_round = max_round_dict.get(level)

        super().__init__(max_rounds=max_round)
        # Load system prompts
        prompt_file = os.path.join(os.path.dirname(__file__), 'akinator_optimized_prompts.json')
        self.game_secret = self.load_random_object(level)
        
        # Randomly select a system prompt
        system_prompts = load_prompts(prompt_file)
        self.system_prompt = random.choice(list(system_prompts.values()))
        self.conversation.set_system_message(self.system_prompt)

        # Set allowed answers based on the level
        if level in [1, 2]:
            self.allowed_answers = ["Yes", "Probably Yes", "Don't Know", "Probably No", "No"]
        else:  # Level 3
            self.allowed_answers = ["Yes", "Don't Know", "No"]
        
        accepted_answers = ', '.join([f'"{ans}"' for ans in self.allowed_answers])
        self.system_prompt += f"\n\nAccepted Answers: Only these responses are acceptable: {accepted_answers}."
        self.system_prompt += f"\n\nCurrent level is {self.level}, You can only ask {max_round} questions."

        self.current_round = 0
        self.game_over = False
        self.game_status = None
        

    def is_game_over(self):
        return self.game_over
    
    def reach_max_round(self):
        if self.current_round > self.max_rounds:
            self.game_status = 'PLAYER_LOSE'
            self.game_over = True
            return True
        return False
    
    def load_random_object(self, level):
        data_file = LEVEL_DATA_FILES.get(level)
        if not data_file or not os.path.exists(data_file):
            raise FileNotFoundError(f"Data file for level {level} not found.")
        with open(data_file, 'r') as f:
            objects_list = json.load(f)
        return random.choice(objects_list)
    
    def check_akinator_valid_guess(self, s):
        pattern = r"this is a guess"
        return len(re.findall(pattern, s.lower())) != 0
    
    def guessed_word_correctly(self, s):
        pattern = self.game_secret.lower()
        return len(re.findall(pattern, s.lower())) != 0
