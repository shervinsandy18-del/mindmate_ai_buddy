import tkinter as tk
from tkinter import messagebox
from mindmate.theme import *

MODES = {"Focus": 25, "Short Break": 5, "Long Break": 15}


class TimerPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Focus Timer", "Pomodoro technique: 25 minutes of deep work")
        self.mode, self.total = "Focus", 25 * 60
        self.remaining, self.running, self.job = self.total, False, None
        card = Card(self)
        card.pack(padx=34, pady=(0, 24), fill="both", expand=True)
        modes = tk.Frame(card, bg=CARD)
        modes.pack(pady=(18, 4))
        for name in MODES:
            RoundedButton(modes, name, lambda n=name: self.set_mode(n), bg=INPUT, hover=BORDER, width=110, height=32).pack(side="left", padx=4)
        self.canvas = tk.Canvas(card, width=300, height=300, bg=CARD, highlightthickness=0)
        self.canvas.pack(expand=True)
        bar = tk.Frame(card, bg=CARD)
        bar.pack(pady=(0, 24))
        self.start_btn = RoundedButton(bar, "Start", self.toggle, width=110)
        self.start_btn.pack(side="left", padx=6)
        RoundedButton(bar, "Reset", self.reset, bg=INPUT, hover=BORDER, width=110).pack(side="left", padx=6)
        self.draw()

    def draw(self):
        c = self.canvas
        c.delete("all")
        c.create_oval(30, 30, 270, 270, outline=INPUT, width=14)
        frac = self.remaining / self.total if self.total else 0
        if frac > 0:
            c.create_arc(30, 30, 270, 270, start=90, extent=-359.9 * frac, style="arc",
                         outline=ACCENT if self.mode == "Focus" else SUCCESS, width=14)
        m, s = divmod(self.remaining, 60)
        c.create_text(150, 140, text=f"{m:02d}:{s:02d}", fill=TEXT, font=font(44, "bold"))
        c.create_text(150, 190, text=self.mode.upper(), fill=MUTED, font=font(10, "bold"))

    def set_mode(self, name):
        self.mode = name
        self.total = MODES[name] * 60
        self.reset()

    def toggle(self):
        if self.running:
            self.running = False
            if self.job:
                self.after_cancel(self.job)
            self.start_btn.set_text("Resume")
        else:
            self.running = True
            self.start_btn.set_text("Pause")
            self.job = self.after(1000, self.tick)

    def tick(self):
        self.remaining -= 1
        self.draw()
        if self.remaining <= 0:
            self.running = False
            self.start_btn.set_text("Start")
            self.bell()
            if self.mode == "Focus":
                self.db.add_pomodoro()
            messagebox.showinfo("MindMate", f"{self.mode} session complete! 🎉\n"
                                + ("Time for a short break." if self.mode == "Focus" else "Ready to focus again?"))
            self.remaining = self.total
            self.draw()
        else:
            self.job = self.after(1000, self.tick)

    def reset(self):
        self.running = False
        if self.job:
            self.after_cancel(self.job)
            self.job = None
        self.remaining = self.total
        self.start_btn.set_text("Start")
        self.draw()
