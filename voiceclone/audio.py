"""Loading, cleaning, recording and playing audio."""

import shutil
import subprocess
import tempfile
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

try:
    import sounddevice as sd
except (ImportError, OSError):  # OSError: PortAudio library not installed
    sd = None

SAMPLE_RATE = 24000      # Chatterbox works at 24 kHz
MIN_SECONDS = 5          # the model needs at least this much speech
GOOD_SECONDS = 10        # it listens to the first ~10 s, so aim for this or more
MAX_SECONDS = 30         # anything longer is ignored, so don't keep it
MAX_READ_SECONDS = 180   # how much of a long video or recording to look through

# Formats librosa opens directly; everything else (videos, m4a, aac...) goes through ffmpeg.
SOUNDFILE_TYPES = {".wav", ".flac", ".ogg", ".mp3", ".aiff", ".aif"}

# A short passage with a wide mix of sounds. Reading it gives a good voice sample.
READING_PASSAGE = (
    "The quick brown fox jumps over the lazy dog. "
    "On a bright Monday morning, Priya walked to the market to buy fresh mangoes, "
    "warm bread and a jar of honey. Would you believe the shop was closed? "
    "She laughed, called her brother, and they had chai at the station instead."
)


def parse_time(value) -> float | None:
    """'90', '1:30' or '0:01:30' -> 90.0 seconds. Empty -> None."""
    if value is None or str(value).strip() == "":
        return None
    seconds = 0.0
    try:
        for part in str(value).strip().split(":"):
            seconds = seconds * 60 + float(part)
    except ValueError:
        raise ValueError(f"Can't understand the time '{value}'. Use seconds (90) or minutes:seconds (1:30).")
    return seconds


def find_ffmpeg() -> str | None:
    """ffmpeg from your system, or the copy that comes with the imageio-ffmpeg package."""
    if path := shutil.which("ffmpeg"):
        return path
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def load(path, sr: int = SAMPLE_RATE, start: float | None = None, end: float | None = None) -> np.ndarray:
    """Load the sound from any audio or video file (wav, mp3, m4a, mp4, mkv...) as mono float32.

    `start` and `end` (in seconds) pick out part of the file.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No such file: {path}")
    offset = start or 0.0
    length = None
    if end is not None:
        length = end - offset
        if length <= 0:
            raise ValueError("The end time must be after the start time.")

    ffmpeg = find_ffmpeg()
    if path.suffix.lower() in SOUNDFILE_TYPES or ffmpeg is None:
        try:
            wav, _ = librosa.load(path, sr=sr, mono=True, offset=offset, duration=length)
        except Exception as e:
            raise RuntimeError(
                f"Can't read {path.name}. Install ffmpeg (https://ffmpeg.org) to open videos "
                "and other audio formats."
            ) from e
    else:
        # ffmpeg pulls the soundtrack out of videos and opens every common audio format.
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "audio.wav"
            cmd = [ffmpeg, "-y", "-loglevel", "error", "-ss", str(offset), "-i", str(path)]
            if length is not None:
                cmd += ["-t", str(length)]
            cmd += ["-vn", "-ac", "1", "-ar", str(sr), str(out)]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "does not contain any stream" in result.stderr:
                raise ValueError(f"{path.name} has no sound in it.")
            if result.returncode != 0 or not out.exists():
                reason = result.stderr.strip().splitlines()[-1] if result.stderr.strip() else ""
                raise RuntimeError(f"Couldn't get any audio out of {path.name}. {reason}")
            wav, _ = librosa.load(out, sr=sr, mono=True)

    if wav.size == 0:
        raise ValueError(f"No audio found in {path.name} (check the start and end times).")
    return wav


def isolate_voice(wav: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Strip background music and noise, keeping only the voice (uses Meta's Demucs model)."""
    try:
        import torch
        from demucs.api import Separator
    except ImportError:
        raise RuntimeError("Removing background sound needs demucs. Run: pip install demucs")
    try:
        separator = Separator(model="htdemucs", progress=True)
    except OSError as e:
        raise RuntimeError(f"Couldn't download the background-removal model. Check your internet connection. ({e})")
    _, stems = separator.separate_tensor(torch.from_numpy(wav)[None], sr)
    vocals = stems["vocals"].mean(0).cpu().numpy()
    return librosa.resample(vocals, orig_sr=separator.samplerate, target_sr=sr)


def extract_voice(path, start=None, end=None, isolate: bool = False) -> np.ndarray:
    """Get a voice sample out of an audio or video file.

    Only the first few minutes from `start` are read: that's far more than the model uses.
    """
    start, end = parse_time(start), parse_time(end)
    if end is None:
        end = (start or 0.0) + MAX_READ_SECONDS
    wav = load(path, start=start, end=end)
    if isolate:
        print("Separating the voice from background music and noise...")
        wav = isolate_voice(wav)
    return wav


def clean_reference(wav: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Turn a raw recording into a good cloning sample.

    Cuts silence at the edges, shortens long pauses (the model only hears the first
    few seconds, so they should be packed with speech), and evens out the volume.
    """
    wav = np.asarray(wav, dtype=np.float32)
    if wav.size == 0 or not np.any(wav):
        raise ValueError("The recording is silent.")

    pieces = librosa.effects.split(wav, top_db=40, frame_length=1024, hop_length=256)
    gap = np.zeros(int(0.25 * sr), dtype=np.float32)
    speech = []
    for start, end in pieces:
        if speech:
            speech.append(gap)
        speech.append(wav[start:end])
    wav = np.concatenate(speech)[: MAX_SECONDS * sr]

    wav = wav - np.mean(wav)                     # remove DC offset
    peak = np.max(np.abs(wav))
    if peak > 0:
        wav = wav * (0.9 / peak)                 # normalise to about -1 dBFS
    return wav.astype(np.float32)


def duration(wav: np.ndarray, sr: int = SAMPLE_RATE) -> float:
    return len(wav) / sr


def save(path, wav: np.ndarray, sr: int = SAMPLE_RATE):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    sf.write(path, wav, sr)


def record(seconds: float, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Record from the default microphone."""
    if sd is None:
        raise RuntimeError("Recording needs sounddevice. Run: pip install sounddevice")
    wav = sd.rec(int(seconds * sr), samplerate=sr, channels=1, dtype="float32")
    sd.wait()
    return wav[:, 0]


def can_play() -> bool:
    if sd is None:
        return False
    try:
        sd.query_devices(kind="output")
        return True
    except Exception:
        return False


def play(wav: np.ndarray, sr: int = SAMPLE_RATE):
    if sd is None:
        raise RuntimeError("Playback needs sounddevice. Run: pip install sounddevice")
    sd.play(wav, sr)
    sd.wait()
