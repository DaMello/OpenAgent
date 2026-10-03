from __future__ import annotations

import asyncio

from ..config import Settings
from ..identity import load_identity
from ..providers import QwenOllamaProvider
from .modes import PROFILES, ReasoningMode


ULTRA_ROLES = {
    "planner": "Decompose the task, identify dependencies, propose the best execution plan.",
    "builder": "Work out the implementation or concrete solution in detail.",
    "critic": "Look for errors, unsafe assumptions, missing constraints, and better alternatives.",
    "reviewer": "Independently solve the task and focus on correctness and completeness.",
}


class OpenAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.provider = QwenOllamaProvider(settings)
        self.identity = load_identity(settings)

    def _system(self, mode: ReasoningMode, plan_mode: bool) -> str:
        profile = PROFILES[mode]
        plan = (
            "\n\nPLAN MODE IS ACTIVE. Do not perform or claim external side effects. "
            "Produce a concrete runnable plan and list required permissions."
            if plan_mode
            else ""
        )
        return f"{self.identity}\n\nReasoning mode: {mode.value}.\n{profile.guidance}{plan}"

    async def run(
        self,
        prompt: str,
        *,
        mode: ReasoningMode = ReasoningMode.HIGH,
        plan_mode: bool = False,
    ) -> str:
        if mode is ReasoningMode.ULTRA:
            return await self._ultra(prompt, plan_mode=plan_mode)

        profile = PROFILES[mode]
        messages = [
            {"role": "system", "content": self._system(mode, plan_mode)},
            {"role": "user", "content": prompt},
        ]
        answer = await self.provider.chat(
            messages,
            think=profile.think,
            num_predict=profile.num_predict,
        )

        for _ in range(profile.review_passes):
            answer = await self.provider.chat(
                [
                    {"role": "system", "content": self._system(mode, plan_mode)},
                    {
                        "role": "user",
                        "content": (
                            "Review the draft below for correctness, missing constraints, and unnecessary claims. "
                            "Return a corrected final answer only.\n\n"
                            f"Original task:\n{prompt}\n\nDraft:\n{answer}"
                        ),
                    },
                ],
                think=True,
                num_predict=profile.num_predict,
            )
        return answer

    async def _ultra(self, prompt: str, *, plan_mode: bool) -> str:
        system = self._system(ReasoningMode.MAX, plan_mode)

        async def first_pass(name: str, role: str) -> tuple[str, str]:
            out = await self.provider.chat(
                [
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": f"You are the {name} agent. {role}\n\nTask:\n{prompt}",
                    },
                ],
                think=True,
                num_predict=PROFILES[ReasoningMode.MAX].num_predict,
            )
            return name, out

        first = dict(
            await asyncio.gather(
                *(first_pass(name, role) for name, role in ULTRA_ROLES.items())
            )
        )

        blackboard = "\n\n".join(
            f"## {name}\n{content}" for name, content in first.items()
        )

        async def second_pass(name: str, role: str) -> tuple[str, str]:
            out = await self.provider.chat(
                [
                    {"role": "system", "content": system},
                    {
                        "role": "user",
                        "content": (
                            f"You are the {name} agent. {role}\n"
                            "All four agents have posted a first pass to the shared blackboard. "
                            "Read it, identify disagreements or missing pieces, and propose the best correction.\n\n"
                            f"Task:\n{prompt}\n\nShared blackboard:\n{blackboard}"
                        ),
                    },
                ],
                think=True,
                num_predict=PROFILES[ReasoningMode.MAX].num_predict,
            )
            return name, out

        second = dict(
            await asyncio.gather(
                *(second_pass(name, role) for name, role in ULTRA_ROLES.items())
            )
        )

        reviewed_board = "\n\n".join(
            f"## {name} review\n{content}" for name, content in second.items()
        )

        return await self.provider.chat(
            [
                {"role": "system", "content": system},
                {
                    "role": "user",
                    "content": (
                        "Act as the final synthesizer. Produce one coherent final answer from the shared work. "
                        "Resolve conflicts using evidence and correctness, not majority vote. Do not mention the internal agents.\n\n"
                        f"Task:\n{prompt}\n\nFirst-pass blackboard:\n{blackboard}\n\n"
                        f"Second-pass reviews:\n{reviewed_board}"
                    ),
                },
            ],
            think=True,
            num_predict=PROFILES[ReasoningMode.MAX].num_predict,
        )
