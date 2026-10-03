from __future__ import annotations

from .config import Settings
from .db import initialize
from .defaults import DEFAULT_IDENTITY


def bootstrap(settings: Settings | None = None) -> Settings:
    settings = settings or Settings.load()
    p = settings.paths
    p.create()
    initialize(p.database)

    if not p.identity_file.exists():
        p.identity_file.write_text(DEFAULT_IDENTITY, encoding="utf-8")

    notice = p.credentials / "README.txt"
    if not notice.exists():
        notice.write_text(
            "OpenAgent does not store plaintext passwords in this directory.\n"
            "Credential metadata lives in data/openagent.db.\n"
            "Secret values are stored through the operating-system credential store via keyring.\n",
            encoding="utf-8",
        )

    marker = p.runtime / "BOOTSTRAPPED"
    marker.write_text("OpenAgent runtime initialized.\n", encoding="utf-8")
    return settings
