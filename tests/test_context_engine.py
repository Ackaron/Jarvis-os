from pathlib import Path

import pytest

from core.context_engine import ContextEngine


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    stakeholders_dir = tmp_path / "stakeholders"
    stakeholders_dir.mkdir()
    (stakeholders_dir / "Трутнев.md").write_text(
        "---\n"
        "focus_areas: [Инвестиции, Продукты]\n"
        "confidence_score: 0.95\n"
        "---\n"
        "Заметки про Трутнева.\n",
        encoding="utf-8",
    )

    templates_dir = tmp_path / "templates" / "presentations"
    templates_dir.mkdir(parents=True)
    (templates_dir / "intc_residents.md").write_text("# Template", encoding="utf-8")

    kb_dir = tmp_path / "knowledge_base" / "intc"
    kb_dir.mkdir(parents=True)
    (kb_dir / "residents.md").write_text("# Residents list", encoding="utf-8")

    return tmp_path


def test_get_stakeholder_parses_frontmatter(vault: Path):
    engine = ContextEngine(vault_path=vault)
    stakeholder = engine.get_stakeholder("Трутнев")
    assert stakeholder is not None
    assert stakeholder["metadata"]["confidence_score"] == 0.95
    assert "Инвестиции" in stakeholder["metadata"]["focus_areas"]
    assert "Заметки" in stakeholder["content"]


def test_get_stakeholder_returns_none_when_missing(vault: Path):
    engine = ContextEngine(vault_path=vault)
    assert engine.get_stakeholder("Несуществующий") is None


def test_list_templates(vault: Path):
    engine = ContextEngine(vault_path=vault)
    templates = engine.list_templates("presentations")
    assert len(templates) == 1
    assert templates[0].name == "intc_residents.md"


def test_get_knowledge(vault: Path):
    engine = ContextEngine(vault_path=vault)
    content = engine.get_knowledge("intc", "residents")
    assert content == "# Residents list"


def test_get_knowledge_missing_returns_none(vault: Path):
    engine = ContextEngine(vault_path=vault)
    assert engine.get_knowledge("intc", "does_not_exist") is None


def test_get_domain_reads_real_domains_config(vault: Path):
    engine = ContextEngine(vault_path=vault)
    domain = engine.get_domain("intc")
    assert domain is not None
    assert domain["name"] == "ИНТЦ"
