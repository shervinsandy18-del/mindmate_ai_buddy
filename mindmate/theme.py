"""Theme constants and reusable widgets."""
import tkinter as tk

BG, SIDEBAR, CARD = "#10131A", "#171C26", "#1D2430"
ACCENT, ACCENT_H = "#8B7CFF", "#A093FF"
TEXT, MUTED, SUCCESS = "#F2F5FA", "#9AA7B8", "#42C99A"
DANGER, INPUT, BORDER = "#F2677A", "#252D3B", "#2A3345"
FAMILY = "Segoe UI"


def font(size=11, weight="normal"):
    return (FAMILY, size, weight)


class Card(tk.Frame):
    def __init__(self, parent, **kw):
        kw.setdefault("bg", CARD)
        super().__init__(parent, highlightbackground=BORDER, highlightthickness=1, **kw)


class RoundedButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg=ACCENT, hover=ACCENT_H,
                 fg="#FFFFFF", width=130, height=38, radius=12):
        super().__init__(parent, width=width, height=height, bg=parent["bg"],
                         highlightthickness=0, cursor="hand2")
        self.text, self.cmd, self.bgc, self.hv, self.fg = text, command, bg, hover, fg
        self.w, self.h, self.r = width, height, radius
        self._draw(bg)
        self.bind("<Enter>", lambda e: self._draw(self.hv))
        self.bind("<Leave>", lambda e: self._draw(self.bgc))
        self.bind("<ButtonRelease-1>", self._click)

    def _draw(self, color):
        self.delete("all")
        w, h, r = self.w, self.h, self.r
        pts = [r, 0, w - r, 0, w, 0, w, r, w, h - r, w, h, w - r, h,
               r, h, 0, h, 0, h - r, 0, r, 0, 0]
        self.create_polygon(pts, smooth=True, fill=color, outline=color)
        self.create_text(w / 2, h / 2, text=self.text, fill=self.fg, font=font(10, "bold"))

    def _click(self, e):
        if self.cmd and 0 <= e.x <= self.w and 0 <= e.y <= self.h:
            self.cmd()

    def set_text(self, text):
        self.text = text
        self._draw(self.bgc)


def make_entry(parent, **kw):
    return tk.Entry(parent, bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat",
                    font=font(11), highlightthickness=1, highlightbackground=BORDER,
                    highlightcolor=ACCENT, **kw)


def make_text(parent, **kw):
    return tk.Text(parent, bg=INPUT, fg=TEXT, insertbackground=TEXT, relief="flat",
                   font=font(11), highlightthickness=1, highlightbackground=BORDER,
                   highlightcolor=ACCENT, wrap="word", padx=10, pady=8, **kw)


class Page(tk.Frame):
    def __init__(self, parent, app, title, subtitle=""):
        super().__init__(parent, bg=BG)
        self.app, self.db = app, app.db
        head = tk.Frame(self, bg=BG)
        head.pack(fill="x", padx=28, pady=(24, 16))
        tk.Label(head, text=title, bg=BG, fg=TEXT, font=font(22, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(head, text=subtitle, bg=BG, fg=MUTED, font=font(11)).pack(anchor="w")

    def refresh(self):
        pass


class ScrollFrame(tk.Frame):
    def __init__(self, parent, bg=CARD):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner = tk.Frame(self.canvas, bg=bg)
        win = self.canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.canvas.configure(yscrollcommand=sb.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(win, width=e.width))
        self.canvas.bind("<Enter>", self._on)
        self.canvas.bind("<Leave>", self._off)

    def _on(self, _):
        self.canvas.bind_all("<MouseWheel>", self._wheel)
        self.canvas.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(1, "units"))

    def _off(self, _):
        for s in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            self.canvas.unbind_all(s)

    def _wheel(self, e):
        self.canvas.yview_scroll(-1 if e.delta > 0 else 1, "units")

    def clear(self):
        for w in self.inner.winfo_children():
            w.destroy()
