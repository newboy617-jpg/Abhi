"""Speaking (text-to-speech) and listening (speech recognition)."""

import os

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None


def load_cloned_voice(name: str):
    """Speak with a voice made by `python -m voiceclone` (set JARVIS_VOICE in .env)."""
    try:
        from voiceclone import VoiceCloner, VoiceLibrary, audio

        voice = VoiceLibrary().get(name)
        if not audio.can_play():
            raise RuntimeError("no speakers found")
        cloner = VoiceCloner()
        cloner.model("turbo")  # load (and on the first run download) it now, not mid-conversation
        return cloner, voice
    except Exception as e:
        print(f"(Can't use the cloned voice '{name}': {e}. Using the built-in voice.)")
        return None


class Voice:
    def __init__(self, use_mic: bool = True, speak_aloud: bool = True):
        self.clone = None
        if speak_aloud and os.environ.get("JARVIS_VOICE"):
            self.clone = load_cloned_voice(os.environ["JARVIS_VOICE"])

        self.engine = None
        if speak_aloud and pyttsx3 is not None:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 180)
                # Prefer a male English voice if one is installed, for the classic Jarvis feel.
                for v in self.engine.getProperty("voices"):
                    name = (v.name or "").lower()
                    if "david" in name or "daniel" in name or "male" in name:
                        self.engine.setProperty("voice", v.id)
                        break
            except Exception:
                self.engine = None

        self.recognizer = None
        self.mic = None
        if use_mic and sr is not None:
            try:
                self.mic = sr.Microphone()
                self.recognizer = sr.Recognizer()
                self.recognizer.pause_threshold = 0.8
                with self.mic as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
            except Exception:
                self.mic = None
                self.recognizer = None

    @property
    def can_listen(self) -> bool:
        return self.mic is not None

    def say(self, text: str):
        print(f"JARVIS: {text}")
        if self.clone is not None:
            from voiceclone import audio

            cloner, voice = self.clone
            try:
                wav, sr = cloner.speak(voice, text, language="en", fast=True)
                audio.play(wav, sr)
                return
            except Exception as e:
                print(f"(Cloned voice failed: {e}. Switching to the built-in voice.)")
                self.clone = None
        if self.engine is not None:
            self.engine.say(text)
            self.engine.runAndWait()

    def listen(self, timeout: float = 8, phrase_limit: float = 12) -> str:
        """Return what the user said (lower-case), or "" if nothing was understood."""
        if not self.can_listen:
            try:
                return input("You: ").strip()
            except EOFError:
                return "exit"

        with self.mic as source:
            print("Listening...")
            try:
                audio = self.recognizer.listen(
                    source, timeout=timeout, phrase_time_limit=phrase_limit
                )
            except sr.WaitTimeoutError:
                return ""
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"You: {text}")
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            print("(Speech service unavailable - type instead)")
            return input("You: ").strip()
