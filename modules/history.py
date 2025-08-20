from pathlib import Path
import json

class History:
    def __init__(self, filename):
        self.history_file = Path(f'histories/{filename}.json')
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self.history_file.touch()

    def _get(self):
        try:
            with open(self.history_file, 'r', encoding='utf-8') as file:
                return json.load(file)
        except:
            return []

    def add(self, id):
        history = self._get()
        history.append(id)
        with open(self.history_file, 'w', encoding='utf-8') as file:
            json.dump(history, file, indent=2, ensure_ascii=False)
    
    def has(self, id):
        history = self._get()
        return id in history