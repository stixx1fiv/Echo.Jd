import os
import json
import threading
import logging
from datetime import datetime, timedelta
from uuid import uuid4

class MemoryEntry:
    def __init__(
        self, content, importance=0.5, mood_tag="neutral", types=None,
        topic_tags=None, ambient_tags=None, decay_rate=0.01, timestamp=None, adjacent_uuids=None
    ):
        self.content = content
        self.importance = importance
        self.mood_tag = mood_tag
        self.types = types or []
        self.topic_tags = topic_tags or []
        self.ambient_tags = ambient_tags or []
        self.decay_rate = decay_rate
        self.timestamp = timestamp or datetime.utcnow()
        self.uuid = str(uuid4())
        self.adjacent_uuids = adjacent_uuids or []

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return MemoryEntry(
            content=data.get("content"),
            importance=data.get("importance", 0.5),
            mood_tag=data.get("mood_tag", "neutral"),
            types=data.get("types", []),
            topic_tags=data.get("topic_tags", []),
            ambient_tags=data.get("ambient_tags", []),
            decay_rate=data.get("decay_rate", 0.01),
            timestamp=datetime.fromisoformat(data.get("timestamp")) if data.get("timestamp") else datetime.utcnow(),
            adjacent_uuids=data.get("adjacent_uuids", [])
        )

class MemoryDaemon:
    def __init__(self, memory_file, archive_file, state_manager=None):
        self.memory_file = memory_file
        self.archive_file = archive_file
        self.state_manager = state_manager
        self.running = False
        self.memory = []
        self.shutdown_event = threading.Event()
        self._thread = None
        self.load_memory()

    def load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                try:
                    self.memory = json.load(f)
                    if not isinstance(self.memory, list):
                        print("[MemoryDaemon] Memory file is not a list. Resetting to empty list.")
                        self.memory = []
                    else:
                        print(f"[MemoryDaemon] Loaded {len(self.memory)} memories.")
                except json.JSONDecodeError:
                    print("[MemoryDaemon] Memory file is corrupted. Starting fresh.")
                    self.memory = []
        else:
            self.memory = []

    def save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.memory, f, indent=4)

    def archive_memory(self, item):
        if not os.path.exists(self.archive_file):
            with open(self.archive_file, 'w') as f:
                json.dump([], f)

        with open(self.archive_file, 'r+') as f:
            archive = json.load(f)
            if not isinstance(archive, list):
                print("[MemoryDaemon] Archive file is not a list. Resetting to empty list.")
                archive = []
            archive.append(item)
            f.seek(0)
            json.dump(archive, f, indent=4)
            f.truncate()
            print(f"[MemoryDaemon] Archived memory: {item.get('uuid', 'Unknown ID')}")

    def update_memory_weights(self):
        now = datetime.utcnow()
        updated_memories = []
        for item in self.memory:
            try:
                mem = MemoryEntry.from_dict(item)
                age_days = (now - mem.timestamp).days
                decay_penalty = mem.decay_rate * age_days
                score = mem.importance - decay_penalty
                if score <= 0.1:
                    self.archive_memory(mem.to_dict())
                else:
                    updated_memories.append(mem.to_dict())
            except Exception as e:
                print(f"[MemoryDaemon] Error updating memory: {e}")
        self.memory = updated_memories
        self.save_memory()

    def score_memory(self, mem, current_mood, query_tags):
        importance_weight = mem.importance * 0.5
        mood_match = 1 if mem.mood_tag == current_mood else 0.5
        mood_weight = mood_match * 0.3
        topic_overlap = len(set(mem.topic_tags) & set(query_tags)) * 0.1
        ambient_overlap = len(set(mem.ambient_tags) & set(query_tags)) * 0.05
        age_days = (datetime.utcnow() - mem.timestamp).days
        decay_penalty = mem.decay_rate * age_days
        return (importance_weight + mood_weight + topic_overlap + ambient_overlap) - decay_penalty

    def retrieve_memories(self, current_mood, query_tags, max_results=5):
        scored = []
        for item in self.memory:
            try:
                mem = MemoryEntry.from_dict(item)
                score = self.score_memory(mem, current_mood, query_tags)
                scored.append((score, mem))
            except Exception as e:
                print(f"[MemoryDaemon] Error scoring memory: {e}")
        scored.sort(reverse=True, key=lambda x: x[0])
        return [mem.to_dict() for score, mem in scored[:max_results]]

    def start(self):
        if self.running:
            print("[MemoryDaemon] Already running.")
            return
        print("[MemoryDaemon] Starting daemon thread...")
        self.running = True
        self._thread = threading.Thread(target=self.run, daemon=True)
        self._thread.start()

    def run(self):
        print("[MemoryDaemon] MemoryDaemon started.")
        while self.running:
            self.update_memory_weights()
            self.shutdown_event.wait(10)

    def stop(self):
        print("[MemoryDaemon] Attempting to stop MemoryDaemon...")
        self.running = False
        self.shutdown_event.set()
        if self._thread:
            self._thread.join()
        logging.info("MemoryDaemon stopped.")

    def add_memory(self, memory_item):
        if isinstance(memory_item, MemoryEntry):
            self.memory.append(memory_item.to_dict())
        elif isinstance(memory_item, dict):
            self.memory.append(memory_item)
        else:
            raise TypeError("Memory must be a dict or MemoryEntry.")
        self.save_memory()

    def prepare_prompt_context(self):
        if not self.memory:
            return "(No recent memories.)"
        recent = [item for item in self.memory if isinstance(item, dict)][-5:]
        summary = "\n".join([
            f"[{item.get('timestamp', 'unknown')}] {item.get('content', str(item))}" for item in recent
        ])
        return summary

    def on_heartbeat(self):
        print("[MemoryDaemon] Heartbeat received. Syncing to StateManager...")
        if hasattr(self, 'state_manager') and self.state_manager:
            for item in self.memory:
                if isinstance(item, dict) and 'content' in item:
                    self.state_manager.add_memory_chroma(item['content'], memory_type="short", metadata=item)
