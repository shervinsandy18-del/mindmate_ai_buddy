import random
import tkinter as tk
from tkinter import messagebox
from mindmate.theme import *


class FlashcardsPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Flashcards", "Practice active recall")
        self.idx, self.revealed = 0, False
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        body.columnconfigure(0, weight=1)
        body.rowconfigure(0, weight=1)

        study = Card(body)
        study.grid(row=0, column=0, sticky="nsew", padx=(6, 14))
        self.counter = tk.Label(study, bg=CARD, fg=MUTED, font=font(10))
        self.counter.pack(pady=(16, 0))
        self.side = tk.Label(study, bg=CARD, fg=ACCENT, font=font(10, "bold"))
        self.side.pack(pady=(24, 0))
        self.text = tk.Label(study, bg=CARD, fg=TEXT, font=font(20, "bold"), wraplength=480, justify="center")
        self.text.pack(expand=True, fill="both", padx=24)
        study.bind("<Configure>", lambda e: self.text.config(wraplength=max(200, e.width - 60)))
        bar = tk.Frame(study, bg=CARD)
        bar.pack(pady=18)
        RoundedButton(bar, "◀ Prev", self.prev, bg=INPUT, hover=BORDER, width=90).pack(side="left", padx=4)
        RoundedButton(bar, "Reveal Answer", self.flip, width=140).pack(side="left", padx=4)
        RoundedButton(bar, "Next ▶", self.next, bg=INPUT, hover=BORDER, width=90).pack(side="left", padx=4)
        bar2 = tk.Frame(study, bg=CARD)
        bar2.pack(pady=(0, 18))
        RoundedButton(bar2, "Shuffle", self.shuffle, bg=INPUT, hover=BORDER, width=90, height=32).pack(side="left", padx=4)
        RoundedButton(bar2, "Delete Card", self.delete, bg=DANGER, hover="#FF8496", width=110, height=32).pack(side="left", padx=4)

        form = Card(body)
        form.grid(row=0, column=1, sticky="ns")
        tk.Label(form, text="Create Flashcard", bg=CARD, fg=TEXT, font=font(13, "bold")).pack(anchor="w", padx=16, pady=(16, 8))
        tk.Label(form, text="Question", bg=CARD, fg=MUTED, font=font(10)).pack(anchor="w", padx=16)
        self.q = make_text(form, width=30, height=5)
        self.q.pack(padx=16, pady=(2, 10))
        tk.Label(form, text="Answer", bg=CARD, fg=MUTED, font=font(10)).pack(anchor="w", padx=16)
        self.a = make_text(form, width=30, height=5)
        self.a.pack(padx=16, pady=(2, 14))
        RoundedButton(form, "+ Add Card", self.add, width=240).pack(padx=16, pady=(0, 16))

    def cards(self):
        return self.db.all("flashcards")

    def add(self):
        q, a = self.q.get("1.0", "end").strip(), self.a.get("1.0", "end").strip()
        if not q or not a:
            messagebox.showwarning("MindMate", "Both question and answer are required.")
            return
        self.db.add("flashcards", question=q, answer=a)
        self.q.delete("1.0", "end"); self.a.delete("1.0", "end")
        self.idx = len(self.cards()) - 1
        self.show()

    def show(self):
        cards = self.cards()
        self.revealed = False
        if not cards:
            self.counter.config(text="No cards yet")
            self.side.config(text="")
            self.text.config(text="Add your first flashcard →", fg=MUTED)
            return
        self.idx %= len(cards)
        self.counter.config(text=f"Card {self.idx + 1} of {len(cards)}")
        self.side.config(text="QUESTION")
        self.text.config(text=cards[self.idx]["question"], fg=TEXT)

    def flip(self):
        cards = self.cards()
        if not cards:
            return
        self.revealed = not self.revealed
        c = cards[self.idx]
        self.side.config(text="ANSWER" if self.revealed else "QUESTION")
        self.text.config(text=c["answer"] if self.revealed else c["question"],
                         fg=SUCCESS if self.revealed else TEXT)

    def next(self):
        self.idx += 1
        self.show()

    def prev(self):
        self.idx -= 1
        self.show()

    def shuffle(self):
        random.shuffle(self.db.data["flashcards"])
        self.db.save()
        self.idx = 0
        self.show()

    def delete(self):
        cards = self.cards()
        if cards and messagebox.askyesno("Delete card", "Delete this flashcard?"):
            self.db.delete("flashcards", cards[self.idx]["id"])
            self.show()

    def refresh(self):
        self.show()
