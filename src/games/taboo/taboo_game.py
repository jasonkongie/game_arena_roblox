# src/games/taboo/taboo_game.py

from src.games.base_game import BaseGame
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
        # Initialize conversation
        self.conversation = []
        self.current_round = 0
        self.game_over = False
        self.game_status = None
        # Load taboo words
        taboo_file = os.path.join(os.path.dirname(__file__), 'taboo.json')
        with open(taboo_file, 'r') as f:
            taboo_words = json.load(f)
        self.game_secret = random.choice([word for words in taboo_words.values() for word in words])

        # Add system prompt to conversation
        self.update_conversation('system', self.system_prompt)

    def update_conversation(self, nickname, content):
        self.conversation.append({"nickname": nickname, "content": content})

    def is_game_over(self):
        return self.game_over

    def check_valid_guess(self, ai_message):
        pattern = r"my guess of the word is:"
        return bool(re.search(pattern, ai_message.lower()))

    def check_word_uttered(self, ai_message):
        return self.game_secret.lower() in ai_message.lower()