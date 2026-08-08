from pathlib import Path

from integrations.obsidian import ObsidianVault


def test_render_frontmatter_roundtrips_with_parse():
    metadata = {"status": "active", "focus_areas": ["Инвестиции", "Продукты"]}
    body = "Заметки.\n"
    rendered = ObsidianVault.render_frontmatter(metadata, body)

    parsed_metadata, parsed_body = ObsidianVault.parse_frontmatter(rendered)
    assert parsed_metadata == metadata
    assert parsed_body == body


def test_render_frontmatter_without_metadata_returns_body_unchanged():
    body = "Just text."
    assert ObsidianVault.render_frontmatter({}, body) == body


def test_write_note_with_frontmatter_then_read_back(tmp_path: Path):
    vault = ObsidianVault(tmp_path)
    vault.write_note_with_frontmatter(
        "stakeholders/Трутнев.md", {"confidence_score": 0.9}, "Notes\n"
    )
    metadata, body = vault.read_note_parsed("stakeholders/Трутнев.md")
    assert metadata == {"confidence_score": 0.9}
    assert body == "Notes\n"
