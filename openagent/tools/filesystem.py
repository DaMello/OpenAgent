from __future__ import annotations

from pathlib import Path


class WorkspaceFiles:
    """Filesystem tool constrained to one workspace root."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _resolve(self, relative: str | Path) -> Path:
        candidate = (self.root / relative).resolve()
        if candidate != self.root and self.root not in candidate.parents:
            raise PermissionError("path escapes workspace")
        return candidate

    def read_text(self, relative: str | Path) -> str:
        return self._resolve(relative).read_text(encoding="utf-8")

    def write_text(self, relative: str | Path, content: str) -> str:
        target = self._resolve(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        return str(target)

    def list(self, relative: str | Path = ".") -> list[str]:
        target = self._resolve(relative)
        return sorted(p.name for p in target.iterdir())

    def delete(self, relative: str | Path) -> None:
        target = self._resolve(relative)
        if target.is_dir():
            target.rmdir()
        else:
            target.unlink()
