import tkinter as tk

class TypingIndicator(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Initialize canvas and dot objects
        self.canvas = tk.Canvas(self, height=10, bg=self["bg"], highlightthickness=0)
        self.canvas.pack()
        self.dots = []
        for i in range(3):
            dot = self.canvas.create_oval(5 + i*10, 2, 10 + i*10, 7, fill="#555555", outline="")
            self.dots.append(dot)
        self.is_typing = False
        self.animation_id = None

    def start_typing(self):
        if not self.is_typing:
            self.is_typing = True
            self._animate_typing(0)

    def stop_typing(self):
        if self.is_typing:
            self.is_typing = False
            if self.animation_id:
                self.after_cancel(self.animation_id)
            for dot in self.dots:
                self.canvas.itemconfig(dot, fill="#555555")

    def _animate_typing(self, dot_index):
        if not self.is_typing: return

        # Dim all dots
        for dot in self.dots:
            self.canvas.itemconfig(dot, fill="#555555")

        # Light up the current dot
        self.canvas.itemconfig(self.dots[dot_index], fill="#E6E6FA")

        next_dot_index = (dot_index + 1) % 3
        self.animation_id = self.after(300, lambda: self._animate_typing(next_dot_index))