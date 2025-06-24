import os
import sys
import threading
import time
from queue import Queue
from queue import Empty # Assuming this was added in a previous step

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

try:
    from brain.daemons import folder_watcher
    print("[run_daemons.py] Successfully imported folder_watcher.")
except ImportError as e:
    print(f"[run_daemons.py] Error importing folder_watcher: {e}")
    folder_watcher = None

try:
    from brain.daemons.FileProcessorDaemon import FileProcessorDaemon
    print("[run_daemons.py] Successfully imported FileProcessorDaemon.")
except ImportError as e:
    print(f"[run_daemons.py] Error importing FileProcessorDaemon: {e}")
    sys.exit(1)

# --- Imports for other daemons ---
# from brain.daemons.heartbeat_daemon import HeartbeatDaemon # Legacy/Deprecated - do not use
from brain.daemons.memory_daemon import MemoryDaemon     # Uncommented

running_daemons = []
daemon_threads = []
folder_watcher_shutdown_event_for_thread = threading.Event() # For programmatic stop

def start_all_daemons(memory_injector, state_manager=None, api_gateway_instance=None, gui_instance=None):
    """
    Initializes and starts all core daemons for Judy's system.
    Args:
        memory_injector: Callback for injecting file content into memory.
        state_manager: Optional StateManager instance.
        api_gateway_instance: Optional API Gateway instance.
        gui_instance: Optional GUI instance.
    """
    print("[run_daemons.py] Attempting to start all daemons...")

    if state_manager:
        print(f"[run_daemons.py] StateManager instance received: {state_manager}")
    else:
        print("[run_daemons.py] StateManager instance not provided.")
    if api_gateway_instance:
        print(f"[run_daemons.py] ApiGateway instance received: {api_gateway_instance}")
    else:
        print("[run_daemons.py] ApiGateway instance not provided.")
    if gui_instance:
        print(f"[run_daemons.py] GUI instance received: {gui_instance}")
    else:
        print("[run_daemons.py] GUI instance not provided.")

    file_processing_queue = Queue()
    file_processor = FileProcessorDaemon(
        memory_injector=memory_injector,
        file_queue=file_processing_queue
    )
    running_daemons.append(file_processor)
    file_processor.start()
    print("[run_daemons.py] FileProcessorDaemon started.")

    if folder_watcher:
        stixx_data_folder = os.path.join(project_root, "stixx_data_dropzone")
        if not os.path.exists(stixx_data_folder):
            try:
                os.makedirs(stixx_data_folder)
                print(f"[run_daemons.py] Created Stixx data drop folder: {stixx_data_folder}")
            except Exception as e:
                print(f"[run_daemons.py] Error creating Stixx data drop folder {stixx_data_folder}: {e}")

        try:
            # Pass the shutdown event to the folder watcher
            folder_watcher_thread = threading.Thread(
                target=folder_watcher.start_folder_watcher,
                args=(stixx_data_folder, file_processing_queue, folder_watcher_shutdown_event_for_thread),
                daemon=True, # Daemon True is okay if we have a clean shutdown signal
                name="FolderWatcherThread"
            )
            daemon_threads.append(folder_watcher_thread)
            folder_watcher_thread.start()
            print(f"[run_daemons.py] FolderWatcher thread started for {stixx_data_folder}.")
        except Exception as e:
            print(f"[run_daemons.py] Error starting FolderWatcher thread: {e}")
    else:
        print("[run_daemons.py] FolderWatcher not available, skipping startup.")

    # --- Start Heartbeat Daemon ---
    # HeartbeatDaemon is legacy/deprecated and should not be started
    # try:
    #     heartbeat_daemon = HeartbeatDaemon(config={}) # Assuming a dummy config for now
    #     running_daemons.append(heartbeat_daemon)
    #     # heartbeat_daemon.start() # OLD - BLOCKS
    #     heartbeat_thread = threading.Thread(target=heartbeat_daemon.start, daemon=True, name="HeartbeatDaemonThread")
    #     daemon_threads.append(heartbeat_thread)
    #     heartbeat_thread.start()
    #     print("[run_daemons.py] HeartbeatDaemon thread started.")
    # except NameError: # If HeartbeatDaemon class is not defined due to missing file
    #     print("[run_daemons.py] HeartbeatDaemon class not found. Cannot start.")
    # except Exception as e:
    #     print(f"[run_daemons.py] Error starting HeartbeatDaemon: {e}")


    # --- Start Memory Daemon ---
    try:
        mem_file = os.path.join(project_root, "runtime", "memory.json")
        arch_file = os.path.join(project_root, "runtime", "memory_archive.json")
        # Ensure runtime directory exists
        os.makedirs(os.path.join(project_root, "runtime"), exist_ok=True)
        memory_daemon = MemoryDaemon(memory_file=mem_file, archive_file=arch_file)
        running_daemons.append(memory_daemon)
        memory_daemon.start() # Assuming MemoryDaemon's start() is non-blocking or manages its own thread
        print("[run_daemons.py] MemoryDaemon started.")
    except NameError: # If MemoryDaemon class is not defined due to missing file
        print("[run_daemons.py] MemoryDaemon class not found. Cannot start.")
    except Exception as e:
        print(f"[run_daemons.py] Error starting MemoryDaemon: {e}")

    print("[run_daemons.py] Finished attempting to start all daemons.")


def stop_all_daemons():
    print("[run_daemons.py] Attempting to stop all daemons...")

    # Signal the folder watcher to shut down
    if folder_watcher:
        print("[run_daemons.py] Signaling FolderWatcher to stop...")
        folder_watcher_shutdown_event_for_thread.set()

    for daemon_instance in running_daemons:
        try:
            print(f"[run_daemons.py] Signaling {daemon_instance.__class__.__name__} to stop.")
            daemon_instance.stop()
        except Exception as e:
            print(f"[run_daemons.py] Error stopping {daemon_instance.__class__.__name__}: {e}")

    print("[run_daemons.py] Joining daemon threads...")
    for thread in daemon_threads:
        if thread.is_alive():
            print(f"[run_daemons.py] Joining thread {thread.name}...")
            thread.join(timeout=5) # Wait up to 5 seconds
            if thread.is_alive():
                print(f"[run_daemons.py] Thread {thread.name} did not terminate after timeout.")

    # Note: FileProcessorDaemon's internal thread is joined by its own stop() method.
    # HeartbeatDaemon's thread (if correctly implemented with self.running) should also join.
    # MemoryDaemon's thread (if it has one started by its start() method) should be joined by its stop().

    daemon_threads.clear()
    running_daemons.clear()
    print("[run_daemons.py] Note: FolderWatcherThread is a daemon thread and is not explicitly stopped by this function. It will exit when the main program exits.") # This message might be redundant if event works.
    print("[run_daemons.py] Finished stopping all daemons.")

if __name__ == '__main__':
    print("[run_daemons.py] Running directly as a script (for testing).")
    def dummy_memory_injector_test(content):
         print(f"[DummyMemoryInjectorForTest] Received content: {content[:50]}...")

    start_all_daemons(
        memory_injector=dummy_memory_injector_test,
        state_manager="TestSM_Placeholder",
        api_gateway_instance="TestAPI_Placeholder",
        gui_instance="TestGUI_Placeholder"
    )
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[run_daemons.py] KeyboardInterrupt in test mode. Stopping daemons...")
        stop_all_daemons()
        print("[run_daemons.py] Script finished.")
