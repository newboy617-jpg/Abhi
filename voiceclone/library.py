"""Your saved voices. Each one is a folder holding a cleaned sample and a profile:

    voices/
      abhi/
        reference.wav
        profile.json
"""

import json
import os
import re
import shutil
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from . import audio

DEFAULT_DIR = Path(os.environ.get("VOICECLONE_DIR", Path(__file__).resolve().parent.parent / "voices"))


@dataclass
class Voice:
    name: str
    folder: Path = field(repr=False)
    language: str = "en"
    seconds: float = 0.0
    source: str = ""
    consent: str = ""
    created: str = ""

    @property
    def reference(self) -> Path:
        return self.folder / "reference.wav"


def slugify(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.strip().lower()).strip("-")
    if not slug:
        raise ValueError("Give the voice a name with at least one letter or number.")
    return slug


class VoiceLibrary:
    def __init__(self, folder=DEFAULT_DIR):
        self.folder = Path(folder)

    def add(self, name: str, wav, *, consent: str, language: str = "en", source: str = "") -> Voice:
        """Save a new voice from raw audio. Returns the saved voice."""
        if not consent.strip():
            raise ValueError("Record who gave permission to clone this voice.")
        wav = audio.clean_reference(wav)
        seconds = audio.duration(wav)
        if seconds < audio.MIN_SECONDS:
            raise ValueError(
                f"Only {seconds:.1f} s of speech found. Use at least {audio.MIN_SECONDS} s "
                f"(10 to 30 s of clear talking works best)."
            )

        folder = self.folder / slugify(name)
        folder.mkdir(parents=True, exist_ok=True)
        voice = Voice(
            name=name.strip(),
            folder=folder,
            language=language,
            seconds=round(seconds, 1),
            source=source,
            consent=consent.strip(),
            created=datetime.now().isoformat(timespec="seconds"),
        )
        audio.save(voice.reference, wav)
        profile = {k: v for k, v in asdict(voice).items() if k != "folder"}
        (folder / "profile.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")
        return voice

    def get(self, name: str) -> Voice:
        folder = self.folder / slugify(name)
        profile = folder / "profile.json"
        if not profile.exists():
            known = ", ".join(self.names()) or "none yet"
            raise KeyError(f"No voice called '{name}'. Saved voices: {known}")
        data = json.loads(profile.read_text(encoding="utf-8"))
        return Voice(folder=folder, **data)

    def all(self) -> list[Voice]:
        if not self.folder.exists():
            return []
        voices = []
        for profile in sorted(self.folder.glob("*/profile.json")):
            data = json.loads(profile.read_text(encoding="utf-8"))
            voices.append(Voice(folder=profile.parent, **data))
        return voices

    def names(self) -> list[str]:
        return [v.name for v in self.all()]

    def remove(self, name: str):
        voice = self.get(name)
        shutil.rmtree(voice.folder)
