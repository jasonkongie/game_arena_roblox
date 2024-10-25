# src/games/akinator/akinator_game.py

from src.games.base_game import BaseGame
import random
import json
import os

class AkinatorGame(BaseGame):
    def __init__(self):
        super().__init__(max_rounds=20, save_path='output/akinator/')
        # Load system prompts
        prompt_file = os.path.join(os.path.dirname(__file__), 'akinator_optimized_prompts.json')
        game_secret_file = os.path.join(os.path.dirname(__file__), 'akinator.json')
        with open(prompt_file, 'r') as f:
            system_prompts = json.load(f)
        # Randomly select a system prompt
        self.system_prompt = random.choice(list(system_prompts.values()))
        # Initialize conversation
        self.conversation = []
        self.current_round = 0
        self.game_over = False
        self.game_status = None

        #Game secret!
        with open(game_secret_file, 'r') as f:
            game_secrets = json.load(f)
        # Randomly select a system prompt
        self.game_secret = random.choice(list(game_secrets))

        # Add system prompt to conversation
        self.update_conversation('system', self.system_prompt)

    def update_conversation(self, nickname, content):
        self.conversation.append({"nickname": nickname, "content": content})

    def is_game_over(self):
        return self.game_over

    def check_valid_guess(self, ai_message):
        # Implement your logic to check if the AI's guess is valid
        return "my guess is" in ai_message.lower()