import time
import os
from queue import Queue
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

class FileDropHandler(FileSystemEventHandler):
    def __init__(self, file_queue: Queue):
        self.file_queue = file_queue

    def on_created(self, event):
        """Called when a file or directory is created."""
        if not event.is_directory:
            print(f"[FileWatcher] New file detected: {event.src_path}")
            self.file_queue.put(event.src_path)

# Global or passed-in event to signal shutdown (as per instructions)
# However, it's better to pass it as an argument for clarity and testability.
# folder_watcher_shutdown_event = threading.Event() # This would be if it's global

def start_folder_watcher(folder_path: str, file_queue: Queue, shutdown_event: threading.Event): # MODIFIED
    """
    Starts a watchdog observer to monitor a folder for new files.

    Args:
        folder_path: The path to the folder to watch.
        file_queue: The queue to put new file paths into.
        shutdown_event: A threading.Event to signal when to stop.
    """
    event_handler = FileDropHandler(file_queue)
    observer = Observer()
    observer.schedule(event_handler, folder_path, recursive=False)
    observer.start()
    print(f"[FileWatcher] Watching folder: {folder_path}")
    try:
        while not shutdown_event.is_set(): # Check the event
            time.sleep(1) # Keep polling the event
    except Exception as e: # Keep general exception handling
        print(f"[FileWatcher] An error occurred in the observer: {e}")
    finally:
        print("[FileWatcher] Shutdown signal received or error occurred.")
        observer.stop()
        observer.join() # Wait for watchdog's own thread to stop
        print("[FileWatcher] Observer thread joined.")

class FolderWatcher:
    def __init__(self, folder_path: str, file_queue: Queue, shutdown_event=None):
        self.folder_path = folder_path
        self.file_queue = file_queue
        self.shutdown_event = shutdown_event or threading.Event()
        self._thread = None
        self._running = False

    def start(self):  # MODIFIED
        if self._running:
            print("[FolderWatcher] Already running.")
            return
        print(f"[FolderWatcher] Starting watcher on {self.folder_path}")
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        print("[Judy] Hello! I'm Judy, your AI assistant. How can I help you today?")  # Judy's greeting

    def stop(self):
        print("[FolderWatcher] Stopping watcher...")
        self._running = False
        self.shutdown_event.set()
        if self._thread:
            self._thread.join()
        print("[FolderWatcher] Watcher stopped.")

    def _run(self):
        event_handler = FileDropHandler(self.file_queue)
        observer = Observer()
        observer.schedule(event_handler, self.folder_path, recursive=False)
        observer.start()
        print(f"[FileWatcher] Watching folder: {self.folder_path}")
        try:
            while not self.shutdown_event.is_set() and self._running:
                time.sleep(1)
        except Exception as e:
            print(f"[FileWatcher] An error occurred in the observer: {e}")
        finally:
            print("[FileWatcher] Shutdown signal received or error occurred.")
            observer.stop()
            observer.join()
            print("[FileWatcher] Observer thread joined.")

if __name__ == '__main__':
    # Always run the watcher on stixx_data_dropzone when executed directly
    dummy_queue = Queue()
    watch_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../stixx_data_dropzone'))
    test_shutdown_event = threading.Event()

    # Create the folder if it doesn't exist
    if not os.path.exists(watch_folder):
        os.makedirs(watch_folder)
        print(f"Created stixx_data_dropzone: {watch_folder}")

    print(f"[FolderWatcher] Always running on {watch_folder}. Press Ctrl+C to stop.")

    watcher = FolderWatcher(watch_folder, dummy_queue, test_shutdown_event)
    watcher.start()

    try:
        while watcher._running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[FolderWatcher] KeyboardInterrupt. Stopping watcher...")
        watcher.stop()
        print("[FolderWatcher] Watcher stopped.")

    # Process any files that might have been dropped during the test
    while not dummy_queue.empty():
        file_path = dummy_queue.get()
        print(f"Processing from queue: {file_path}")
        dummy_queue.task_done()

    print("Test finished.")
