from __future__ import annotations

import argparse
import asyncio

import httpx

from .agent import OpenAgent, ReasoningMode
from .bootstrap import bootstrap
from .providers import QwenOllamaProvider


def cmd_bootstrap() -> int:
    settings = bootstrap()
    print(f"OpenAgent home: {settings.paths.home}")
    print(f"Database:       {settings.paths.database}")
    print(f"Identity:       {settings.paths.identity_file}")
    print("Bootstrap complete.")
    return 0


async def cmd_doctor_async() -> int:
    settings = bootstrap()
    print(f"home       {settings.paths.home}")
    print(f"database   {settings.paths.database}")
    print(f"identity   {settings.paths.identity_file}")
    print(f"ollama     {settings.ollama_url}")
    try:
        provider = QwenOllamaProvider(settings)
        model = await provider.resolve_model()
        print(f"qwen       {model}")
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"qwen       ERROR: {exc}")
        return 1
    print("status     ready")
    return 0


async def cmd_chat_async(mode: ReasoningMode, plan: bool) -> int:
    settings = bootstrap()
    agent = OpenAgent(settings)

    print(f"OpenAgent · {mode.value}{' · PLAN' if plan else ''}")
    print("Type /exit to quit.\n")

    while True:
        try:
            prompt = input("You> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not prompt:
            continue
        if prompt in {"/exit", "/quit"}:
            break
        try:
            answer = await agent.run(prompt, mode=mode, plan_mode=plan)
        except Exception as exc:
            print(f"OpenAgent error: {exc}\n")
            continue
        print(f"\nOpenAgent> {answer}\n")

    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="openagent")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("bootstrap")
    sub.add_parser("doctor")

    chat = sub.add_parser("chat")
    chat.add_argument(
        "--mode",
        choices=[m.value for m in ReasoningMode],
        default=ReasoningMode.HIGH.value,
    )
    chat.add_argument("--plan", action="store_true")

    args = parser.parse_args()

    if args.command in {None, "bootstrap"}:
        code = cmd_bootstrap()
    elif args.command == "doctor":
        code = asyncio.run(cmd_doctor_async())
    elif args.command == "chat":
        code = asyncio.run(
            cmd_chat_async(ReasoningMode(args.mode), plan=bool(args.plan))
        )
    else:
        parser.print_help()
        code = 2

    raise SystemExit(code)


if __name__ == "__main__":
    main()
