import tkinter as tk

class SettingsPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg="#111111")
        label = tk.Label(self, text="Settings", bg="#111111", fg="#FFFFFF")
        label.pack(pady=10)

        self.close_btn = tk.Button(self, text="Close", command=self.hide, bg="#333333", fg="#FFFFFF")
        self.close_btn.pack(pady=5)

    def show(self):
        self.pack(side="bottom", fill="x")

    def hide(self):
        self.pack_forget()