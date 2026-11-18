# MindMate – Smart Study Companion

A dark-themed desktop study app built with **Python + Tkinter** (standard library only, no extra installs).

## Features
Dashboard (stats, daily quote, quick navigation) · Notes (create/edit/delete/search) · Study Planner (pending/completed, priority, due) · Flashcards (reveal, navigate, shuffle) · Focus Timer (25-min Pomodoro, breaks, start/pause/reset, completion alert) · Study Buddy (interactive local AI chat with conversation context and quick prompts).
All data is saved automatically to `data/mindmate_data.json`.

## Study Buddy AI
The Study Buddy uses [Ollama](https://ollama.com/download) to run a language model locally. Chat is processed on your machine, with no API key or per-request fees.

1. Install and start Ollama.
2. In a terminal, download the default model: `ollama pull gemma3:1b`.
3. Run MindMate. In Study Buddy, you can change the model name to any model you have installed with Ollama.

Ollama must be running on its default local address (`localhost:11434`). The Study Buddy explains connection and missing-model errors in the chat.

## Install & run
1. Install **Python 3.9+** from python.org (on Windows keep "tcl/tk and IDLE" ticked; on Ubuntu: `sudo apt install python3-tk`).
2. Extract the ZIP and open the `MindMate` folder in **VS Code** (File > Open Folder).
3. Install the Python extension in VS Code, then open a terminal (Ctrl+`).
4. *(Optional)* create a virtual environment: `python -m venv .venv` then activate it.
5. `pip install -r requirements.txt` (nothing is actually required).
6. Run: `python main.py`  (macOS/Linux: `python3 main.py`)

Run the Study Buddy API tests with `python -m unittest discover -s tests`.

## Structure
```
main.py            app window, sidebar, navigation
database/          JSON storage layer
mindmate/          theme.py (shared widgets) + one module per screen
data/              saved user data
```
## Troubleshooting
`No module named tkinter` → install Tk (see step 1). Delete `data/mindmate_data.json` to reset all data.
