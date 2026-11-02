from copy import deepcopy
from stack import Stack

class GameHistory:

    def __init__(self):
        self.undo_stack = Stack()

    def save_snapshot(self, game_snapshot):
        self.undo_stack.push(game_snapshot)

    def undo(self):
        if self.undo_stack.is_empty():
            return None

        return self.undo_stack.pop()

    def clear(self):
        self.undo_stack = Stack()

    def can_undo(self):
        return not self.undo_stack.is_empty()
