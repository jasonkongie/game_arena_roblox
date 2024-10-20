# games/taboo/taboo_game.py

from games.base_game import BaseGame
from games.text_generator import TextGenerator
import random
import json
import os
import re

class TabooGame(BaseGame):
    def __init__(self):
        super().__init__(max_rounds=5, save_path='output/taboo/')
        # Load system prompts
        prompt_file = os.path.join(os.path.dirname(__file__), 'taboo_optimized_prompts.json')
        with open(prompt_file, 'r') as f:
            system_prompts = json.load(f)
        self.system_prompt = random.choice(list(system_prompts.values()))
        self.text_generator = TextGenerator()

        # Load taboo words
        taboo_file = os.path.join(os.path.dirname(__file__), 'taboo.json')
        with open(taboo_file, 'r') as f:
            taboo_words = json.load(f)
        # Flatten the list of words
        self.game_secret = random.choice([word for words in taboo_words.values() for word in words])

    def generate_ai_response(self):
        ai_message = self.text_generator.generate_response(self.system_prompt, self.conversation)
        return ai_message

    def check_valid_guess(self, ai_message):
        pattern = r"my guess of the word is:"
        return bool(re.search(pattern, ai_message.lower()))

    def check_word_uttered(self, ai_message):
        return self.game_secret.lower() in ai_message.lower()