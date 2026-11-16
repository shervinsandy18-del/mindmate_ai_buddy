import random, re
import tkinter as tk
from mindmate.theme import *

TIPS = [
    "Use the Pomodoro technique: 25 minutes focus, 5 minutes break.",
    "Test yourself instead of rereading: active recall beats passive review.",
    "Space your revision over several days; spaced repetition builds long-term memory.",
    "Teach the topic to someone else (or a rubber duck). If you can explain it, you know it.",
    "Study the hardest subject first, while your energy is highest.",
    "Sleep is part of studying. Memory consolidates overnight.",
    "Put your phone in another room during focus sessions.",
]
RULES = [
    (("hello", "hi ", "hey"), "Hi! I'm your Study Buddy. Ask me for a tip, a revision schedule, or help with motivation."),
    (("tip", "advice", "suggest"), None),
    (("focus", "distract", "concentrat"), "Try a 25-minute Pomodoro in the Focus Timer tab. Silence notifications and keep only one tab or book open."),
    (("memor", "remember", "revise", "flashcard"), "Make flashcards in the Flashcards tab and quiz yourself daily. Review wrong cards more often."),
    (("exam", "test"), "Work backwards from the exam date: learn, practise past papers, then revise. Type 'schedule for 10 days' and I'll draft a plan."),
    (("stress", "anxious", "overwhelm", "tired", "motivat"), "Break your work into tiny tasks and add them to the Planner. Finishing one small thing builds momentum. Take breaks; you've got this!"),
    (("note",), "Keep notes short and organised by subject. Review them within 24 hours to lock them in."),
    (("thank",), "You're welcome! Happy studying 🎓"),
]


def schedule(days):
    days = max(1, min(days, 60))
    learn, practise = max(1, round(days * 0.55)), max(0, round(days * 0.3))
    lines = [f"Here's a {days}-day revision plan:"]
    for d in range(1, days + 1):
        if d <= learn:
            phase = "Learn & summarise one topic, then make flashcards"
        elif d <= learn + practise:
            phase = "Practise questions / past papers and fix weak areas"
        elif d < days:
            phase = "Quick revision using notes and flashcards"
        else:
            phase = "Light review, rest well, and sleep early"
        lines.append(f"  Day {d}: {phase}")
    lines.append("Use 25-minute focus blocks with 5-minute breaks.")
    return "\n".join(lines)


def reply(msg):
    low = msg.lower() + " "
    m = re.search(r"(\d+)\s*(day|days|week|weeks)", low)
    if any(k in low for k in ("schedule", "plan", "timetable", "revision")) and m:
        n = int(m.group(1)) * (7 if m.group(2).startswith("week") else 1)
        return schedule(n)
    if any(k in low for k in ("schedule", "plan", "timetable")):
        return "How many days do you have? Try: 'make a schedule for 7 days'."
    for keys, ans in RULES:
        if any(k in low for k in keys):
            return ans or random.choice(TIPS)
    return "I can help with study tips, focus, memory techniques, motivation and revision schedules. " + random.choice(TIPS)


class StudyBuddyPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Study Buddy", "Offline study assistant: tips, focus and revision plans")
        card = Card(self)
        card.pack(fill="both", expand=True, padx=34, pady=(0, 24))
        chips = tk.Frame(card, bg=CARD)
        chips.pack(fill="x", padx=14, pady=(14, 6))
        for text in ("Give me a study tip", "Make a schedule for 7 days", "How do I stay focused?", "I feel overwhelmed"):
            RoundedButton(chips, text, lambda t=text: self.send(t), bg=INPUT, hover=BORDER, width=185, height=30).pack(side="left", padx=3)
        self.chat = tk.Text(card, bg=CARD, fg=TEXT, relief="flat", font=font(11), wrap="word",
                            padx=14, pady=10, state="disabled", highlightthickness=0)
        self.chat.pack(fill="both", expand=True, padx=8)
        self.chat.tag_config("you", foreground=ACCENT, font=font(11, "bold"), spacing1=10)
        self.chat.tag_config("bot", foreground=SUCCESS, font=font(11, "bold"), spacing1=10)
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x", padx=14, pady=14)
        row.columnconfigure(0, weight=1)
        self.entry = make_entry(row)
        self.entry.grid(row=0, column=0, sticky="ew", ipady=7, padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.send())
        RoundedButton(row, "Send", self.send, width=90).grid(row=0, column=1)
        self.say("Buddy", "Hi! I'm your Study Buddy 👋 Ask me for tips, or say 'schedule for 10 days'.")

    def say(self, who, text):
        self.chat.config(state="normal")
        self.chat.insert("end", f"{who}\n", "you" if who == "You" else "bot")
        self.chat.insert("end", text + "\n")
        self.chat.config(state="disabled")
        self.chat.see("end")

    def send(self, text=None):
        text = (text or self.entry.get()).strip()
        if not text:
            return
        self.entry.delete(0, "end")
        self.say("You", text)
        self.say("Buddy", reply(text))
