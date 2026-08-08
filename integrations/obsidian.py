"""Low-level file access to the Obsidian vault (source of truth, see PROJECT_IDEA.md).

Phase 0 talks to the vault directly on the filesystem — no Obsidian REST API
plugin dependency (see ADR-004). core.context_engine builds on top of this.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml

FRONTMATTER_DELIMITER = "---"


class NoteNotFoundError(FileNotFoundError):
    """Raised when a requested vault note does not exist."""


class ObsidianVault:
    def __init__(self, vault_path: Path):
        self.vault_path = Path(vault_path)

    def _resolve(self, relative_path: str) -> Path:
        return self.vault_path / relative_path

    def read_note(self, relative_path: str) -> str:
        path = self._resolve(relative_path)
        if not path.exists():
            raise NoteNotFoundError(f"Note not found in vault: {relative_path}")
        return path.read_text(encoding="utf-8")

    def write_note(self, relative_path: str, content: str) -> None:
        path = self._resolve(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def note_exists(self, relative_path: str) -> bool:
        return self._resolve(relative_path).exists()

    def list_notes(self, subfolder: str = "") -> list[Path]:
        folder = self._resolve(subfolder)
        if not folder.exists():
            return []
        return sorted(folder.glob("*.md"))

    @staticmethod
    def parse_frontmatter(content: str) -> tuple[dict, str]:
        """Splits a note into (yaml_frontmatter_dict, body). Returns ({}, content)
        if there's no valid frontmatter block."""
        lines = content.splitlines()
        if not lines or lines[0].strip() != FRONTMATTER_DELIMITER:
            return {}, content

        for i in range(1, len(lines)):
            if lines[i].strip() == FRONTMATTER_DELIMITER:
                frontmatter_raw = "\n".join(lines[1:i])
                body = "\n".join(lines[i + 1 :]).lstrip("\n")
                metadata = yaml.safe_load(frontmatter_raw) or {}
                return metadata, body

        return {}, content

    def read_note_parsed(self, relative_path: str) -> tuple[dict, str]:
        return self.parse_frontmatter(self.read_note(relative_path))
