"""Clone a voice from a short recording and make it say anything."""

import os

# On Apple Silicon, run any operation the GPU doesn't support on the CPU instead of failing.
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

from .library import Voice, VoiceLibrary

__all__ = ["Voice", "VoiceLibrary", "VoiceCloner"]


def __getattr__(name):
    # Imported lazily so that listing or adding voices doesn't load PyTorch.
    if name == "VoiceCloner":
        from .engine import VoiceCloner
        return VoiceCloner
    raise AttributeError(name)
