import sys
import os
import time
import json
import signal
from queue import Queue
from brain.daemons.memory_daemon import MemoryDaemon
from brain.daemons.lore_trigger_watcher import LoreTriggerWatcher
from brain.agents.jalen_agent import JalenAgent
from brain.core.state_manager import StateManager
from brain.daemons.MessageHandlerDaemon import MessageHandlerDaemon
from brain.daemons.PulseCoordinator import PulseCoordinator
from runners import run_daemons
from gui.widgets import status_bar  # 👈 so PulseCoordinator can hit the GUI pulse handler
import threading
import tkinter as tk
from tkinter import scrolledtext

CONFIG_PATH = "config/config.yaml"
MEMORY_PATH = "runtime/memory.json"
ARCHIVE_PATH = "chronicles/memory_archive.json"
PID_FILE = "app.pid"

def load_config(path):
    if not os.path.exists(path):
        print(f"[Config] Config file not found: {path}")
        return {}
    if path.endswith('.json'):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Config] Error loading JSON config: {e}")
            return {}
    else:
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML config files. Install with 'pip install pyyaml'.")
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"[Config] Error loading YAML config: {e}")
            return {}

def your_actual_memory_injector(content: str):
    print(f"[MemoryInjector] Snippet: {content[:100]}...")
    pass

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

def launch_test_gui(agent):
    import tkinter as tk
    from gui.components.jalen_widget import JalenWidget
    
    def on_user_input(user_message):
        """Handle user input and get agent response"""
        if hasattr(agent, 'generate_response'):
            # Show typing indicator
            jalen_widget.show_typing_indicator()
            
            # Generate response asynchronously
            def handle_response(response):
                # Schedule GUI updates to run in the main Tkinter thread
                jalen_widget.after(0, lambda: jalen_widget.hide_typing_indicator())
                jalen_widget.after(0, lambda: jalen_widget.show_avatar(temporary=True)) # Show avatar with Judy's message
                jalen_widget.after(0, lambda: jalen_widget._log_message(f"You: {user_message}"))
                jalen_widget.after(0, lambda: jalen_widget._log_message(f"Judy🌹: {response}"))
            
            # Hide avatar before showing typing indicator and sending new message
            # These calls are made from the main thread (Tkinter event handlers), so they are safe.
            jalen_widget.hide_avatar()
            agent.generate_response_async(user_message, handle_response)
        else:
            jalen_widget._log_message(f"You: {user_message}")
            jalen_widget._log_message("Judy🌹: [Agent not ready]")
    
    # Create main window
    root = tk.Tk()
    root.title("J.A.L.E.N - Judy's Advanced Interface")
    root.geometry("800x600")
    root.configure(bg="#0f0f1a")
    
    # Use your sophisticated JalenWidget
    jalen_widget = JalenWidget(root)
    jalen_widget.pack(fill="both", expand=True)
    
    # Add input handling (you'll need to add this method to JalenWidget)
    # For now, let's add a simple input method
    input_frame = tk.Frame(root, bg="#0f0f1a")
    input_frame.pack(fill="x", padx=10, pady=5)
    
    input_box = tk.Entry(input_frame, bg="#1a1a2e", fg="#E6E6FA", insertbackground="#FF00CC")
    input_box.pack(side="left", fill="x", expand=True, padx=(0, 5))
    
    def send_message(event=None):
        message = input_box.get().strip()
        if message:
            input_box.delete(0, tk.END)
            on_user_input(message)
    
    input_box.bind('<Return>', send_message)
    
    send_btn = tk.Button(input_frame, text="Send", command=send_message, 
                        bg="#FF00CC", fg="white")
    send_btn.pack(side="right")
    
    # Initial greeting
    jalen_widget._log_message("Judy🌹: " + agent.greet())
    input_box.focus()
    
    root.mainloop()

def main():
    write_pid()
    config = load_config(CONFIG_PATH)
    print("[✅] Config loaded:", config)

    # Extract model settings
    model_settings = config.get("model_settings", {})
    model_path_config = model_settings.get("model_path") # Will be None if not set
    # Default n_gpu_layers to 0 (CPU) if not specified or if section is missing.
    # The TextGeneration class itself also has a default.
    n_gpu_layers_config = model_settings.get("n_gpu_layers", 0)

    # Extract logging settings
    logging_settings = config.get("logging_settings", {})
    log_prompts_config = logging_settings.get("log_prompts", False)

    state_file = config.get("state_file", "runtime/state.json")
    state_manager = StateManager(memory_file=state_file)

    memory_daemon = MemoryDaemon(memory_file=MEMORY_PATH, archive_file=ARCHIVE_PATH)
    memory_daemon.state_manager = state_manager
    # memory_daemon.start() # Ensure memory daemon is started if it has a start method

    # --- Temporarily disable non-essential daemons ---
    # lore_trigger_watcher = LoreTriggerWatcher(state_manager, memory_daemon)
    # lore_trigger_watcher.start() # If it has a start method

    # message_queue = Queue()
    # def dummy_command_router(cmd):
    #     print(f"[CommandRouter] {cmd}")
    # message_handler = MessageHandlerDaemon(dummy_command_router, message_queue, state_manager=state_manager)
    # message_handler.start()

    # pulse_coordinator = PulseCoordinator(
    #     state_manager=state_manager,
    #     memory_daemon=memory_daemon,
    #     daemons={
    #         # "LoreTriggerWatcher": lore_trigger_watcher, # Disabled
    #         # "MessageHandler": message_handler # Disabled
    #     },
    #     interval=30 # Increased interval if kept, or disable
    # )
    # pulse_coordinator.register_observer(status_bar.handle_pulse_update) # GUI dependent
    # pulse_coordinator.start()
    # --- End of disabled daemons ---

    print("[⚠️] LoreTriggerWatcher, MessageHandlerDaemon, and PulseCoordinator are temporarily disabled for simplification.")

    agent = JalenAgent(memory_daemon,
                       state_manager,
                       model_path=model_path_config,
                       n_gpu_layers=n_gpu_layers_config,
                       log_prompts=log_prompts_config)

    # Determine mode: CLI or GUI
    run_gui = False
    if len(sys.argv) > 1 and sys.argv[-1] == "--gui":
        run_gui = True
    
    if run_gui:
        print("[🚀] Launching GUI mode...")
        gui_thread = threading.Thread(target=launch_test_gui, args=(agent,), daemon=True)
        gui_thread.start()
    else:
        print("[🚀] Launching CLI mode...")
        agent.start_chatbox() # Enable CLI chatbox

    print("[🌹] Judy’s simplified system is live. Focus on core chat.")

    try:
        # If running CLI, the main loop is effectively in agent._chat_loop()
        # If running GUI, this loop keeps the main thread alive for daemon threads
        # and to catch KeyboardInterrupt.
        while True:
            if run_gui and not gui_thread.is_alive():
                print("[System] GUI thread has ended. Exiting.")
                break
            if not run_gui and agent._input_thread and not agent._input_thread.is_alive():
                 print("[System] CLI chat thread has ended. Exiting.")
                 break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[System] Shutdown requested.")
    finally:
        agent.stop()
        memory_daemon.stop() # Ensure it has a stop method and is called
        # lore_trigger_watcher.stop() # If it was started and has a stop method
        # message_handler.stop() # If it was started and has a stop method
        # pulse_coordinator.stop() # If it was started and has a stop method
        remove_pid()
        print("[System] Cleanup complete. Exiting.")

if __name__ == "__main__":
    # Simplified argument parsing: `python main.py start` or `python main.py start --gui`
    if len(sys.argv) >= 2 and sys.argv[1] == "start":
        main() # main() will check for --gui itself
    elif len(sys.argv) == 2 and sys.argv[1] == "stop":
        pid = read_pid()
        if pid:
            try:
                # Windows: use os.kill with signal.CTRL_BREAK_EVENT
                if os.name == 'nt':
                    import ctypes
                    handle = ctypes.windll.kernel32.OpenProcess(1, 0, pid)
                    ctypes.windll.kernel32.GenerateConsoleCtrlEvent(1, pid)
                    ctypes.windll.kernel32.CloseHandle(handle)
                else:
                    os.kill(pid, signal.SIGINT)
                print(f"[System] Sent stop signal to process {pid}.")
                remove_pid()
            except Exception as e:
                print(f"[System] Could not stop process {pid}: {e}")
        else:
            print("[System] No running app found.")
    else:
        print("Usage: python main.py [start|stop]")
