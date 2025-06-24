import threading
import time

class SceneGlitchMonitor:
    def __init__(self, memory_daemon, config):
        self.memory_daemon = memory_daemon
        self.config = config
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()
        print("[👁️] SceneGlitchMonitor started.")

    def run(self):
        check_interval = self.config.get("scene_glitch_check_interval", 15)
        while self.running:
            self.scan_for_glitches()
            time.sleep(check_interval)

    def scan_for_glitches(self):
        current_scene = self.memory_daemon.get_memory("active_scene")
        if current_scene and "glitch" in current_scene.lower():
            print(f"[⚠️] Glitch detected in scene: {current_scene}")
            self.memory_daemon.add_history_event(f"Scene glitch event in {current_scene}")
            # You could trigger other responses here — notify agents, adjust mood, etc.

    def stop(self):
        self.running = False
        print("[🔻] SceneGlitchMonitor stopped.")
