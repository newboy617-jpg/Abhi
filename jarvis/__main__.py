"""Start JARVIS:  python -m jarvis

With JARVIS_PHONE_NAME / JARVIS_PHONE_ADDRESS / JARVIS_PHONE_IP set in .env, Jarvis waits
in standby and greets you as soon as your phone comes within range of your room.
"""

import argparse
import os
import threading

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from . import skills
from .brain import Brain
from .presence import PresenceDetector
from .voice import Voice

SLEEP_WORDS = ("go to sleep", "sleep", "goodbye", "bye", "good night", "that's all", "stand by")
EXIT_WORDS = ("exit", "quit", "shut down", "shutdown", "power off")


def main():
    parser = argparse.ArgumentParser(description="JARVIS personal assistant")
    parser.add_argument("--text", action="store_true", help="type instead of using the microphone")
    parser.add_argument("--mute", action="store_true", help="print replies instead of speaking")
    parser.add_argument("--no-presence", action="store_true", help="don't wait for your phone")
    args = parser.parse_args()

    voice = Voice(use_mic=not args.text, speak_aloud=not args.mute)
    if not args.text and not voice.can_listen:
        print("(No microphone found - switching to typing mode.)")
    brain = Brain()

    arrived = threading.Event()
    left = threading.Event()

    detector = None
    phone_configured = any(
        os.environ.get(k) for k in ("JARVIS_PHONE_NAME", "JARVIS_PHONE_ADDRESS", "JARVIS_PHONE_IP")
    )
    if phone_configured and not args.no_presence:
        detector = PresenceDetector(
            phone_name=os.environ.get("JARVIS_PHONE_NAME", ""),
            phone_address=os.environ.get("JARVIS_PHONE_ADDRESS", ""),
            phone_ip=os.environ.get("JARVIS_PHONE_IP", ""),
            rssi_threshold=int(os.environ.get("JARVIS_RSSI_THRESHOLD", "-80")),
            away_after=int(os.environ.get("JARVIS_AWAY_SECONDS", "90")),
            on_arrive=lambda: (left.clear(), arrived.set()),
            on_leave=lambda: (arrived.clear(), left.set()),
        )
        detector.start()

    try:
        if detector is None:
            voice.say(skills.greeting())
            session(voice, brain, left)
            return
        while True:
            print("JARVIS is on standby, waiting for your phone...")
            standby(voice, arrived)
            arrived.clear()
            voice.say(skills.welcome_back())
            if session(voice, brain, left) == "exit":
                return
    except KeyboardInterrupt:
        print()
    finally:
        if detector:
            detector.stop()
        voice.say("Shutting down. Goodbye, sir.")


def standby(voice, arrived):
    """Block until the phone arrives (or, with a microphone, until you say 'Jarvis')."""
    while not arrived.is_set():
        if voice.can_listen:
            heard = voice.listen(timeout=3, phrase_limit=4).lower()
            if "jarvis" in heard:
                return
        else:
            arrived.wait(1)


def session(voice, brain, left):
    """Talk until you send Jarvis to sleep or your phone leaves. Returns 'sleep' or 'exit'."""
    while True:
        if left.is_set():
            left.clear()
            voice.say("You've left the room, sir. Going on standby.")
            return "sleep"

        command = voice.listen()
        if not command:
            continue
        c = command.lower().replace("jarvis", "").strip(" ,.!?")
        if not c:
            voice.say("Yes, sir?")
            continue

        if any(c == w or c.startswith(w + " ") for w in EXIT_WORDS):
            return "exit"
        if any(c == w or c.startswith(w + " ") for w in SLEEP_WORDS):
            voice.say("Very well, sir. I'll be here if you need me.")
            return "sleep"
        if c in ("forget everything", "clear memory", "reset"):
            brain.reset()
            voice.say("Memory cleared, sir.")
            continue

        reply = skills.handle(c)
        if reply is None:
            print("(thinking...)")
            reply = brain.think(command)
        voice.say(reply)


if __name__ == "__main__":
    main()
