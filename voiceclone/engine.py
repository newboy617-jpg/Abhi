"""The cloning engine, built on Resemble AI's open-source Chatterbox models (MIT licence).

Three models are used, picked automatically:
  standard      English, best quality, with emotion control
  turbo         English, several times faster (good for live use such as Jarvis)
  multilingual  23 languages including Hindi

Model weights (a few GB) download from Hugging Face the first time each one is used.
Every clip is stamped with Resemble's inaudible Perth watermark so it can later be
identified as AI-generated (see `python -m voiceclone check`).
"""

import re

import numpy as np

LANGUAGES = {
    "ar": "Arabic", "da": "Danish", "de": "German", "el": "Greek", "en": "English",
    "es": "Spanish", "fi": "Finnish", "fr": "French", "he": "Hebrew", "hi": "Hindi",
    "it": "Italian", "ja": "Japanese", "ko": "Korean", "ms": "Malay", "nl": "Dutch",
    "no": "Norwegian", "pl": "Polish", "pt": "Portuguese", "ru": "Russian",
    "sv": "Swedish", "sw": "Swahili", "tr": "Turkish", "zh": "Chinese",
}

# Split after sentence-ending punctuation (including the Hindi danda and CJK full stops).
_SENTENCE_END = re.compile(r"(?<=[.!?।])\s+|(?<=[。！？])")


def split_text(text: str, max_chars: int = 250) -> list[str]:
    """Break long text into sentence-sized chunks the model can say in one go."""
    pieces = []
    for sentence in _SENTENCE_END.split(" ".join(text.split())):
        sentence = sentence.strip()
        while len(sentence) > max_chars:
            cut = sentence.rfind(", ", 0, max_chars) + 1
            if cut < max_chars // 2:
                cut = sentence.rfind(" ", 0, max_chars)
            if cut <= 0:
                cut = max_chars
            pieces.append(sentence[:cut].strip())
            sentence = sentence[cut:].strip()
        if sentence:
            pieces.append(sentence)

    chunks, current = [], ""
    for piece in pieces:
        if current and len(current) + 1 + len(piece) > max_chars:
            chunks.append(current)
            current = piece
        else:
            current = f"{current} {piece}".strip()
    if current:
        chunks.append(current)
    return chunks


class ModelLoadError(RuntimeError):
    pass


def pick_device() -> str:
    import torch

    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


class VoiceCloner:
    def __init__(self, device: str | None = None):
        self.device = device or pick_device()
        self._models = {}
        self._prepared = {}  # model kind -> reference file it is currently set up with

    def model(self, kind: str):
        if kind not in self._models:
            print(f"Loading the {kind} voice model on {self.device} "
                  "(the first run downloads it, which can take a few minutes)...")
            if kind == "turbo":
                from chatterbox.tts_turbo import ChatterboxTurboTTS as Model
            elif kind == "multilingual":
                from chatterbox.mtl_tts import ChatterboxMultilingualTTS as Model
            else:
                from chatterbox.tts import ChatterboxTTS as Model
            try:
                self._models[kind] = Model.from_pretrained(device=self.device)
            except Exception as e:
                raise ModelLoadError(f"Couldn't load the {kind} voice model ({type(e).__name__}: {e}). "
                                   "The first run needs internet to download it.") from e
        return self._models[kind]

    def speak(
        self,
        voice,
        text: str,
        language: str | None = None,
        emotion: float = 0.5,
        cfg_weight: float = 0.5,
        temperature: float = 0.8,
        fast: bool = False,
    ) -> tuple[np.ndarray, int]:
        """Say `text` in a saved voice. Returns (audio samples, sample rate).

        emotion      0.25 calm ... 0.5 natural ... 1.0+ dramatic (not used by turbo)
        cfg_weight   lower (~0.3) for slower, more deliberate speech; 0 reduces the
                     voice's accent when it speaks a language it wasn't recorded in
        temperature  higher gives more varied delivery, lower more consistent
        fast         use the turbo model for English
        """
        if not text.strip():
            raise ValueError("Nothing to say: the text is empty.")
        language = (language or voice.language or "en").lower()
        if language not in LANGUAGES:
            raise ValueError(f"Unsupported language '{language}'. Choose from: {', '.join(LANGUAGES)}")
        kind = "multilingual" if language != "en" else ("turbo" if fast else "standard")

        try:
            return self._generate(kind, voice, text, language, emotion, cfg_weight, temperature)
        except (ModelLoadError, KeyboardInterrupt):
            raise
        except Exception as e:
            if self.device != "mps":
                raise
            # Some operations aren't supported on Apple's GPU in every PyTorch version.
            print(f"(The Mac's GPU couldn't run the voice model: {e}. Switching to the CPU.)")
            self.device = "cpu"
            self._models.clear()
            self._prepared.clear()
            return self._generate(kind, voice, text, language, emotion, cfg_weight, temperature)

    def _generate(self, kind, voice, text, language, emotion, cfg_weight, temperature):
        model = self.model(kind)
        if self._prepared.get(kind) != voice.reference:
            model.prepare_conditionals(str(voice.reference), exaggeration=emotion)
            self._prepared[kind] = voice.reference

        gap = np.zeros(int(0.2 * model.sr), dtype=np.float32)
        parts = []
        for chunk in split_text(text):
            if kind == "turbo":
                wav = model.generate(chunk, temperature=temperature)
            elif kind == "multilingual":
                wav = model.generate(chunk, language_id=language, exaggeration=emotion,
                                     cfg_weight=cfg_weight, temperature=temperature)
            else:
                wav = model.generate(chunk, exaggeration=emotion,
                                     cfg_weight=cfg_weight, temperature=temperature)
            parts += [wav.squeeze(0).cpu().numpy().astype(np.float32), gap]
        return np.concatenate(parts[:-1]), model.sr


def watermark_score(path) -> float:
    """How sure (0 to 1) we are that a clip carries the Perth AI watermark."""
    import librosa
    import perth

    wav, sr = librosa.load(path, sr=None, mono=True)
    return float(perth.PerthImplicitWatermarker().get_watermark(wav, sample_rate=sr))
