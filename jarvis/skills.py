"""Built-in commands Jarvis handles instantly on your computer, without asking Claude."""

import os
import platform
import random
import subprocess
import webbrowser
from datetime import datetime
from urllib.parse import quote_plus

WEBSITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "chatgpt": "https://chatgpt.com",
    "claude": "https://claude.ai",
    "spotify": "https://open.spotify.com",
    "netflix": "https://www.netflix.com",
    "linkedin": "https://www.linkedin.com",
    "maps": "https://maps.google.com",
    "stack overflow": "https://stackoverflow.com",
}

APPS = {
    "Windows": {
        "notepad": "notepad", "calculator": "calc", "paint": "mspaint",
        "command prompt": "cmd", "file explorer": "explorer",
        "vs code": "code", "chrome": "chrome", "settings": "ms-settings:",
    },
    "Darwin": {
        "notes": "Notes", "calculator": "Calculator", "terminal": "Terminal",
        "finder": "Finder", "safari": "Safari", "chrome": "Google Chrome",
        "vs code": "Visual Studio Code", "music": "Music", "settings": "System Settings",
    },
    "Linux": {
        "terminal": "x-terminal-emulator", "calculator": "gnome-calculator",
        "files": "nautilus", "text editor": "gedit", "chrome": "google-chrome",
        "firefox": "firefox", "vs code": "code",
    },
}

GREETINGS = [
    "At your service, sir.",
    "Online and ready, sir.",
    "Good to see you, sir. What can I do for you?",
]


def greeting() -> str:
    hour = datetime.now().hour
    part = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
    return f"Good {part}, sir. JARVIS is online. How may I help you?"


def welcome_back() -> str:
    hour = datetime.now().hour
    part = "morning" if hour < 12 else "afternoon" if hour < 17 else "evening"
    return f"Hello sir, welcome back. Good {part}. How can I help you?"


def _open_app(name: str) -> bool:
    system = platform.system()
    target = APPS.get(system, {}).get(name)
    if target is None:
        return False
    try:
        if system == "Windows":
            os.startfile(target) if target.endswith(":") else subprocess.Popen(target, shell=True)
        elif system == "Darwin":
            subprocess.Popen(["open", "-a", target])
        else:
            subprocess.Popen([target])
        return True
    except Exception:
        return False


def handle(command: str):
    """Try to handle a command locally. Returns a reply string, or None to pass to Claude."""
    c = command.lower().strip().rstrip(".!?")

    if c in ("hi", "hello", "hey", "wake up", "you there", "are you there"):
        return random.choice(GREETINGS)

    if "time" in c and ("what" in c or "tell" in c) and "timer" not in c and len(c.split()) <= 6:
        return f"It's {datetime.now().strftime('%I:%M %p').lstrip('0')}, sir."

    if ("date" in c or "what day" in c) and len(c.split()) <= 6:
        return f"Today is {datetime.now().strftime('%A, %d %B %Y')}."

    if c.startswith("play "):
        query = c[5:].replace(" on youtube", "").strip()
        webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
        return f"Playing {query} on YouTube, sir."

    for prefix in ("search google for ", "google ", "search for ", "search "):
        if c.startswith(prefix):
            query = c[len(prefix):].strip()
            webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
            return f"Here are the Google results for {query}, sir."

    if c.startswith("open ") or c.startswith("launch ") or c.startswith("start "):
        target = c.split(" ", 1)[1].strip()
        if target in WEBSITES:
            webbrowser.open(WEBSITES[target])
            return f"Opening {target}, sir."
        if _open_app(target):
            return f"Launching {target}, sir."
        if "." in target and " " not in target:
            webbrowser.open(f"https://{target}")
            return f"Opening {target}, sir."
        return None  # let Claude respond

    return None
