import tkinter as tk
from tkinter import ttk
from gui.components.status_bar import StatusBar
from gui.components.settings_panel import SettingsPanel
from .typing_indicator import TypingIndicator  # Import the TypingIndicator

class JalenWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#0f0f1a", bd=2, relief="flat", **kwargs)
        self.parent = parent

        # ———————————————————————————
        # 🔹 STATUS BAR
        # ———————————————————————————
        self.status_bar = StatusBar(self)
        self.status_bar.pack(side="top", fill="x", pady=(0, 2))

        # ———————————————————————————
        # 🔹 TOP TITLE
        # ———————————————————————————
        title = tk.Label(
            self,
            text="J.A.L.E.N",
            font=("Courier New", 16, "bold"),
            fg="#FF00CC",
            bg="#0f0f1a"
        )
        title.pack(pady=(10, 4))

        # ———————————————————————————
        # 🔹 MAIN CONTENT AREA
        # ———————————————————————————
        self.chat_display = tk.Text(
            self,
            height=10,
            bg="#1a1a2e",
            fg="#E6E6FA",
            insertbackground="#FF00CC",
            bd=0,
            relief="flat",
            font=("Consolas", 11),
            wrap="word"
        )
        self.chat_display.pack(padx=10, pady=6, fill="both", expand=True)

        # ———————————————————————————
        # 🔹 TYPING INDICATOR
        # ———————————————————————————
        self.typing_indicator = TypingIndicator(self, bg="#0f0f1a")
        # Not packed initially

        # ———————————————————————————
        # 🔹 SETTINGS TOGGLE
        # ———————————————————————————
        self.settings_panel = SettingsPanel(self)

        toggle_btn = ttk.Button(
            self,
            text="⚙️ Settings",
            command=self.toggle_settings
        )
        toggle_btn.pack(pady=(2, 6))

    def update_mode(self, mode):
        """Update Jalen’s mode — changes status bar + optional effects."""
        self.status_bar.update_status(mode)
        if mode == "alert":
            self._shake_warning()
            self._log_message("[JALEN] SYSTEM ALERT ACTIVE")

    def _log_message(self, msg):
        """Internal method to insert a message into the chat log."""
        self.chat_display.insert("end", f"{msg}\n")
        self.chat_display.see("end")

    def toggle_settings(self):
        """Show/hide the settings panel."""
        if not self.settings_panel.winfo_ismapped():
            self.settings_panel.pack(side="bottom", fill="x", padx=4, pady=4)
        else:
            self.settings_panel.pack_forget()

    def _shake_warning(self):
        """Optional animation when status is alert — little ghost rider glitch pulse."""
        def shake(count=0):
            if count >= 6: return
            offset = (-2 if count % 2 == 0 else 2)
            self.place_configure(x=self.winfo_x() + offset)
            self.after(40, lambda: shake(count + 1))
        if hasattr(self, 'place_configure'):
            shake()

    def show_typing_indicator(self):
        """Show the typing indicator and start animation."""
        self.typing_indicator.pack(fill="x", pady=(2, 6))
        self.typing_indicator.start_typing()

    def hide_typing_indicator(self):
        """Hide the typing indicator and stop animation."""
        self.typing_indicator.stop_typing()
        self.typing_indicator.pack_forget()

    # ———————————————————————————
    # 🔹 PULSE REGISTRATION PATCH
    # ———————————————————————————
    def register_pulse(self, pulse_coordinator):
        pulse_coordinator.register_observer(self.status_bar.handle_pulse_update)
