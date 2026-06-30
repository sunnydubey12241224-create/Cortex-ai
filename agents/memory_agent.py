import json
import os

MEMORY_FILE = "memory.json"

class MemoryAgent:

    def load(self):
        if not os.path.exists(MEMORY_FILE):
            return {}
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)

    def save(self, data):
        with open(MEMORY_FILE, "w") as f:
            json.dump(data, f)

    def store(self, key, value):
        memory = self.load()
        memory[key] = value
        self.save(memory)
        return f"I will remember that your {key} is {value}"

    def recall(self, key):
        memory = self.load()
        return memory.get(key, None)