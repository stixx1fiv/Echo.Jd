import threading
import time

class HeartbeatDaemon:
    def __init__(self, config_loader):
        self.interval = config_loader.get("scan_interval_minutes", 5) * 60
        self.silent_mode = config_loader.get("silent_mode", False)
        self._running = False
        self._thread = None
        self.subscribers = []

    def start(self):
        if self._running:
            if not self.silent_mode:
                print("[Heartbeat] Already running.")
            return
        if not self.silent_mode:
            print("[Heartbeat] Starting heartbeat daemon...")
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.silent_mode:
            print("[Heartbeat] Stopping heartbeat daemon...")
        self._running = False
        if self._thread:
            self._thread.join()
        if not self.silent_mode:
            print("[Heartbeat] Stopped.")

    def subscribe(self, callback):
        if callback not in self.subscribers:
            self.subscribers.append(callback)

    def _run(self):
        while self._running:
            time.sleep(self.interval)
            for callback in self.subscribers:
                try:
                    callback()
                except Exception as e:
                    print(f"[Heartbeat] Error in subscriber callback: {e}")
