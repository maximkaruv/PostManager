import json

class History:
    def __init__(self):
        self.history_file = 'history.json'

    def _get(self):
        with open(self.history_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def add(self, id):
        history = self._get()
        history.append(id)
        with open(self.history_file, 'w', encoding='utf-8') as file:
            json.dump(history, file, indent=2, ensure_ascii=False)
    
    def has(self, id):
        history = self._get()
        return id in history