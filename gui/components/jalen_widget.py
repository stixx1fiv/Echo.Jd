import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from .typing_indicator import TypingIndicator
import os

class JalenWidget(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent

        # --- Load Background Image ---
        # NOTE: Assumes 'jalen_card_bg.png' is in 'assets/images/'
        self.widget_width = 400
        self.widget_height = 600
        self.configure(width=self.widget_width, height=self.widget_height)
        self.pack_propagate(False)

        try:
            bg_image_path = os.path.join("assets", "images", "jalen_card_bg.png")
            self.bg_image_pil = Image.open(bg_image_path)
            self.bg_image_pil = self.bg_image_pil.resize((self.widget_width, self.widget_height), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(self.bg_image_pil)
            
            self.background_label = tk.Label(self, image=self.bg_image)
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            # Fallback if the image isn't found
            self.configure(bg="#0f0f1a")
            self.background_label = tk.Label(self, text="BG Image not found.\nPlace 'jalen_card_bg.png' in assets/images.", bg="#0f0f1a", fg="white")
            self.background_label.pack(fill="both", expand=True)
            self.bg_image = None # Ensure it's None

        # --- Widget Content ---

        # J.A.L.E.N Title
        self.jalen_label = tk.Label(
            self,
            text="J.A.L.E.N",
            font=("Consolas", 24, "bold"),
            fg="#68d7e3", # Light teal/cyan
            bg="#210a2f"  # Background color from image
        )
        self.jalen_label.place(relx=0.5, y=55, anchor="center")

        # Avatar Display
        self.avatar_label = tk.Label(self, bg="#210a2f") # Match background color
        self.avatar_label.place(relx=0.5, y=170, anchor="center")
        self.avatar_image = None
        self.load_avatar_image("assets/images/judy_idle.png", size=(180, 180))

        # 615 JUDY Sub-label
        self.judy_label = tk.Label(
            self,
            text="615 JUDY",
            font=("Consolas", 18, "bold"),
            fg="#e368a4", # Neon Pink/Purple
            bg="#210a2f"
        )
        self.judy_label.place(relx=0.5, y=285, anchor="center")

        # Chat Display
        self.chat_display = tk.Text(
            self,
            height=10,
            bg="#000000", # Black background for the chat area
            fg="#E6E6FA", # Light lavender text
            insertbackground="#FF00CC",
            bd=0,
            relief="flat",
            font=("Consolas", 11),
            wrap="word",
            state=tk.DISABLED
        )
        self.chat_display.place(relx=0.5, y=415, anchor="center", width=340, height=190)

        # Input Frame
        self.input_frame = tk.Frame(self, bg="#0d0510") # Dark color from bottom of card
        self.input_frame.place(relx=0.5, y=540, anchor="center", width=340, height=40)

        self.input_box = tk.Entry(
            self.input_frame, 
            bg="#1a1a2e", 
            fg="#E6E6FA",
            insertbackground="#FF00CC", 
            bd=0, 
            relief="flat",
            font=("Consolas", 11)
        )
        self.input_box.place(x=5, y=5, width=280, height=30)
        self.input_box.bind('<Return>', self._send_message_on_event)

        self.send_btn = tk.Button(
            self.input_frame, 
            text="➤", 
            command=self.send_message,
            bg="#FF00CC", 
            fg="white", 
            bd=0, 
            relief="flat",
            font=("Courier New", 16, "bold"), 
            activebackground="#1a1a2e",
            activeforeground="#FF00CC"
        )
        self.send_btn.place(x=290, y=5, width=45, height=30)
        
        # Typing Indicator (placed dynamically)
        self.typing_indicator = TypingIndicator(self, bg="#000000")

        self.input_handler = None
        
    def _update_led_border(self, color_name):
        """ Deprecated. Kept for compatibility, does nothing. """
        pass

    def update_mode(self, mode):
        """ Update Jalen's mode. Currently doesn't have visual feedback other than typing. """
        if mode == "processing":
            self.show_typing_indicator()
        elif mode == "error":
            self.hide_typing_indicator() # Example: stop typing on error
        elif mode == "incoming":
            pass # No visual for incoming yet
        else: # Default to calm
            self.hide_typing_indicator()

    def _flicker_led(self, color_name, times=3, interval_ms=75):
        """ Deprecated. Kept for compatibility, does nothing. """
        pass

    def _pulse_led(self, color_name, pulses=2, interval_ms=200):
        """ Deprecated. Kept for compatibility, does nothing. """
        pass

    def _log_message(self, msg):
        """Internal method to insert a message into the chat log."""
        self.chat_display.config(state=tk.NORMAL) # Temporarily enable to insert text
        self.chat_display.insert("end", f"{msg}\n")
        self.chat_display.see("end")
        self.chat_display.config(state=tk.DISABLED) # Disable again

    def toggle_settings(self):
        """ Stub for settings panel. Not implemented with new design. """
        print("Settings panel toggled (not implemented).")

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
        self.typing_indicator.place(relx=0.5, y=575, anchor="center")
        self.typing_indicator.start_typing()

    def hide_typing_indicator(self):
        """Hide the typing indicator and stop animation."""
        self.typing_indicator.stop_typing()
        self.typing_indicator.place_forget()

    # ———————————————————————————
    # 🔹 Public Methods for Interaction
    # ———————————————————————————

    def set_input_handler(self, handler):
        """Sets the function to call when the user sends a message."""
        self.input_handler = handler

    def send_message(self):
        """Handles sending the message from the input box."""
        message = self.input_box.get().strip()
        if message and self.input_handler:
            self.input_box.delete(0, tk.END)
            self.input_handler(message)
        elif not self.input_handler:
            self._log_message("[JalenWidget] Error: Input handler not set.")

    def _send_message_on_event(self, event=None):
        """Callback for the return key event."""
        self.send_message()

    def focus_input(self):
        """Sets focus to the input box."""
        self.input_box.focus()

    # ———————————————————————————
    # 🔹 PULSE REGISTRATION PATCH
    # ———————————————————————————
    def register_pulse(self, pulse_coordinator):
        # pulse_coordinator.register_observer(self.status_bar.handle_pulse_update) # This may need to change if status_bar is removed
        pass

    def load_avatar_image(self, image_path, size=(180, 180)):
        """Loads and displays the avatar image."""
        if not os.path.exists(image_path):
            print(f"[JalenWidget] Avatar image not found at: {image_path}")
            # Create a placeholder if image is missing
            placeholder = Image.new('RGB', size, (40, 40, 40))
            self.avatar_image = ImageTk.PhotoImage(placeholder)
        else:
            try:
                # Load the image with PIL and convert to PhotoImage
                avatar_pil = Image.open(image_path)
                avatar_pil = avatar_pil.resize(size, Image.Resampling.LANCZOS)
                self.avatar_image = ImageTk.PhotoImage(avatar_pil)
            except Exception as e:
                print(f"Error loading avatar image: {e}")
                placeholder = Image.new('RGB', size, (40, 10, 10)) # Reddish placeholder on error
                self.avatar_image = ImageTk.PhotoImage(placeholder)
        
        self.avatar_label.config(image=self.avatar_image)

    def show_avatar(self, image_path=None, temporary=False):
        """Shows a specific avatar, or the default one."""
        if image_path:
            self.load_avatar_image(image_path, size=(180, 180)) # Ensure correct size
        self.avatar_label.place(relx=0.5, y=170, anchor="center") # Make sure it's visible

    def hide_avatar(self):
        """Hides the avatar label."""
        self.avatar_label.place_forget()
