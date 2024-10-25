# src/games/akinator/akinator_game.py

from src.games.base_game import BaseGame
import random
import json
import os


class AkinatorGame(BaseGame):
    def __init__(self):
        super().__init__(max_rounds=20)
        # Load system prompts
        prompt_file = os.path.join(os.path.dirname(__file__), 'akinator_optimized_prompts.json')
        game_secret_file = os.path.join(os.path.dirname(__file__), 'akinator.json')
        with open(prompt_file, 'r') as f:
            system_prompts = json.load(f)
        # Randomly select a system prompt
        self.system_prompt = random.choice(list(system_prompts.values()))
        # Initialize conversation
        # self.conversation = []

        #randomly choose a model: MOVE TO BASEGAME.py
        # models, _, _ = get_model_list(
        #     '../../config/api_endpoint.json ', multimodal=False
        # )
        # model_name = random.choice(models)

        # self.conversation = get_conversation_template(model_name)


        self.current_round = 0
        self.game_over = False
        self.game_status = None

        #Game secret!
        with open(game_secret_file, 'r') as f:
            game_secrets = json.load(f)
        # Randomly select a system prompt
        self.game_secret = random.choice(list(game_secrets))

        # Add system prompt to conversation
        self.conversation.set_system_message(self.system_prompt)
        # self.update_conversation('system', self.system_prompt)

    def is_game_over(self):
        return self.game_over

    def check_valid_guess(self, ai_message):
        # Implement your logic to check if the AI's guess is valid
        return "my guess is" in ai_message.lower()