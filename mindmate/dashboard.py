import datetime
import tkinter as tk
from mindmate.theme import *

QUOTES = [
    "The secret of getting ahead is getting started.",
    "Small daily improvements lead to stunning results.",
    "Study while others are sleeping; work while others are loafing.",
    "Don't watch the clock; do what it does. Keep going.",
    "Success is the sum of small efforts repeated day in and day out.",
    "You don't have to be great to start, but you have to start to be great.",
    "Discipline is choosing between what you want now and what you want most.",
]


class DashboardPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Welcome back 👋", "Here's your study overview")
        self.stats = tk.Frame(self, bg=BG)
        self.stats.pack(fill="x", padx=28)
        self.labels = {}
        for i, (key, name, color) in enumerate([
                ("notes", "Total Notes", ACCENT), ("tasks", "Study Tasks", "#5AA9FF"),
                ("done", "Completed", SUCCESS), ("cards", "Flashcards", "#FFB85C"),
                ("focus", "Focus Sessions", "#F2677A")]):
            self.stats.columnconfigure(i, weight=1, uniform="s")
            card = Card(self.stats)
            card.grid(row=0, column=i, sticky="nsew", padx=6, pady=4)
            tk.Label(card, text=name, bg=CARD, fg=MUTED, font=font(10)).pack(anchor="w", padx=16, pady=(14, 0))
            lbl = tk.Label(card, text="0", bg=CARD, fg=color, font=font(28, "bold"))
            lbl.pack(anchor="w", padx=16, pady=(0, 14))
            self.labels[key] = lbl

        quote = Card(self)
        quote.pack(fill="x", padx=34, pady=12)
        tk.Label(quote, text="DAILY MOTIVATION", bg=CARD, fg=ACCENT, font=font(9, "bold")).pack(anchor="w", padx=18, pady=(14, 2))
        self.quote = tk.Label(quote, bg=CARD, fg=TEXT, font=font(14, "italic"), wraplength=700, justify="left")
        self.quote.pack(anchor="w", padx=18, pady=(0, 16))
        quote.bind("<Configure>", lambda e: self.quote.config(wraplength=max(200, e.width - 40)))

        tk.Label(self, text="Quick Navigation", bg=BG, fg=TEXT, font=font(13, "bold")).pack(anchor="w", padx=34, pady=(8, 6))
        nav = tk.Frame(self, bg=BG)
        nav.pack(anchor="w", padx=34)
        for key, text in [("notes", "New Note"), ("planner", "Add Task"), ("flashcards", "Study Cards"),
                          ("timer", "Start Focus"), ("buddy", "Ask Buddy")]:
            RoundedButton(nav, text, lambda k=key: app.show(k), width=140).pack(side="left", padx=(0, 10), pady=4)

    def refresh(self):
        tasks = self.db.all("tasks")
        vals = {"notes": len(self.db.all("notes")), "tasks": len(tasks),
                "done": sum(1 for t in tasks if t["done"]), "cards": len(self.db.all("flashcards")),
                "focus": self.db.data["stats"].get("pomodoros", 0)}
        for k, v in vals.items():
            self.labels[k].config(text=str(v))
        day = datetime.date.today().timetuple().tm_yday
        self.quote.config(text=f"“{QUOTES[day % len(QUOTES)]}”")
