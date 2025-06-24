import os
import threading
import time
from queue import Queue
from queue import Empty # Added import

class FileProcessorDaemon:
    """
    Watches a file dropzone queue, parses and indexes files,
    and feeds content into Judy's memory system.
    """

    def __init__(self, memory_injector, file_queue: Queue):
        """
        Args:
            memory_injector: callable that accepts parsed content and indexes it.
            file_queue: thread-safe queue with incoming file paths or file-like objects.
        """
        self.memory_injector = memory_injector
        self.file_queue = file_queue
        self._running = False
        self.worker_thread = threading.Thread(target=self._process_files_loop, daemon=True)

    def start(self):
        self._running = True
        self.worker_thread.start()
        print("[FileProcessorDaemon] Started.")

    def stop(self):
        print(f"[FileProcessorDaemon] Stopping. Signaling worker thread {self.worker_thread.name} to terminate.")
        self._running = False
        # Send sentinel to queue to unblock worker_thread if it's waiting on file_queue.get()
        self.file_queue.put(None)
        # It's good practice to check if the thread is alive before joining
        if self.worker_thread.is_alive():
            print(f"[FileProcessorDaemon] Attempting to join worker thread: {self.worker_thread.name}")
            self.worker_thread.join()
        print("[FileProcessorDaemon] Stopped.")

    def _process_files_loop(self):
        while self._running:
            file_item = None # Ensure file_item is defined for finally block if get() fails
            try:
                file_item = self.file_queue.get(timeout=1)  # waits for new files
                # Check if a sentinel None was put in the queue to signal shutdown cleanly
                if file_item is None:
                    print("[FileProcessorDaemon] Received None sentinel. Shutting down loop.") # ADD THIS
                    self._running = False # Signal loop to terminate
                    continue # Go to the top of the loop to check self._running

                print(f"[FileProcessorDaemon] Processing file: {file_item}")
                content = self._parse_file(file_item)
                if content: # Ensure content is not empty before injecting
                    self.memory_injector(content)
                    print(f"[FileProcessorDaemon] Injected content from {file_item} into memory.")
            except Empty: # Changed from queue.Empty
                # Timeout, no file in queue, just continue
                pass # No task to mark as done
            except Exception as e:
                # Handle other potential exceptions during processing
                print(f"[FileProcessorDaemon] Error during file processing for item {file_item}: {e}")
            finally:
                if file_item is not None: # Only call task_done if an item was actually retrieved and processed
                    self.file_queue.task_done()

    def _parse_file(self, file_item):
        """
        Parses the file content based on extension.
        Extend this for more file types.
        """
        # Ensure file_item is a string, as it might be None if queue was shut down with None
        if not isinstance(file_item, str):
            print(f"[FileProcessorDaemon] _parse_file received non-string item: {file_item}. Skipping.")
            return ""

        _, ext = os.path.splitext(file_item)
        ext = ext.lower()
        try:
            if ext in ['.txt', '.md']:
                with open(file_item, 'r', encoding='utf-8') as f:
                    return f.read()
            elif ext == '.pdf':
                # Placeholder: Implement PDF text extraction here
                # For now, let's ensure it's clear this is a placeholder
                print(f"[FileProcessorDaemon] PDF processing for {file_item} is a placeholder.")
                return f"[PDF content placeholder for {file_item}]"
            else:
                print(f"[FileProcessorDaemon] Unsupported file type: {ext} for file {file_item}. Skipping.")
                return ""
        except FileNotFoundError:
            print(f"[FileProcessorDaemon] File not found during parsing: {file_item}")
            return ""
        except Exception as e:
            print(f"[FileProcessorDaemon] Error parsing file {file_item}: {e}")
            return ""
