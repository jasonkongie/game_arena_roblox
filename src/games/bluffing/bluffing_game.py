# src/games/bluffing/bluffing_game.py

import random
import json
import os
import re
from games.base_game import BaseGame

class BluffingGame(BaseGame):
    def __init__(self):
        super().__init__(max_rounds=6, save_path='output/bluffing/')
        # Load system prompts
        prompt_file = os.path.join(os.path.dirname(__file__), 'bluffing_optimized_prompts.json')
        with open(prompt_file, 'r') as f:
            system_prompts = json.load(f)
        all_prompts = list(system_prompts.values())
        self.system_prompt = random.choice(all_prompts)
        self.system_prompt_index = all_prompts.index(self.system_prompt)

        # Load bluffing questions
        bluffing_questions_file = os.path.join(os.path.dirname(__file__), 'bluffing.json')
        with open(bluffing_questions_file, 'r') as f:
            self.bluffing_questions = json.load(f)
        self.system_question = random.choice(self.bluffing_questions)

        # Initialize conversation
        self.conversation = []
        self.current_round = 0
        self.game_over = False
        self.game_status = None

        # Game-specific attributes
        self.first_user_message = None  # The user's initial statement
        self.secret_system_message = None  # Not used in this context

        # Add system prompt to conversation
        self.update_conversation('system', self.system_prompt)

    def update_conversation(self, nickname, content):
        self.conversation.append({"nickname": nickname, "content": content})

    def is_game_over(self):
        return self.game_over

    def check_valid_guess(self, ai_message):
        pattern = r"i believe your statement is:\s*(true|false)"
        return bool(re.search(pattern, ai_message.lower()))

    def is_llm_giving_answer(self, ai_message):
        return self.check_valid_guess(ai_message)

    def check_user_win(self, ai_message, user_statement_truth):
        """
        Determine if the user wins based on the AI's guess and the actual truth of the user's statement.
        """
        ai_guess = re.search(r"i believe your statement is:\s*(true|false)", ai_message.lower())
        if ai_guess:
            ai_guess = ai_guess.group(1)
            if ai_guess == user_statement_truth.lower():
                return False  # AI guessed correctly; user loses
            else:
                return True  # AI guessed incorrectly; user wins
        return False  # No valid guess made

    def set_game_status(self, status):
        self.game_over = True
        self.game_status = status