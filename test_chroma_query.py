import threading
import time
import json
import os
from datetime import datetime
from brain.core.utils import log_helper

class MemoryDaemon(threading.Thread):
    def __init__(self, memory_path, archive_path, log_path):
        super().__init__(daemon=True)
        self.memory_path = memory_path
        self.archive_path = archive_path
        self.log_path = log_path
        self.running = True

    def run(self):
        log_helper.log_info("MemoryDaemon started.")
        while self.running:
            self.process_memories()
            time.sleep(5)  # adjust polling interval as needed

    def process_memories(self):
        if not os.path.exists(self.memory_path):
            log_helper.log_info("No memory file found.")
            return

        try:
            with open(self.memory_path, 'r') as file:
                memories = json.load(file)
        except Exception as e:
            log_helper.log_error(f"Failed to load memory file: {e}")
            return

        clean_memories = []
        for mem in memories:
            timestamp = mem.get("timestamp")
            if not self.validate_timestamp(timestamp):
                log_helper.log_warning(f"Invalid timestamp in memory: {timestamp}. Archiving.")
                self.archive_memory(mem)
                continue

            clean_memories.append(mem)

        with open(self.memory_path, 'w') as file:
            json.dump(clean_memories, file, indent=2)
        log_helper.log_info(f"Processed {len(clean_memories)} valid memories.")

    def validate_timestamp(self, timestamp):
        if not timestamp:
            return False
        try:
            # Accept string or datetime formats
            if isinstance(timestamp, str):
                datetime.fromisoformat(timestamp)
            elif isinstance(timestamp, datetime):
                pass
            else:
                return False
            return True
        except Exception as e:
            log_helper.log_warning(f"Timestamp parse error: {e}")
            return False

    def archive_memory(self, mem):
        if not os.path.exists(self.archive_path):
            os.makedirs(self.archive_path)

        archive_file = os.path.join(self.archive_path, f"archive_{datetime.now().strftime('%Y%m%d')}.json")
        existing = []
        if os.path.exists(archive_file):
            with open(archive_file, 'r') as file:
                try:
                    existing = json.load(file)
                except:
                    existing = []

        existing.append(mem)
        with open(archive_file, 'w') as file:
            json.dump(existing, file, indent=2)

        log_helper.log_info(f"Archived memory with invalid timestamp: {mem}")

    def stop(self):
        self.running = False
        log_helper.log_info("MemoryDaemon stopped.")
