import json
import queue
import threading
import tkinter as tk
import urllib.error
import urllib.request

from mindmate.theme import *

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
DEFAULT_MODEL = "gemma3:1b"
SYSTEM_PROMPT = (
    "You are MindMate, a friendly and practical study buddy. Help with learning, "
    "revision, focus, and study planning. Explain ideas clearly, ask a follow-up "
    "question when it would help, and keep answers encouraging and concise."
)
QUESTION_PLACEHOLDER = "Type your question here..."


def ask_ollama(messages, model):
    """Send a chat request to the local Ollama server and return its reply."""
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "stream": False,
    }).encode("utf-8")
    request = urllib.request.Request(
        OLLAMA_CHAT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=180) as response:
        try:
            result = json.loads(response.read().decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("Ollama returned an invalid response.") from exc

    if not isinstance(result, dict):
        raise ValueError("Ollama returned an invalid response.")
    if result.get("error"):
        raise ValueError(str(result["error"]))

    message = result.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ValueError("Ollama returned an empty reply.")
    return content.strip()


class StudyBuddyPage(Page):
    def __init__(self, parent, app):
        super().__init__(parent, app, "Study Buddy", "Your private, AI-powered study assistant")
        self.history = []
        self.results = queue.Queue()
        self.pending = False

        card = Card(self)
        card.pack(fill="both", expand=True, padx=34, pady=(0, 24))

        chips = tk.Frame(card, bg=CARD)
        chips.pack(fill="x", padx=14, pady=(14, 6))
        for text in ("Give me a study tip", "Plan 7 days", "Help me focus", "I feel overwhelmed"):
            RoundedButton(
                chips, text, lambda t=text: self.send(t), bg=INPUT, hover=BORDER,
                width=145, height=30,
            ).pack(side="left", padx=3)

        settings = tk.Frame(card, bg=CARD)
        settings.pack(fill="x", padx=17, pady=(4, 2))
        tk.Label(settings, text="Ollama model", bg=CARD, fg=MUTED, font=font(10)).pack(side="left")
        self.model_entry = make_entry(settings, width=22)
        self.model_entry.insert(0, DEFAULT_MODEL)
        self.model_entry.pack(side="left", padx=(8, 12), ipady=4)
        RoundedButton(settings, "New chat", self.new_chat, bg=INPUT, hover=BORDER,
                      width=95, height=30).pack(side="right")

        self.status = tk.Label(
            card,
            text=f"Local AI • No API key or usage fees • Run: ollama pull {DEFAULT_MODEL}",
            bg=CARD, fg=MUTED, font=font(9), anchor="w",
        )
        self.status.pack(fill="x", padx=17, pady=(0, 5))

        ask_bar = tk.Frame(card, bg=CARD)
        ask_bar.pack(fill="x", padx=14, pady=(8, 10))
        tk.Label(
            ask_bar, text="Ask Study Buddy", bg=CARD, fg=TEXT,
            font=font(11, "bold"), anchor="w",
        ).pack(fill="x", pady=(0, 6))
        row = tk.Frame(ask_bar, bg=CARD)
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        self.entry = make_entry(row)
        self.entry.config(font=font(12), highlightthickness=2)
        self.entry.grid(row=0, column=0, sticky="ew", ipady=10, padx=(0, 8))
        self.entry.bind("<FocusIn>", self._clear_placeholder)
        self.entry.bind("<FocusOut>", self._restore_placeholder)
        self.entry.bind("<Return>", lambda event: self.send())
        RoundedButton(row, "Ask AI", self.send, width=100, height=42).grid(row=0, column=1)
        self.placeholder_visible = True
        self.entry.insert(0, QUESTION_PLACEHOLDER)
        self.entry.config(fg=MUTED)

        self.chat = tk.Text(
            card, bg=CARD, fg=TEXT, relief="flat", font=font(11), wrap="word",
            padx=14, pady=10, state="disabled", highlightthickness=0,
        )
        self.chat.pack(fill="both", expand=True, padx=8)
        self.chat.tag_config("you", foreground=ACCENT, font=font(11, "bold"), spacing1=10)
        self.chat.tag_config("bot", foreground=SUCCESS, font=font(11, "bold"), spacing1=10)

        self.say(
            "Buddy",
            "Hi! Type a question in the Ask Study Buddy bar above, then press Ask AI or Enter. "
            "You can also choose one of the quick prompts.",
        )

    def say(self, who, text):
        self.chat.config(state="normal")
        self.chat.insert("end", f"{who}\n", "you" if who == "You" else "bot")
        self.chat.insert("end", text + "\n")
        self.chat.config(state="disabled")
        self.chat.see("end")

    def _clear_placeholder(self, _event=None):
        if self.placeholder_visible:
            self.entry.delete(0, "end")
            self.entry.config(fg=TEXT)
            self.placeholder_visible = False

    def _restore_placeholder(self, _event=None):
        if not self.entry.get().strip():
            self.entry.delete(0, "end")
            self.entry.insert(0, QUESTION_PLACEHOLDER)
            self.entry.config(fg=MUTED)
            self.placeholder_visible = True

    def new_chat(self):
        if self.pending:
            return
        self.history.clear()
        self.chat.config(state="normal")
        self.chat.delete("1.0", "end")
        self.chat.config(state="disabled")
        self.say("Buddy", "New chat started. What would you like to study?")

    def send(self, text=None):
        if self.pending:
            return
        if text is None:
            text = "" if self.placeholder_visible else self.entry.get()
        text = text.strip()
        model = self.model_entry.get().strip()
        if not text:
            return
        if not model:
            self.status.config(text="Enter an Ollama model name, for example gemma3:1b.", fg=DANGER)
            return

        self.entry.delete(0, "end")
        self.placeholder_visible = False
        self.entry.config(fg=TEXT)
        self.say("You", text)
        self.pending = True
        self.status.config(text=f"Waiting for {model}…", fg=MUTED)
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *self.history,
            {"role": "user", "content": text},
        ]
        worker = threading.Thread(
            target=self._request_reply,
            args=(text, model, messages),
            daemon=True,
        )
        worker.start()
        self.after(100, self._poll_result)

    def _request_reply(self, text, model, messages):
        try:
            answer = ask_ollama(messages, model)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace").strip()
            if detail:
                try:
                    error_body = json.loads(detail)
                    if isinstance(error_body, dict):
                        detail = str(error_body.get("error") or detail)
                except json.JSONDecodeError:
                    pass
            self.results.put((text, model, None, f"Ollama returned HTTP {exc.code}: {detail or exc.reason}"))
        except urllib.error.URLError as exc:
            self.results.put((
                text, model, None,
                f"Couldn't connect to Ollama at localhost:11434 ({exc.reason}). "
                "Install and start Ollama, then pull the selected model.",
            ))
        except TimeoutError:
            self.results.put((
                text, model, None,
                "Ollama took too long to respond. Try again or choose a smaller installed model.",
            ))
        except OSError as exc:
            self.results.put((
                text, model, None,
                f"Ollama couldn't complete the local request ({exc}). Check that it is running.",
            ))
        except ValueError as exc:
            self.results.put((text, model, None, str(exc)))
        else:
            self.results.put((text, model, answer, None))

    def _poll_result(self):
        try:
            text, model, answer, error = self.results.get_nowait()
        except queue.Empty:
            self.after(100, self._poll_result)
            return

        self.pending = False
        if error:
            self.say("Buddy", error)
            self.status.config(text="Not connected • Check Ollama and the selected model.", fg=DANGER)
            return

        self.history.extend((
            {"role": "user", "content": text},
            {"role": "assistant", "content": answer},
        ))
        self.history = self.history[-20:]
        self.say("Buddy", answer)
        self.status.config(text=f"Connected to local model: {model}", fg=SUCCESS)
