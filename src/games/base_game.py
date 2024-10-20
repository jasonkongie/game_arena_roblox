# games/base_game.py

class BaseGame:
    def __init__(self, max_rounds, save_path):
        self.max_rounds = max_rounds
        self.save_path = save_path
        self.conversation = []
        self.current_round = 0
        self.game_over = False
        self.game_status = None
        self.system_prompt = None  # To be set by subclasses

    def update_conversation(self, role, content):
        self.conversation.append({"role": role, "content": content})

    def is_game_over(self):
        return self.game_over