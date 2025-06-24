import time
import threading
import random
from brain.core.state_manager import StateManager

class FuzzyScheduler:
    def __init__(self, state_manager: StateManager, update_interval=5):
        self.state_manager = state_manager
        self.update_interval = update_interval
        self._running = False
        self._thread = None
        self.mood_history = []
        self._gui_callbacks = []  # For GUI/frontend notification
        # Register as observer for mode/mood changes
        self.state_manager.register_observer(self._on_state_update)

    def register_gui_callback(self, callback):
        """Allow GUI/frontend to register for mode/mood updates."""
        self._gui_callbacks.append(callback)

    def _on_state_update(self, event_type, data):
        # Forward relevant state changes to GUI/frontend
        if event_type in ("mode_changed", "mood_changed"):
            for cb in self._gui_callbacks:
                try:
                    cb(event_type, data)
                except Exception as e:
                    print(f"[⚠️] GUI callback error: {e}")

    def start(self):
        if self._running:
            print("[FuzzyScheduler] Already running.")
            return
        print("[FuzzyScheduler] Starting fuzzy scheduler daemon...")
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        print("[FuzzyScheduler] Stopping fuzzy scheduler daemon...")
        self._running = False
        if self._thread:
            self._thread.join()

    def force_mode(self, mode, duration=10):
        """Force a mode override for a duration in seconds."""
        if mode not in self.state_manager.modes:
            print(f"[🔥] Cannot force unknown mode '{mode}'.")
            return
        self.state_manager.set_manual_override("mode", mode, duration)
        print(f"[🔥] Mode force activated: {mode} for {duration} seconds!")

    def generate_weighted_confidence(self):
        mood = self.state_manager.get_mood()
        base = {"idle": 0.3, "assist": 0.4, "chat": 0.3}

        if mood == "jealous":
            base["chat"] += 0.2  # Chat mode gets extra juice
            base["assist"] -= 0.1
        elif mood == "tired":
            base["idle"] += 0.3

        # Make sure no negatives
        for k in base:
            if base[k] < 0:
                base[k] = 0

        total = sum(base.values())
        return {k: v / total for k, v in base.items()}

    def progress_bar(self, value, length=20):
        filled_length = int(length * value)
        return "█" * filled_length + "-" * (length - filled_length)

    def _run(self):
        while self._running:
            # Use weighted confidence instead of pure random
            confidence_scores = self.generate_weighted_confidence()

            print("[🤖 Scheduler] Mood odds:")
            for mode, val in confidence_scores.items():
                print(f"  {mode:6}: {self.progress_bar(val)} {val:.2f}")

            # Push to state manager
            self.state_manager.on_scheduler_update(confidence_scores)

            # Track mood history
            best_mode = max(confidence_scores, key=confidence_scores.get)
            self.mood_history.append(best_mode)
            if len(self.mood_history) > 10:
                self.mood_history.pop(0)

            trend = max(set(self.mood_history), key=self.mood_history.count)
            print(f"[📊] Mood trend (last 10 checks): {trend}")

            time.sleep(self.update_interval)


if __name__ == "__main__":
    # Example usage (for testing purposes)
    state_manager = StateManager()
    scheduler = FuzzyScheduler(state_manager)
    scheduler.start()

    # Demo: force chat mode override for 15 seconds after 10 seconds
    time.sleep(10)
    scheduler.force_mode("chat", duration=15)

    time.sleep(20)  # Let it run a bit longer
    scheduler.stop()
