from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReasoningMode(str, Enum):
    INSTANT = "instant"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"
    ULTRA = "ultra"


@dataclass(frozen=True)
class ModeProfile:
    think: bool
    num_predict: int
    review_passes: int
    guidance: str


PROFILES: dict[ReasoningMode, ModeProfile] = {
    ReasoningMode.INSTANT: ModeProfile(
        think=False,
        num_predict=2048,
        review_passes=0,
        guidance="Answer directly. Use the minimum deliberation needed.",
    ),
    ReasoningMode.MEDIUM: ModeProfile(
        think=True,
        num_predict=4096,
        review_passes=1,
        guidance="Think through the task, then give a concise result.",
    ),
    ReasoningMode.HIGH: ModeProfile(
        think=True,
        num_predict=8192,
        review_passes=1,
        guidance="Plan, execute mentally, verify assumptions, then answer.",
    ),
    ReasoningMode.MAX: ModeProfile(
        think=True,
        num_predict=16384,
        review_passes=2,
        guidance="Use a deep plan, check alternatives, inspect failure modes, and self-review.",
    ),
    ReasoningMode.ULTRA: ModeProfile(
        think=True,
        num_predict=16384,
        review_passes=2,
        guidance="Handled by the four-agent Ultra Think orchestrator.",
    ),
}
