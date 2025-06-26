import sys
import os
import time
import json
import signal
from queue import Queue
from brain.daemons.memory_daemon import MemoryDaemon
from brain.daemons.lore_trigger_watcher import LoreTriggerWatcher
from brain.core.state_manager import StateManager
from brain.daemons.MessageHandlerDaemon import MessageHandlerDaemon
from brain.daemons.PulseCoordinator import PulseCoordinator
# from gui.widgets import status_bar  # Not needed for headless
# from brain.agents.jalen_agent import JalenAgent
import threading

CONFIG_PATH = "config/config.yaml"
MEMORY_PATH = "runtime/memory.json"
ARCHIVE_PATH = "chronicles/memory_archive.json"
PID_FILE = "app.pid"

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def read_pid():
    if not os.path.exists(PID_FILE):
        return None
    with open(PID_FILE, "r") as f:
        return int(f.read().strip())

def remove_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

def load_config(path):
    if not os.path.exists(path):
        return {}
    try:
        import yaml
        with open(path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def main():
    write_pid()
    config = load_config(CONFIG_PATH)
    print("[🌿] JudyLite starting up...")

    model_settings = config.get("model_settings", {})
    state_file = config.get("state_file", "runtime/state.json")
    state_manager = StateManager(memory_file=state_file)

    memory_daemon = MemoryDaemon(memory_file=MEMORY_PATH, archive_file=ARCHIVE_PATH)
    memory_daemon.state_manager = state_manager

    lore_trigger_watcher = LoreTriggerWatcher(state_manager, memory_daemon)
    message_queue = Queue()

    def dummy_command_router(cmd):
        print(f"[CommandRouter] {cmd}")

    message_handler = MessageHandlerDaemon(dummy_command_router, message_queue, state_manager=state_manager)
    message_handler.start()

    daemons = {
        "LoreTriggerWatcher": lore_trigger_watcher,
        "MessageHandler": message_handler
    }

    pulse_coordinator = PulseCoordinator(
        state_manager=state_manager,
        memory_daemon=memory_daemon,
        daemons=daemons,
        interval=5
    )
    # pulse_coordinator.register_observer(status_bar.handle_pulse_update)  # GUI pulse handler removed
    pulse_coordinator.start()

    print("[✨] Core daemons running. JudyLite is alive (and chill).")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[System] Shutdown requested.")
        memory_daemon.stop()
        lore_trigger_watcher.stop()
        message_handler.stop()
        pulse_coordinator.stop()
    finally:
        remove_pid()

if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "start":
        main()
    elif len(sys.argv) == 2 and sys.argv[1] == "stop":
        pid = read_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGINT)
                print(f"[System] Sent stop signal to process {pid}.")
                remove_pid()
            except Exception as e:
                print(f"[System] Could not stop process {pid}: {e}")
        else:
            print("[System] No running app found.")
    else:
        print("Usage: python judylite_main.py [start|stop]")
