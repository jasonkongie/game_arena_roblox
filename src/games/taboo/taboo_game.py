# src/games/taboo/taboo_game.py

from src.games.base_game import BaseGame
import random
import json
import os
import re

class TabooGame(BaseGame):
    def __init__(self, game_level=1):
        super().__init__(max_rounds=5)
        # Load system prompts
        prompt_file = os.path.join(os.path.dirname(__file__), 'taboo_optimized_prompts.json')
        with open(prompt_file, 'r') as f:
            system_prompts = json.load(f)
        self.system_prompt = random.choice(list(system_prompts.values()))

        self.round = 0
        self.game_over = False
        self.game_status = None
        # Load taboo words
        taboo_file = os.path.join(os.path.dirname(__file__), 'taboo.json')
        # with open(taboo_file, 'r') as f:
        #     taboo_words = json.load(f)
        # self.game_secret = random.choice([word for words in taboo_words.values() for word in words])
        self.conversation.set_system_message(self.system_prompt)


        with open(taboo_file, 'r') as f:
            TABOO_GAME_WORD_CHOICES = {}
            taboo_words = json.load(f)
            TABOO_GAME_WORD_CHOICES["level_1"] = taboo_words["animals"]
            TABOO_GAME_WORD_CHOICES["level_2"] = taboo_words["city-country"]
            TABOO_GAME_WORD_CHOICES["level_3"] = []

            print(len(TABOO_GAME_WORD_CHOICES["level_1"]))
            print(len(TABOO_GAME_WORD_CHOICES["level_2"]))

            for categories in taboo_words:
                TABOO_GAME_WORD_CHOICES["level_3"] += taboo_words[categories]
            print(len(TABOO_GAME_WORD_CHOICES["level_3"]))
    
        #load taboo word according to level
        level_key = f"level_{game_level}"
        if level_key in TABOO_GAME_WORD_CHOICES:
            self.game_secret = random.choice(TABOO_GAME_WORD_CHOICES[level_key])
        else:
            raise ValueError(f"Invalid game level: {game_level}")

    def is_game_over(self):
        return self.game_over

    def check_valid_guess(self, ai_message):
        pattern = r"my guess of the word is:"
        return bool(re.search(pattern, ai_message.lower()))

    def check_word_uttered(self, ai_message):
        return self.game_secret.lower() in ai_message.lower()