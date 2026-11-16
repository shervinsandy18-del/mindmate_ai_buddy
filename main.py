"""MindMate – Smart Study Companion. Run: python main.py"""
import sys
import tkinter as tk
from tkinter import messagebox
from database.database import Database
from mindmate.theme import *
from mindmate.dashboard import DashboardPage
from mindmate.notes import NotesPage
from mindmate.planner import PlannerPage
from mindmate.flashcards import FlashcardsPage
from mindmate.timer import TimerPage
from mindmate.study_buddy import StudyBuddyPage

NAV = [("dashboard", "◈  Dashboard", DashboardPage), ("notes", "✎  Notes", NotesPage),
       ("planner", "☑  Planner", PlannerPage), ("flashcards", "❖  Flashcards", FlashcardsPage),
       ("timer", "◷  Focus Timer", TimerPage), ("buddy", "✦  Study Buddy", StudyBuddyPage)]


class MindMateApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MindMate – Smart Study Companion")
        self.geometry("1150x720")
        self.minsize(960, 620)
        self.configure(bg=BG)
        self.db = Database()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        side = tk.Frame(self, bg=SIDEBAR, width=230)
        side.grid(row=0, column=0, sticky="ns")
        side.grid_propagate(False)
        side.pack_propagate(False)
        tk.Label(side, text="🧠 MindMate", bg=SIDEBAR, fg=ACCENT, font=font(20, "bold")).pack(anchor="w", padx=22, pady=(28, 2))
        tk.Label(side, text="Smart Study Companion", bg=SIDEBAR, fg=MUTED, font=font(9)).pack(anchor="w", padx=24, pady=(0, 26))
        self.nav = {}
        for key, text, _ in NAV:
            lbl = tk.Label(side, text=text, bg=SIDEBAR, fg=MUTED, font=font(12), anchor="w", padx=22, pady=11, cursor="hand2")
            lbl.pack(fill="x", padx=10, pady=2)
            lbl.bind("<Button-1>", lambda e, k=key: self.show(k))
            lbl.bind("<Enter>", lambda e, l=lbl: l.cget("bg") == SIDEBAR and l.config(bg=CARD))
            lbl.bind("<Leave>", lambda e, l=lbl, k=key: l.config(bg=ACCENT if k == self.current else SIDEBAR))
            self.nav[key] = lbl
        tk.Label(side, text="v1.0 • Stay consistent ✨", bg=SIDEBAR, fg=MUTED, font=font(9)).pack(side="bottom", pady=18)

        box = tk.Frame(self, bg=BG)
        box.grid(row=0, column=1, sticky="nsew")
        box.rowconfigure(0, weight=1)
        box.columnconfigure(0, weight=1)
        self.pages, self.current = {}, None
        for key, _, cls in NAV:
            page = cls(box, self)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages[key] = page
        self.show("dashboard")

    def show(self, key):
        self.current = key
        for k, lbl in self.nav.items():
            active = k == key
            lbl.config(bg=ACCENT if active else SIDEBAR, fg="#FFFFFF" if active else MUTED)
        self.pages[key].refresh()
        self.pages[key].tkraise()

    def report_callback_exception(self, exc, val, tb):
        messagebox.showerror("MindMate", f"Something went wrong:\n{val}")


if __name__ == "__main__":
    try:
        MindMateApp().mainloop()
    except tk.TclError as err:
        print("Could not start the GUI:", err)
        sys.exit(1)
