from __future__ import annotations

from .config import Settings
from .defaults import DEFAULT_IDENTITY


def load_identity(settings: Settings) -> str:
    path = settings.paths.identity_file
    if path.exists():
        return path.read_text(encoding="utf-8")
    return DEFAULT_IDENTITY
