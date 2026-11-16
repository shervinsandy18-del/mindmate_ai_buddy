import tkinter as tk
from tkinter import messagebox
from mindmate.theme import *

PRIORITY_COLORS = {"High": DANGER, "Medium": "#FFB85C", "Low": SUCCESS}


class PlannerPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Study Planner", "Plan your work and tick it off")
        form = Card(self)
        form.pack(fill="x", padx=34, pady=(0, 12))
        row = tk.Frame(form, bg=CARD)
        row.pack(fill="x", padx=14, pady=14)
        row.columnconfigure(0, weight=1)
        self.title = make_entry(row)
        self.title.grid(row=0, column=0, sticky="ew", ipady=6, padx=(0, 8))
        self.title.bind("<Return>", lambda e: self.add())
        self.due = make_entry(row, width=14)
        self.due.grid(row=0, column=1, ipady=6, padx=(0, 8))
        self.due.insert(0, "Due (optional)")
        self.due.bind("<FocusIn>", lambda e: self.due.get() == "Due (optional)" and self.due.delete(0, "end"))
        self.prio = tk.StringVar(value="Medium")
        om = tk.OptionMenu(row, self.prio, *PRIORITY_COLORS)
        om.config(bg=INPUT, fg=TEXT, relief="flat", highlightthickness=0, activebackground=ACCENT, width=8)
        om["menu"].config(bg=INPUT, fg=TEXT)
        om.grid(row=0, column=2, padx=(0, 8))
        RoundedButton(row, "+ Add Task", self.add, width=110).grid(row=0, column=3)

        cols = tk.Frame(self, bg=BG)
        cols.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        cols.rowconfigure(0, weight=1)
        self.lists = {}
        self.heads = {}
        for i, (key, name) in enumerate([("pending", "Pending"), ("done", "Completed")]):
            cols.columnconfigure(i, weight=1, uniform="c")
            card = Card(cols)
            card.grid(row=0, column=i, sticky="nsew", padx=6)
            self.heads[key] = tk.Label(card, bg=CARD, fg=TEXT, font=font(13, "bold"))
            self.heads[key].pack(anchor="w", padx=16, pady=(14, 6))
            sf = ScrollFrame(card)
            sf.pack(fill="both", expand=True, padx=8, pady=(0, 8))
            self.lists[key] = sf

    def add(self):
        title = self.title.get().strip()
        if not title:
            messagebox.showwarning("MindMate", "Enter a task first.")
            return
        due = self.due.get().strip()
        due = "" if due == "Due (optional)" else due
        self.db.add("tasks", title=title, due=due, priority=self.prio.get(), done=False)
        self.title.delete(0, "end")
        self.refresh()

    def toggle(self, t):
        self.db.update("tasks", t["id"], done=not t["done"])
        self.refresh()

    def remove(self, t):
        self.db.delete("tasks", t["id"])
        self.refresh()

    def refresh(self):
        tasks = self.db.all("tasks")
        for key, done in (("pending", False), ("done", True)):
            sf = self.lists[key]
            sf.clear()
            items = [t for t in tasks if t["done"] == done]
            self.heads[key].config(text=f"{'Completed' if done else 'Pending'} ({len(items)})")
            if not items:
                tk.Label(sf.inner, text="Nothing here yet", bg=CARD, fg=MUTED, font=font(10)).pack(pady=20)
            for t in items:
                r = tk.Frame(sf.inner, bg=INPUT)
                r.pack(fill="x", pady=3, padx=4)
                tk.Frame(r, bg=PRIORITY_COLORS.get(t["priority"], ACCENT), width=4).pack(side="left", fill="y")
                RoundedButton(r, "↺" if done else "✓", lambda t=t: self.toggle(t),
                              bg=INPUT, hover=BORDER, fg=SUCCESS if not done else MUTED, width=36, height=32).pack(side="left", padx=4, pady=4)
                info = tk.Frame(r, bg=INPUT)
                info.pack(side="left", fill="x", expand=True, pady=4)
                tk.Label(info, text=t["title"], bg=INPUT, fg=MUTED if done else TEXT, anchor="w",
                         font=(FAMILY, 11, "overstrike") if done else font(11)).pack(anchor="w")
                sub = t["priority"] + (f"  •  Due {t['due']}" if t["due"] else "")
                tk.Label(info, text=sub, bg=INPUT, fg=MUTED, font=font(9)).pack(anchor="w")
                RoundedButton(r, "✕", lambda t=t: self.remove(t), bg=INPUT, hover=BORDER, fg=DANGER,
                              width=36, height=32).pack(side="right", padx=6)
