import tkinter as tk

class StatusBar(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.canvas = tk.Canvas(self, height=6, bg="#000000", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.status_rect = self.canvas.create_rectangle(0, 0, 0, 6, fill="#00FF00", width=0)
        self.bind("<Configure>", self.resize_bar)

        self.current_status = "idle"
        self.update_status(self.current_status)

    def update_status(self, status):
        colors = {
            "idle": "#2E8B57",       # sea green
            "assist": "#FFA500",    # orange
            "chat": "#00FFFF",       # neon cyan
            "alert": "#FF4500",      # orange-red
        }
        color = colors.get(status, "#444444")
        self.canvas.itemconfig(self.status_rect, fill=color)
        self.canvas.coords(self.status_rect, 0, 0, self.winfo_width(), 6)
        self.current_status = status

    def resize_bar(self, event=None):
        self.canvas.coords(self.status_rect, 0, 0, self.winfo_width(), 6)

    def pulse(self, color1, color2, speed=500):
        """Simple color pulse effect between two colors for the status bar."""
        current_fill = self.canvas.itemcget(self.status_rect, "fill")
        new_color = color2 if current_fill == color1 else color1
        self.canvas.itemconfig(self.status_rect, fill=new_color)
        self.after(speed, lambda: self.pulse(color1, color2, speed))
