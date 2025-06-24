import json
import threading
import time
import os
import chromadb
from chromadb.config import Settings
from brain.core.nlp_utils import advanced_autotag

class StateManager:
    def __init__(self, memory_file="memory/state.json", mood_decay_rate=0.01):
        self.memory_file = memory_file
        self.state = {
            "mood": "neutral",
            "short_term_memory": [],
            "long_term_memory": [],
            "pet_names": [],
            "last_updated": time.time(),
            "mode": "idle",
            "scene": "default"
        }
        self.modes = ["idle", "assist", "chat"]
        self.lock = threading.Lock()
        self.manual_overrides = {}
        self.running = True  # For clean thread stops
        self.load_state()
        self.mood_decay_rate = mood_decay_rate
        self._init_chromadb()
        self._observers = []
        self.start_background_migration()

    def _init_chromadb(self):
        self.chroma_client = chromadb.Client(Settings(persist_directory="chromadb_data"))
        self.short_mem_collection = self.chroma_client.get_or_create_collection("short_term_memory")
        self.long_mem_collection = self.chroma_client.get_or_create_collection("long_term_memory")

    def load_state(self):
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                self.state = json.load(f)
            print("[🔄] State loaded from disk.")
        except (FileNotFoundError, json.JSONDecodeError):
            print("[⚠️] No valid previous state found. Starting fresh.")

    def save_state(self):
        with self.lock:
            try:
                with open(self.memory_file, "w", encoding="utf-8") as f:
                    json.dump(self.state, f, indent=2)
            except Exception as e:
                print(f"[⚠️] Failed to save state: {e}")

    def update_mood(self, new_mood):
        with self.lock:
            old_mood = self.state.get("mood", "neutral")
            self.state["mood"] = new_mood
            self._touch()
            print(f"[💢] Mood changed: {old_mood} → {new_mood}")
        self.save_state()
        self.notify_observers("mood_changed", {"old_mood": old_mood, "new_mood": new_mood})

    def decay_mood(self):
        with self.lock:
            if self.state["mood"] != "neutral":
                self.state["mood"] = "neutral"
                self._touch()
                print(f"[🍂] Mood decayed to neutral.")
                self.save_state()

    def add_memory(self, text, memory_type="short"):
        target = "short_term_memory" if memory_type == "short" else "long_term_memory"
        with self.lock:
            self.state[target].append({"timestamp": time.time(), "text": text})
            self._touch()
        self.save_state()
        self.add_memory_chroma(text, memory_type)

    def add_memory_chroma(self, text, memory_type="short", metadata=None):
        collection = self.short_mem_collection if memory_type == "short" else self.long_mem_collection
        doc_id = f"{memory_type}_{int(time.time()*1000)}"
        meta = metadata or {"timestamp": time.time()}
        meta["tags"] = advanced_autotag(text)
        for k, v in meta.items():
            if isinstance(v, list):
                meta[k] = ','.join(map(str, v))
        collection.add(documents=[text], metadatas=[meta], ids=[doc_id])

    def get_memories(self, memory_type="short"):
        with self.lock:
            target = "short_term_memory" if memory_type == "short" else "long_term_memory"
            return list(self.state.get(target, []))

    def set_mode(self, mode):
        with self.lock:
            if mode in self.modes:
                old_mode = self.state.get("mode", "idle")
                self.state["mode"] = mode
                self._touch()
                print(f"[⚙️] Mode: {old_mode} → {mode}")
                self.save_state()
            else:
                print(f"[⚠️] Invalid mode: {mode}")

    def set_scene(self, scene_name):
        scene_path = os.path.join("scenes", f"{scene_name}.json")
        with self.lock:
            try:
                with open(scene_path, "r") as f:
                    scene_data = json.load(f)
                self.state["scene"] = scene_name
                self.state["scene_data"] = scene_data
                self._touch()
                print(f"[🎬] Scene set: {scene_name}")
                self.save_state()
            except Exception as e:
                print(f"[⚠️] Scene error: {e}")

    def _touch(self):
        self.state["last_updated"] = time.time()

    def register_observer(self, callback):
        self._observers.append(callback)

    def notify_observers(self, event_type, data=None):
        for cb in self._observers:
            try:
                cb(event_type, data)
            except Exception as e:
                print(f"[⚠️] Observer error: {e}")

    def start_background_migration(self, interval_minutes=10):
        def migrate_loop():
            while self.running:
                if self.state["mode"] == "idle":
                    self.migrate_legacy_to_chroma()
                time.sleep(interval_minutes * 60)
        t = threading.Thread(target=migrate_loop, daemon=True)
        t.start()
        print(f"[🧠] Memory migration thread live.")

    def migrate_legacy_to_chroma(self, path="memory/state.json"):
        try:
            with open(path, "r", encoding="utf-8") as f:
                old_memories = json.load(f)
        except Exception as e:
            print(f"[⚠️] Migration failed: {e}")
            return
        for mem in old_memories:
            text = mem.get("text", "")
            if text:
                self.add_memory_chroma(text, metadata={"timestamp": mem.get("timestamp", time.time()), "migrated": True})
        print(f"[🔄] Legacy memories migrated.")

    def stop(self):
        self.running = False

    def get_mood(self):
        """
        Returns the current mood state as a string, e.g. 'neutral', 'happy', 'sad', etc.
        """
        with self.lock:
            return self.state.get("mood", "neutral")

    def get_mode(self):
        """
        Returns the current mode state as a string, e.g. 'idle', 'assist', 'chat', etc.
        """
        with self.lock:
            return self.state.get("mode", "idle")

    def get_scene(self):
        """
        Returns the current scene name as a string, e.g. 'default', 'office', etc.
        """
        with self.lock:
            return self.state.get("scene", "default")

    def rewrite_memory(self, memory_id, new_text, memory_type="short"):
        """
        Rewrite a memory entry by ID in the state and save to disk.
        """
        with self.lock:
            target = "short_term_memory" if memory_type == "short" else "long_term_memory"
            for mem in self.state.get(target, []):
                if mem.get("id") == memory_id:
                    mem["text"] = new_text
                    mem["edited_timestamp"] = time.time()
                    break
            self._touch()
        self.save_state()

    def mark_context_stale(self):
        with self.lock:
            self.state["context_stale"] = True

    def clear_context_stale(self):
        with self.lock:
            self.state["context_stale"] = False

    def is_context_stale(self):
        with self.lock:
            return self.state.get("context_stale", False)

    def migrate_long_term_memories_to_chroma(self):
        # Example: migrate all long-term memories to ChromaDB
        with self.lock:
            for mem in self.state.get("long_term_memory", []):
                self.add_memory_chroma(mem["text"], memory_type="long", metadata=mem)
        print("[StateManager] Migrated long-term memories to ChromaDB.")

    def rebuild_prompt_context(self):
        # Placeholder for context rebuild logic
        print("[StateManager] Rebuilt prompt context.")
