from __future__ import annotations

import os
from dataclasses import dataclass

from .paths import OpenAgentPaths


@dataclass(frozen=True)
class Settings:
    paths: OpenAgentPaths
    ollama_url: str
    model: str | None
    context_window: int
    auto_compact_ratio: float

    @classmethod
    def load(cls) -> "Settings":
        model = os.getenv("OPENAGENT_MODEL", "").strip() or None
        ratio = float(os.getenv("OPENAGENT_AUTO_COMPACT_RATIO", "0.75"))
        ratio = min(max(ratio, 0.25), 0.95)
        return cls(
            paths=OpenAgentPaths.from_home(),
            ollama_url=os.getenv("OPENAGENT_OLLAMA_URL", "http://127.0.0.1:11434").rstrip("/"),
            model=model,
            context_window=int(os.getenv("OPENAGENT_CONTEXT_WINDOW", "131072")),
            auto_compact_ratio=ratio,
        )
