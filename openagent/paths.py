from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def resolve_home() -> Path:
    explicit = os.getenv("OPENAGENT_HOME")
    if explicit:
        return Path(explicit).expanduser().resolve()

    if os.name == "nt":
        preferred = Path("E:/Agent")
        if preferred.exists():
            return preferred.resolve()

    return (Path.home() / ".openagent").resolve()


@dataclass(frozen=True)
class OpenAgentPaths:
    home: Path
    data: Path
    memory: Path
    identity: Path
    models: Path
    credentials: Path
    browser_profile: Path
    workspaces: Path
    downloads: Path
    cache: Path
    logs: Path
    runtime: Path
    database: Path
    identity_file: Path

    @classmethod
    def from_home(cls, home: Path | None = None) -> "OpenAgentPaths":
        root = (home or resolve_home()).resolve()
        data = root / "data"
        identity = root / "identity"
        return cls(
            home=root,
            data=data,
            memory=root / "memory",
            identity=identity,
            models=root / "models",
            credentials=root / "credentials",
            browser_profile=root / "browser-profile",
            workspaces=root / "workspaces",
            downloads=root / "downloads",
            cache=root / "cache",
            logs=root / "logs",
            runtime=root / "runtime",
            database=data / "openagent.db",
            identity_file=identity / "identity.md",
        )

    def create(self) -> None:
        dirs = [
            self.home,
            self.data,
            self.memory,
            self.memory / "profile",
            self.memory / "episodes",
            self.memory / "workspaces",
            self.identity,
            self.models,
            self.credentials,
            self.browser_profile,
            self.workspaces,
            self.downloads,
            self.cache,
            self.logs,
            self.runtime,
        ]
        for path in dirs:
            path.mkdir(parents=True, exist_ok=True)
