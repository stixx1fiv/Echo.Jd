class SentinelAgent:
    def __init__(self, config_loader=None):
        self.config = config_loader
        self.silent_mode = config_loader.get("silent_mode", False) if config_loader else False
        self.heartbeat = None
        if not self.silent_mode:
            print("[👁️] SentinelAgent initialized — watching the gates, keeping the pulse.")

    def bind_heartbeat(self, heartbeat):
        self.heartbeat = heartbeat
        self.heartbeat.subscribe(self.on_heartbeat)
        if not self.silent_mode:
            print("[👁️] Sentinel bound to heartbeat.")

    def on_heartbeat(self):
        if not self.silent_mode:
            print("[👁️] Sentinel heartbeat check-in.")

    def run(self, message=None):
        if message:
            print(f"[👁️] Sentinel received message: {message}")
            # Future: handle system monitoring or alerts
        else:
            print("[👁️] Sentinel is on watch duty. Nothing shady… yet.")
