import datetime
import tkinter as tk
from tkinter import messagebox
from mindmate.theme import *


class NotesPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Notes", "Capture and organise your study material")
        self.current, self.view = None, []
        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True, padx=28, pady=(0, 24))
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)

        left = Card(body)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 14))
        self.search = make_entry(left)
        self.search.pack(fill="x", padx=12, pady=(12, 8), ipady=5)
        self.search.bind("<KeyRelease>", lambda e: self.refresh())
        self.listbox = tk.Listbox(left, bg=CARD, fg=TEXT, width=28, relief="flat", font=font(11),
                                  selectbackground=ACCENT, selectforeground="#fff", activestyle="none",
                                  highlightthickness=0, exportselection=False)
        self.listbox.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        self.listbox.bind("<<ListboxSelect>>", self._select)
        RoundedButton(left, "+ New Note", self.new, width=200).pack(padx=12, pady=(0, 12))

        right = Card(body)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Title", bg=CARD, fg=MUTED, font=font(10)).pack(anchor="w", padx=16, pady=(14, 2))
        self.title = make_entry(right)
        self.title.pack(fill="x", padx=16, ipady=6)
        tk.Label(right, text="Subject / Category", bg=CARD, fg=MUTED, font=font(10)).pack(anchor="w", padx=16, pady=(10, 2))
        self.cat = make_entry(right)
        self.cat.pack(fill="x", padx=16, ipady=6)
        tk.Label(right, text="Content", bg=CARD, fg=MUTED, font=font(10)).pack(anchor="w", padx=16, pady=(10, 2))
        self.content = make_text(right)
        self.content.pack(fill="both", expand=True, padx=16)
        bar = tk.Frame(right, bg=CARD)
        bar.pack(fill="x", padx=16, pady=14)
        RoundedButton(bar, "Save Note", self.save, bg=SUCCESS, hover="#5BDDB0", fg="#10131A").pack(side="left")
        RoundedButton(bar, "Delete", self.delete, bg=DANGER, hover="#FF8496").pack(side="left", padx=10)
        self.status = tk.Label(bar, bg=CARD, fg=MUTED, font=font(9))
        self.status.pack(side="right")

    def refresh(self):
        q = self.search.get().strip().lower()
        self.view = [n for n in reversed(self.db.all("notes"))
                     if q in (n["title"] + n.get("category", "") + n["content"]).lower()]
        self.listbox.delete(0, "end")
        for n in self.view:
            tag = f"  [{n['category']}]" if n.get("category") else ""
            self.listbox.insert("end", n["title"] + tag)
        if self.current:
            for i, n in enumerate(self.view):
                if n["id"] == self.current:
                    self.listbox.selection_set(i)

    def _select(self, _):
        sel = self.listbox.curselection()
        if not sel:
            return
        n = self.view[sel[0]]
        self.current = n["id"]
        self.title.delete(0, "end"); self.title.insert(0, n["title"])
        self.cat.delete(0, "end"); self.cat.insert(0, n.get("category", ""))
        self.content.delete("1.0", "end"); self.content.insert("1.0", n["content"])
        self.status.config(text="Last updated " + n.get("updated", ""))

    def new(self):
        self.current = None
        self.listbox.selection_clear(0, "end")
        for w in (self.title, self.cat):
            w.delete(0, "end")
        self.content.delete("1.0", "end")
        self.status.config(text="New note")
        self.title.focus_set()

    def save(self):
        title = self.title.get().strip()
        if not title:
            messagebox.showwarning("MindMate", "Please give your note a title.")
            return
        fields = dict(title=title, category=self.cat.get().strip(),
                      content=self.content.get("1.0", "end").strip(),
                      updated=datetime.datetime.now().strftime("%d %b %Y, %H:%M"))
        if self.current:
            self.db.update("notes", self.current, **fields)
        else:
            self.current = self.db.add("notes", **fields)["id"]
        self.status.config(text="Saved ✓")
        self.refresh()

    def delete(self):
        if not self.current:
            messagebox.showinfo("MindMate", "Select a note to delete first.")
            return
        if messagebox.askyesno("Delete note", "Delete this note permanently?"):
            self.db.delete("notes", self.current)
            self.new()
            self.refresh()
