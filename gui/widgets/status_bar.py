# gui/widgets/status_bar.py

from rich import print  # or your actual GUI framework imports if different

class StatusBar:
    def __init__(self):
        self.last_pulse = {}

    def update_pulse(self, pulse_data):
        self.last_pulse = pulse_data
        self.display_status()

    def display_status(self):
        mood = self.last_pulse.get("mood", "unknown")
        mode = self.last_pulse.get("mode", "unknown")
        scene = self.last_pulse.get("scene", "unknown")
        memory_count = self.last_pulse.get("memory_count", 0)
        daemons = self.last_pulse.get("daemons", {})

        print(f"[🩸 GUI PULSE] Mood: {mood} | Mode: {mode} | Scene: {scene} | Memories: {memory_count}")
        for name, status in daemons.items():
            print(f"[👾] {name}: {status}")

# Global instance for easy access if needed
status_bar_widget = StatusBar()

# This is the observer callback PulseCoordinator will call
def handle_pulse_update(event_type, data):
    if event_type == "pulse":
        status_bar_widget.update_pulse(data)
