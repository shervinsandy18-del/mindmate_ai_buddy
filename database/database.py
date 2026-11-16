"""Local JSON persistence for MindMate."""
import json, os, uuid, shutil, copy

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT = {"notes": [], "tasks": [], "flashcards": [], "stats": {"pomodoros": 0}}


class Database:
    def __init__(self, path=None):
        self.path = path or os.path.join(BASE, "data", "mindmate_data.json")
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.data = self._load()

    def _load(self):
        data = copy.deepcopy(DEFAULT)
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    data.update(json.load(f))
            except (json.JSONDecodeError, OSError):
                try:
                    shutil.copy(self.path, self.path + ".corrupt")
                except OSError:
                    pass
                data = copy.deepcopy(DEFAULT)
        return data

    def save(self):
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
            return True
        except OSError:
            return False

    def all(self, kind):
        return self.data[kind]

    def add(self, kind, **fields):
        item = {"id": uuid.uuid4().hex[:10], **fields}
        self.data[kind].append(item)
        self.save()
        return item

    def update(self, kind, item_id, **fields):
        for item in self.data[kind]:
            if item["id"] == item_id:
                item.update(fields)
                self.save()
                return item
        return None

    def delete(self, kind, item_id):
        self.data[kind] = [i for i in self.data[kind] if i["id"] != item_id]
        self.save()

    def add_pomodoro(self):
        self.data["stats"]["pomodoros"] = self.data["stats"].get("pomodoros", 0) + 1
        self.save()
