# games/akinator_game.py

import json
import random
import re
import os

class AkinatorGame:
    def __init__(self, max_round=20):
        self.max_round = max_round
        self.current_round = 0
        self.game_status = None
        self.system_prompt = self.load_random_prompt()
        self.conversation = []
        self.game_over = False

    def load_random_prompt(self):
        # Adjust the path to the JSON file
        prompts_file = os.path.join(os.path.dirname(__file__), 'akinator_optimized_prompts.json')
        with open(prompts_file, 'r') as f:
            system_prompts = json.load(f)
        all_prompts = list(system_prompts.values())
        return random.choice(all_prompts)

    def check_valid_guess(self, s):
        pattern = r"this is a guess"
        return len(re.findall(pattern, s.lower())) != 0

    def is_game_over(self):
        return self.game_over or self.current_round >= self.max_round

    def update_conversation(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def get_last_message(self):
        return self.conversation[-1] if self.conversation else None