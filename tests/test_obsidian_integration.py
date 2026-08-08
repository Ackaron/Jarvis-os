from pathlib import Path

import pytest

from integrations.obsidian import NoteNotFoundError, ObsidianVault


def test_write_and_read_note(tmp_path: Path):
    vault = ObsidianVault(tmp_path)
    vault.write_note("tasks/example.md", "# Example task")
    assert vault.read_note("tasks/example.md") == "# Example task"


def test_read_missing_note_raises(tmp_path: Path):
    vault = ObsidianVault(tmp_path)
    with pytest.raises(NoteNotFoundError):
        vault.read_note("tasks/missing.md")


def test_parse_frontmatter_splits_metadata_and_body():
    content = "---\nstatus: active\ntags: [a, b]\n---\nBody text here.\n"
    metadata, body = ObsidianVault.parse_frontmatter(content)
    assert metadata == {"status": "active", "tags": ["a", "b"]}
    assert body.strip() == "Body text here."


def test_parse_frontmatter_handles_no_frontmatter():
    content = "Just plain text, no frontmatter."
    metadata, body = ObsidianVault.parse_frontmatter(content)
    assert metadata == {}
    assert body == content


def test_list_notes_returns_only_markdown(tmp_path: Path):
    vault = ObsidianVault(tmp_path)
    vault.write_note("stakeholders/A.md", "a")
    vault.write_note("stakeholders/B.md", "b")
    (tmp_path / "stakeholders" / "notes.txt").write_text("not markdown")
    notes = vault.list_notes("stakeholders")
    assert {p.name for p in notes} == {"A.md", "B.md"}


def test_list_notes_missing_folder_returns_empty(tmp_path: Path):
    vault = ObsidianVault(tmp_path)
    assert vault.list_notes("does_not_exist") == []
