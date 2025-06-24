import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk # For avatar image
from gui.components.status_bar import StatusBar # May be removed later
from gui.components.settings_panel import SettingsPanel
from .typing_indicator import TypingIndicator  # Import the TypingIndicator
import os # For path joining

class JalenWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg="#0f0f1a", **kwargs) # Main background
        self.parent = parent
        self.configure(width=500, height=250) # Approximate cassette size
        self.pack_propagate(False) # Prevent children from resizing the main widget

        # LED Border Colors
        self.led_colors = {
            "calm": "#00FFFF",    # Teal
            "processing": "#007FFF", # Neon Blue
            "error": "#FF4500",   # Blood Orange
            "incoming": "#FF00FF", # Magenta
        }
        self.current_led_color = self.led_colors["calm"]

        # Outer frame for LED border effect
        self.led_border_frame = tk.Frame(self, bg=self.current_led_color, bd=3, relief="solid")
        self.led_border_frame.pack(fill="both", expand=True, padx=3, pady=3)

        # Inner content frame
        self.content_frame = tk.Frame(self.led_border_frame, bg="#0f0f1a") # Dark inner background
        self.content_frame.pack(fill="both", expand=True)
        self.content_frame.pack_propagate(False)


        # ———————————————————————————
        # 🔹 TOP BAR (within content_frame)
        # ———————————————————————————
        self.top_bar = tk.Frame(self.content_frame, bg="#0f0f1a")
        self.top_bar.pack(side="top", fill="x", pady=(5,0))

        # --- Avatar Display ---
        self.avatar_label = tk.Label(self.top_bar, bg="#0f0f1a")
        self.avatar_label.pack(side="left", padx=(5,5), pady=2)
        self.avatar_image = None # To hold the PhotoImage object
        self.load_avatar_image("assets/images/judy_idle.png", size=(40, 40)) # Load initial image

        self.jalen_label = tk.Label(
            self.top_bar,
            text="J.A.L.E.N",
            font=("Courier New", 14, "bold"), # Placeholder font
            fg="#FF00CC", # Neon Pink for title
            bg="#0f0f1a"
        )
        self.jalen_label.pack(side="left", expand=True, fill="x") # Centered by expanding

        self.settings_button = ttk.Button(
            self.top_bar,
            text="⚙️",
            command=self.toggle_settings,
            style="Toolbutton" # Use a less obtrusive style if available or create one
        )
        self.settings_button.pack(side="right", padx=(0, 5), pady=(0,0))

        # Remove old status bar and title, they are replaced by new top_bar and LED border
        # self.status_bar = StatusBar(self)
        # self.status_bar.pack(side="top", fill="x", pady=(0, 2))
        # title = tk.Label(...)
        # title.pack(...)


        # ———————————————————————————
        # 🔹 MAIN CONTENT AREA (within content_frame)
        # ———————————————————————————
        self.chat_display = tk.Text(
            self.content_frame, # Now child of content_frame
            height=10, # Will adjust dynamically or be part of scrollable area
            bg="#1a1a2e", # Darker blue/purple for chat
            fg="#E6E6FA", # Light lavender text
            insertbackground="#FF00CC", # Neon pink cursor
            bd=0,
            relief="flat",
            font=("Consolas", 10), # Slightly smaller font for chat
            wrap="word"
        )
        self.chat_display.pack(padx=10, pady=(5,5), fill="both", expand=True)

        # ———————————————————————————
        # 🔹 TYPING INDICATOR (within content_frame)
        # ———————————————————————————
        self.typing_indicator = TypingIndicator(self.content_frame, bg="#0f0f1a")
        # Not packed initially, will be packed below chat_display when active

        # ———————————————————————————
        # 🔹 SETTINGS PANEL (managed by toggle_settings)
        # ———————————————————————————
        self.settings_panel = SettingsPanel(self) # Remains child of main JalenWidget for overlay
        # Old toggle button is removed, settings are now toggled by top_bar icon
        # toggle_btn = ttk.Button(...)
        # toggle_btn.pack(...)

    def _update_led_border(self, color_name):
        """Updates the LED border color."""
        if color_name in self.led_colors:
            self.current_led_color = self.led_colors[color_name]
            self.led_border_frame.config(bg=self.current_led_color)
        else:
            print(f"[JalenWidget] Unknown LED color: {color_name}")

    def update_mode(self, mode):
        """Update Jalen’s mode — changes LED border + optional effects."""
        # self.status_bar.update_status(mode) # Old status bar
        if mode == "processing":
            self._update_led_border("processing")
        elif mode == "error":
            self._update_led_border("error")
            self._flicker_led("error", times=3) # Flicker for error
        elif mode == "incoming":
            self._update_led_border("incoming")
            self._pulse_led("incoming", pulses=2) # Pulse for incoming
        else: # Default to calm
            self._update_led_border("calm")

        if mode == "alert":
            self._shake_warning()
            self._log_message("[JALEN] SYSTEM ALERT ACTIVE")

    def _flicker_led(self, color_name, times=3, interval_ms=75):
        """Flickers the LED border a number of times."""
        original_color = self.led_border_frame.cget("bg")
        target_color = self.led_colors.get(color_name, original_color)

        def flicker_action(count):
            if count < times * 2:
                current_bg = self.led_border_frame.cget("bg")
                next_color = original_color if current_bg == target_color else target_color
                self.led_border_frame.config(bg=next_color)
                self.after(interval_ms, lambda: flicker_action(count + 1))
            else:
                # Ensure it ends on the target_color or calm after flickering
                self._update_led_border(color_name if color_name != "error" else "calm")


        flicker_action(0)

    def _pulse_led(self, color_name, pulses=2, interval_ms=200):
        """Pulses the LED border color."""
        original_color = self.led_colors["calm"] # Assume calm is the base
        target_color = self.led_colors.get(color_name, original_color)

        def pulse_action(count, is_bright):
            if count < pulses * 2:
                next_color = target_color if is_bright else original_color
                self.led_border_frame.config(bg=next_color)
                self.after(interval_ms, lambda: pulse_action(count + 1, not is_bright))
            else:
                # Return to calm or the specified color after pulsing
                self._update_led_border(color_name if color_name != "incoming" else "calm")

        pulse_action(0, True)


    def _log_message(self, msg):
        """Internal method to insert a message into the chat log."""
        self.chat_display.insert("end", f"{msg}\n")
        self.chat_display.see("end")

    def toggle_settings(self):
        """Show/hide the settings panel."""
        if self.settings_panel.is_shown:
            self.settings_panel.hide()
        else:
            self.settings_panel.show()

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
        self._update_led_border("processing") # Update LED to processing
        self.typing_indicator.pack(in_=self.content_frame, side="bottom", fill="x", pady=(0, 2))
        self.typing_indicator.start_typing()

    def hide_typing_indicator(self):
        """Hide the typing indicator and stop animation."""
        self.typing_indicator.stop_typing()
        self.typing_indicator.pack_forget()
        self._update_led_border("calm") # Return LED to calm

    # ———————————————————————————
    # 🔹 PULSE REGISTRATION PATCH
    # ———————————————————————————
    def register_pulse(self, pulse_coordinator):
        pulse_coordinator.register_observer(self.status_bar.handle_pulse_update) # This may need to change if status_bar is removed

    def load_avatar_image(self, image_path, size=(40,40)):
        """Loads and displays the avatar image."""
        if not os.path.exists(image_path):
            print(f"[JalenWidget] Avatar image not found at {image_path}")
            # Create a placeholder if image is missing
            img = Image.new('RGB', size, color = '#FF00CC') # Bright pink placeholder
            self.avatar_image = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=self.avatar_image)
            self.avatar_label.image = self.avatar_image # Keep a reference!
            return

        try:
            img = Image.open(image_path)
            img = img.resize(size, Image.Resampling.LANCZOS)
            self.avatar_image = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=self.avatar_image)
            # Keep a reference to prevent garbage collection!
            self.avatar_label.image = self.avatar_image
        except Exception as e:
            print(f"[JalenWidget] Error loading avatar image {image_path}: {e}")
            # Create a placeholder if image loading fails
            img = Image.new('RGB', size, color = '#FF4500') # Orange placeholder for error
            self.avatar_image = ImageTk.PhotoImage(img)
            self.avatar_label.config(image=self.avatar_image)
            self.avatar_label.image = self.avatar_image # Keep a reference!


    def show_avatar(self, image_path=None, temporary=False):
        """Shows the avatar. Optionally loads a new image."""
        if image_path:
            self.load_avatar_image(image_path)
        self.avatar_label.pack(side="left", padx=(5,5), pady=2) # Ensure it's visible

        if temporary:
            # Hide after a delay (e.g., 3 seconds for a reply)
            self.after(3000, self.hide_avatar)


    def hide_avatar(self):
        """Hides the avatar."""
        self.avatar_label.pack_forget()
