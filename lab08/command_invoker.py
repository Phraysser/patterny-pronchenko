class CommandInvoker:
    def __init__(self, history_limit=20):
        self._history = []
        self._undone = []
        self._history_limit = history_limit

    def execute(self, command):
        command.execute()
        self._history.append(command)
        if len(self._history) > self._history_limit:
            self._history.pop(0)
        self._undone.clear()

    def undo(self):
        if self._history:
            command = self._history.pop()
            command.undo()
            self._undone.append(command)
            return True
        return False

    def redo(self):
        if self._undone:
            command = self._undone.pop()
            command.execute()
            self._history.append(command)
            return True
        return False

    def get_history(self):
        return list(self._history)

    def get_history_size(self):
        return len(self._history)

    def clear_history(self):
        self._history.clear()
        self._undone.clear()