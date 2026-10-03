from __future__ import annotations

from dataclasses import dataclass

from .config import Settings
from .db import connect


@dataclass(frozen=True)
class Memory:
    id: int
    scope: str
    workspace: str | None
    content: str
    importance: float


class MemoryStore:
    VALID_SCOPES = {"profile", "episode", "workspace"}

    def __init__(self, settings: Settings):
        self.settings = settings

    def add(
        self,
        content: str,
        *,
        scope: str = "episode",
        workspace: str | None = None,
        importance: float = 0.5,
    ) -> int:
        if scope not in self.VALID_SCOPES:
            raise ValueError(f"invalid memory scope: {scope}")
        importance = min(max(float(importance), 0.0), 1.0)
        with connect(self.settings.paths.database) as conn:
            cur = conn.execute(
                """
                INSERT INTO memories(scope, workspace, content, importance)
                VALUES (?, ?, ?, ?)
                """,
                (scope, workspace, content.strip(), importance),
            )
            return int(cur.lastrowid)

    def search(
        self,
        query: str,
        *,
        scope: str | None = None,
        workspace: str | None = None,
        limit: int = 12,
    ) -> list[Memory]:
        clauses = ["content LIKE ?"]
        params: list[object] = [f"%{query}%"]

        if scope:
            clauses.append("scope = ?")
            params.append(scope)
        if workspace:
            clauses.append("workspace = ?")
            params.append(workspace)

        params.append(limit)
        sql = f"""
            SELECT id, scope, workspace, content, importance
            FROM memories
            WHERE {' AND '.join(clauses)}
            ORDER BY importance DESC, updated_at DESC
            LIMIT ?
        """
        with connect(self.settings.paths.database) as conn:
            rows = conn.execute(sql, params).fetchall()
        return [
            Memory(
                id=row["id"],
                scope=row["scope"],
                workspace=row["workspace"],
                content=row["content"],
                importance=row["importance"],
            )
            for row in rows
        ]
