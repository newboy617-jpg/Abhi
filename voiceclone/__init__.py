"""Clone a voice from a short recording and make it say anything."""

from .library import Voice, VoiceLibrary

__all__ = ["Voice", "VoiceLibrary", "VoiceCloner"]


def __getattr__(name):
    # Imported lazily so that listing or adding voices doesn't load PyTorch.
    if name == "VoiceCloner":
        from .engine import VoiceCloner
        return VoiceCloner
    raise AttributeError(name)
