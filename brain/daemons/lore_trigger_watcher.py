import time
import threading
import json
import os
from brain.core.state_manager import StateManager

class LoreTriggerWatcher:
    def __init__(self, state_manager: StateManager, memory_daemon, update_interval=5, trigger_file="config/lore_triggers.json"):
        self.state_manager = state_manager
        self.memory_daemon = memory_daemon
        self.update_interval = update_interval
        self.trigger_file = trigger_file
        self._running = False
        self._thread = None
        self.triggers = self.load_triggers()

    def load_triggers(self):
        try:
            with open(self.trigger_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[LoreTriggerWatcher] Trigger file not found: {self.trigger_file}")
            return []
        except json.JSONDecodeError:
            print(f"[LoreTriggerWatcher] Invalid JSON in trigger file: {self.trigger_file}")
            return []

    def start(self):
        if self._running:
            print("[LoreTriggerWatcher] Already running.")
            return
        print("[LoreTriggerWatcher] Starting lore trigger watcher daemon...")
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        print("[LoreTriggerWatcher] Stopping lore trigger watcher daemon...")
        self._running = False
        if self._thread:
            self._thread.join()

    def _run(self):
        while self._running:
            # Get the latest short-term memories
            memories = self.memory_daemon.get_memories(memory_type="short")

            # Check for triggers in the memories
            for memory in memories:
                text = memory["text"].lower()
                for trigger in self.triggers:
                    if trigger["trigger"] in text:
                        print(f"[LoreTriggerWatcher] Triggered by: {trigger['trigger']}")
                        if "mood" in trigger:
                            self.state_manager.update_mood(trigger["mood"])
                        if "scene" in trigger:
                            self.state_manager.set_scene(trigger["scene"])

            time.sleep(self.update_interval)

if __name__ == "__main__":
    # Example usage (for testing purposes)
    from brain.daemons.memory_daemon import MemoryDaemon  # Import here to avoid circular dependency
    MEMORY_PATH = os.path.join('brain', 'memory', 'memory_archive.json')
    CONFIG_PATH = os.path.join('config', 'master_config.json')

    def load_config(path):
        with open(path, 'r') as f:
            return json.load(f)

    config = load_config(CONFIG_PATH)
    state_manager = StateManager()
    memory_daemon = MemoryDaemon(memory_file=MEMORY_PATH, config=config)
    trigger_watcher = LoreTriggerWatcher(state_manager, memory_daemon)
    trigger_watcher.start()
    time.sleep(20)
    trigger_watcher.stop()
