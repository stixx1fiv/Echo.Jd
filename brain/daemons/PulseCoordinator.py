import threading
import time

class PulseCoordinator:
    """
    Judy's pulse generator. Broadcasts mood, mode, scene, memory count, and daemon health to whoever’s listening.
    """
    def __init__(self, state_manager, memory_daemon, daemons=None, interval=5):
        self.state_manager = state_manager
        self.memory_daemon = memory_daemon
        self.daemons = daemons or {}  # dict of {name: daemon_instance}
        self.interval = interval
        self._stop_event = threading.Event()
        self._observers = []

    def register_observer(self, callback):
        """Subscribe a callback for pulse updates."""
        self._observers.append(callback)

    def notify_observers(self, event_type, data=None):
        for cb in self._observers:
            try:
                cb(event_type, data)
            except Exception as e:
                print(f"[⚠️] Pulse observer error: {e}")

    def start(self):
        self._stop_event.clear()
        threading.Thread(target=self._pulse_loop, daemon=True).start()
        print("[💓] PulseCoordinator started.")

    def stop(self):
        self._stop_event.set()
        print("[🛑] PulseCoordinator stopping.")

    def _handle_idle_behavior(self):
        """
        Idle cycle routines: decay mood, migrate memories, prune, rebuild context, etc.
        """
        try:
            self.state_manager.decay_mood()
        except Exception as e:
            print(f"[PulseCoordinator] Error in decay_mood: {e}")
        try:
            if hasattr(self.state_manager, 'migrate_long_term_memories_to_chroma'):
                self.state_manager.migrate_long_term_memories_to_chroma()
        except Exception as e:
            print(f"[PulseCoordinator] Error in migrate_long_term_memories_to_chroma: {e}")
        try:
            if self.state_manager.is_context_stale():
                self.state_manager.rebuild_prompt_context()
                self.state_manager.clear_context_stale()
        except Exception as e:
            print(f"[PulseCoordinator] Error in context staleness handling: {e}")

    def _context_stale(self):
        return self.state_manager.is_context_stale()

    def _pulse_loop(self):
        while not self._stop_event.is_set():
            try:
                pulse_data = self.collect_status()
                self.notify_observers("pulse", pulse_data)
                if self.state_manager.get_mode() == "idle":
                    self._handle_idle_behavior()
                print(f"[💥] Pulse fired: {pulse_data}")
            except Exception as e:
                print(f"[⚠️] Pulse error: {e}")
            time.sleep(self.interval)

    def collect_status(self):
        """Collect status from key components."""
        status_report = {
            "mood": self.state_manager.get_mood(),
            "mode": self.state_manager.get_mode(),
            "scene": self.state_manager.get_scene(),
            "memory_count": len(self.state_manager.get_memories("short")),
            "daemons": {}
        }
        for name, daemon in self.daemons.items():
            status_report["daemons"][name] = "alive" if getattr(daemon, "is_alive", lambda: False)() else "dead"
        return status_report
