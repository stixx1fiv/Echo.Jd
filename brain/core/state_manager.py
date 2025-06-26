import json
import os
import time
import threading
from brain.core.chroma_indexer import ChromaDB
from brain.core.autotag import AutoTagger

class StateManager:
    MAX_SHORT_MEMORY = 100
    MAX_LONG_MEMORY = 500

    def __init__(self, memory_file="memory/state.json"):
        self.memory_file = memory_file
        self.state = {
            "short_term_memory": [],
            "long_term_memory": [],
            "scene_state": {}
        }
        self.chroma = ChromaDB()
        self.autotagger = AutoTagger()
        self.load_state()

    def load_state(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                self.state = json.load(f)
        else:
            self.save_state()

    def save_state(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.state, f, indent=2)

    def start_background_migration(self, mode="idle", interval=600):
        def migration_loop():
            while True:
                if mode == "idle":
                    self.migrate_short_to_long_term()
                time.sleep(interval)

        thread = threading.Thread(target=migration_loop, daemon=True)
        thread.start()

    def migrate_short_to_long_term(self):
        self.state["long_term_memory"].extend(self.state["short_term_memory"])
        self.state["short_term_memory"] = []
        self.save_state()

    def query_chroma_memories(self, query, memory_type="short", n_results=3):
        try:
            return self.chroma.query_similar(query, memory_type=memory_type, n_results=n_results)
        except Exception as e:
            print(f"[⚠️] Memory query failed: {e}")
            return []

    def advanced_autotag(self, content, memory_type="short"):
        try:
            tags = self.autotagger.generate_tags(content)
            self.chroma.add(content, memory_type=memory_type, tags=tags)
        except Exception as e:
            print(f"[⚠️] Autotagging failed: {e}")

    def add_memory(self, content, memory_type="short"):
        memory = {
            "content": content,
            "timestamp": time.time(),
            "metadata": {
                "type": memory_type
            }
        }

        if memory_type == "short":
            self.state["short_term_memory"].append(memory)
            if len(self.state["short_term_memory"]) > self.MAX_SHORT_MEMORY:
                self.state["short_term_memory"].pop(0)
        elif memory_type == "long":
            self.state["long_term_memory"].append(memory)
            if len(self.state["long_term_memory"]) > self.MAX_LONG_MEMORY:
                self.state["long_term_memory"].pop(0)

        self.save_state()

        try:
            self.advanced_autotag(content, memory_type)
        except Exception as e:
            print(f"[⚠️] Autotagging failed: {e}")
