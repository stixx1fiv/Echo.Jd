import tkinter as tk
from tkinter import ttk

class SettingsPanel(tk.Frame):
    def __init__(self, parent, **kwargs):
        # The panel itself will be a child of the main JalenWidget (parent)
        # It should appear on top of other elements in JalenWidget's content_frame
        super().__init__(parent, bg="#0A0A14", bd=2, relief="solid", **kwargs) # Dark HUD background, clean border
        # Initial placeholder color, can be themed later
        self.config(highlightbackground="#00FFFF", highlightcolor="#00FFFF", highlightthickness=1)


        self.is_shown = False

        # --- Title ---
        title_bar = tk.Frame(self, bg="#080810") # Slightly darker title bar
        title_bar.pack(side="top", fill="x")

        label = tk.Label(title_bar, text="J.A.L.E.N - Settings", font=("Courier New", 12, "bold"), fg="#00FFFF", bg="#080810")
        label.pack(pady=5, padx=10, side="left")

        self.close_btn = ttk.Button(title_bar, text="X", command=self.hide, style="Toolbutton", width=3)
        self.close_btn.pack(pady=5, padx=5, side="right")

        # --- Options Frame ---
        options_frame = tk.Frame(self, bg="#0A0A14")
        options_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Placeholder options
        options = [
            ("Theme Color Mode", ["Default", "Neon", "Stealth"]),
            ("Display Size", ["Full", "Compact"]),
            ("Mute System Interjections", None), # Checkbox
            ("Agent Diagnostic Panel", None),   # Button
            ("Portal Dock Toggle", None),       # Checkbox
            ("Developer Tools", None)           # Button
        ]

        for text, values in options:
            row = tk.Frame(options_frame, bg="#0A0A14")
            row.pack(fill="x", pady=2)
            
            lbl = tk.Label(row, text=text + ":", font=("Consolas", 10), fg="#E6E6FA", bg="#0A0A14", anchor="w")
            lbl.pack(side="left", padx=(0,5))

            if values: # This is a Combobox
                combo = ttk.Combobox(row, values=values, state="readonly", width=15, font=("Consolas", 9))
                if values:
                    combo.set(values[0])
                combo.pack(side="left")
            elif text == "Mute System Interjections" or text == "Portal Dock Toggle": # Checkbox
                var = tk.BooleanVar()
                chk = tk.Checkbutton(row, variable=var, bg="#0A0A14", activebackground="#0A0A14", selectcolor="#1a1a2e", fg="#00FFFF", activeforeground="#00FFFF", relief="flat", overrelief="flat", highlightthickness=0)
                chk.pack(side="left")
            else: # This is a Button
                btn = ttk.Button(row, text="Open", style="Toolbutton", width=8) # Placeholder action
                btn.pack(side="left")


    def show(self):
        if not self.is_shown:
            self.is_shown = True
            # Place it relative to the JalenWidget (self.master)
            # It should slide from the right or appear as an overlay.
            # For simplicity, let's make it appear from the right.
            self.place(relx=1.0, rely=0, relwidth=0.5, relheight=1.0, anchor="ne")
            # Animation for sliding (optional, can be complex with place)
            # self.master.update_idletasks()
            # target_x = self.master.winfo_width() - self.winfo_width()
            # current_x = self.master.winfo_width()
            # self.place(x=current_x, y=0, width=self.winfo_width(), height=self.master.winfo_height())
            # # Add animation logic here if desired

    def hide(self):
        if self.is_shown:
            self.is_shown = False
            self.place_forget()