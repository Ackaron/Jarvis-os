"""Assembles context for task execution from the Obsidian vault.

Phase 0 scope (ADR-004): stakeholders / templates / knowledge_base lookups via
direct file access (integrations.obsidian.ObsidianVault). No live external
data sources (FusionPOS, Bitrix, Calendar) are queried yet — that's Phase 1+.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from core.config_loader import get_domains_config
from integrations.obsidian import NoteNotFoundError, ObsidianVault

DEFAULT_VAULT_PATH = Path(__file__).resolve().parent.parent / "vault"


class ContextEngine:
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault = ObsidianVault(vault_path or DEFAULT_VAULT_PATH)

    def get_stakeholder(self, name: str) -> Optional[dict]:
        relative_path = f"stakeholders/{name}.md"
        try:
            metadata, body = self.vault.read_note_parsed(relative_path)
        except NoteNotFoundError:
            return None
        return {"name": name, "metadata": metadata, "content": body}

    def get_domain(self, domain_id: str) -> Optional[dict]:
        domains_config = get_domains_config()
        return (domains_config.get("domains") or {}).get(domain_id)

    def list_templates(self, category: Optional[str] = None) -> list[Path]:
        subfolder = f"templates/{category}" if category else "templates"
        return self.vault.list_notes(subfolder)

    def get_knowledge(self, domain: str, topic: str) -> Optional[str]:
        relative_path = f"knowledge_base/{domain}/{topic}.md"
        try:
            return self.vault.read_note(relative_path)
        except NoteNotFoundError:
            return None
