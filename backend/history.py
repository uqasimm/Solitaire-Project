from stack import Stack

class GameHistory:

    def __init__(self):
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def save_snapshot(self, game_snapshot):
        self.undo_stack.push(game_snapshot)

        self.redo_stack = Stack()

    def undo(self, current_game):
        if self.undo_stack.is_empty():
            return None

        self.redo_stack.push(current_game)

        return self.undo_stack.pop()

    def redo(self, current_game):
        if self.redo_stack.is_empty():
            return None

        self.undo_stack.push(current_game)

        return self.redo_stack.pop()

    def clear(self):
        self.undo_stack = Stack()
        self.redo_stack = Stack()

    def can_undo(self):
        return not self.undo_stack.is_empty()

    def can_redo(self):
        return not self.redo_stack.is_empty()