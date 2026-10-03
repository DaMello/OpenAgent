from __future__ import annotations

import uuid

import keyring

from .config import Settings
from .db import connect


class CredentialVault:
    """OS-backed credential store.

    Passwords are stored through keyring. SQLite stores only metadata and a secret reference.
    The model should never be given the raw value returned by _get_secret_for_tool().
    """

    SERVICE_PREFIX = "OpenAgent"

    def __init__(self, settings: Settings):
        self.settings = settings

    def put(self, domain: str, username: str, password: str) -> int:
        domain = domain.strip().lower()
        username = username.strip()
        secret_ref = f"credential:{domain}:{uuid.uuid4()}"
        service = f"{self.SERVICE_PREFIX}:{domain}"
        keyring.set_password(service, secret_ref, password)

        with connect(self.settings.paths.database) as conn:
            cur = conn.execute(
                """
                INSERT INTO vault_entries(domain, username, secret_ref)
                VALUES (?, ?, ?)
                """,
                (domain, username, secret_ref),
            )
            return int(cur.lastrowid)

    def list_metadata(self) -> list[dict[str, object]]:
        with connect(self.settings.paths.database) as conn:
            rows = conn.execute(
                "SELECT id, domain, username, secret_ref, created_at FROM vault_entries ORDER BY domain"
            ).fetchall()
        return [dict(row) for row in rows]

    def has_domain(self, domain: str) -> bool:
        with connect(self.settings.paths.database) as conn:
            row = conn.execute(
                "SELECT 1 FROM vault_entries WHERE domain = ? LIMIT 1",
                (domain.strip().lower(),),
            ).fetchone()
        return row is not None

    def _get_secret_for_tool(self, entry_id: int) -> tuple[str | None, str]:
        with connect(self.settings.paths.database) as conn:
            row = conn.execute(
                "SELECT domain, username, secret_ref FROM vault_entries WHERE id = ?",
                (entry_id,),
            ).fetchone()
        if not row:
            raise KeyError(entry_id)

        service = f"{self.SERVICE_PREFIX}:{row['domain']}"
        secret = keyring.get_password(service, row["secret_ref"])
        if secret is None:
            raise RuntimeError("credential metadata exists but OS secret is missing")
        return row["username"], secret
