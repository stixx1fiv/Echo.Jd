import threading
import time

class NotifierDaemon:
    """
    Observes events from FileProcessor and MessageHandler,
    triggers Judy's personality responses and UI notifications.
    """

    def __init__(self):
        self._running = False
        self.event_queue = []
        self.lock = threading.Lock()
        self.worker_thread = threading.Thread(target=self._notify_loop, daemon=True)

    def start(self):
        self._running = True
        self.worker_thread.start()
        print("[NotifierDaemon] Started.")

    def stop(self):
        self._running = False
        self.worker_thread.join()
        print("[NotifierDaemon] Stopped.")

    def queue_event(self, event_type, content=None):
        with self.lock:
            self.event_queue.append((event_type, content))

    def _notify_loop(self):
        while self._running:
            event = None
            with self.lock:
                if self.event_queue:
                    event = self.event_queue.pop(0)
            if event:
                self._handle_event(event)
            else:
                time.sleep(0.5)

    def _handle_event(self, event):
        event_type, content = event
        if event_type == "file_processed":
            print(f"[NotifierDaemon] Judy quips: 'Fresh data just hit my circuits!'")
        elif event_type == "message_processed":
            print(f"[NotifierDaemon] Judy says: 'Got your message loud and clear.'")
        else:
            print(f"[NotifierDaemon] Judy is silent on unknown event '{event_type}'.")
