"""Speaking (text-to-speech) and listening (speech recognition)."""

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:
    sr = None


class Voice:
    def __init__(self, use_mic: bool = True, speak_aloud: bool = True):
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
