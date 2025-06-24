# This file is deprecated and should not be used by the main system.
# All hooks, imports, and references to this legacy StateManager should be removed from the main codebase.

import time
import threading

class StateManager:
    def __init__(self, lore_manager, memory_manager, mode_manager):
        self.lore_manager = lore_manager
        self.memory_manager = memory_manager
        self.mode_manager = mode_manager
        self.running = False
        self.lore_check_interval = 5  # seconds
        self.memory_archive_interval = 60  # seconds
        self.mode_check_interval = 10  # seconds

    def run(self):
        self.running = True
        last_lore_check = 0
        last_memory_archive = 0
        last_mode_check = 0

        while self.running:
            now = time.time()

            # Lore watcher trigger
            if now - last_lore_check > self.lore_check_interval:
                if self.lore_manager.reload_if_updated():
                    print("[StateManager] Lore updated and reloaded — mood shifts incoming.")
                last_lore_check = now

            # Periodic memory archive
            if now - last_memory_archive > self.memory_archive_interval:
                self.memory_manager.archive_memory()
                print("[StateManager] Memory archived.")
                last_memory_archive = now

            # Mode fuzzy scheduler check
            if now - last_mode_check > self.mode_check_interval:
                self.mode_manager.check_modes()
                print("[StateManager] Mode scheduler tick.")
                last_mode_check = now

            time.sleep(1)  # Zen CPU sleep

    def stop(self):
        self.running = False


# To run in a background thread:
def start_state_manager(state_manager):
    thread = threading.Thread(target=state_manager.run, daemon=True)
    thread.start()
    return thread

