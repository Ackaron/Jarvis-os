from pathlib import Path

from core.context_engine import ContextEngine


def test_update_stakeholder_profile_creates_new_note(tmp_path: Path):
    engine = ContextEngine(vault_path=tmp_path)
    result = engine.update_stakeholder_profile(
        "Трутнев", focus_areas=["Инвестиции"], confidence_score=0.5
    )
    assert result["metadata"]["focus_areas"] == ["Инвестиции"]
    assert result["metadata"]["confidence_score"] == 0.5
    assert "updated_at" in result["metadata"]

    reloaded = engine.get_stakeholder("Трутнев")
    assert reloaded["metadata"]["confidence_score"] == 0.5


def test_update_stakeholder_profile_merges_list_fields(tmp_path: Path):
    engine = ContextEngine(vault_path=tmp_path)
    engine.update_stakeholder_profile("Трутнев", focus_areas=["Инвестиции"])
    result = engine.update_stakeholder_profile(
        "Трутнев", focus_areas=["Инвестиции", "Продукты"]
    )
    assert result["metadata"]["focus_areas"] == ["Инвестиции", "Продукты"]


def test_update_stakeholder_profile_overwrites_scalar_fields(tmp_path: Path):
    engine = ContextEngine(vault_path=tmp_path)
    engine.update_stakeholder_profile("Трутнев", interaction_count=1)
    result = engine.update_stakeholder_profile("Трутнев", interaction_count=2)
    assert result["metadata"]["interaction_count"] == 2


def test_update_stakeholder_profile_preserves_body(tmp_path: Path):
    (tmp_path / "stakeholders").mkdir()
    (tmp_path / "stakeholders" / "Трутнев.md").write_text(
        "---\nconfidence_score: 0.1\n---\nСтарые заметки.\n", encoding="utf-8"
    )
    engine = ContextEngine(vault_path=tmp_path)
    result = engine.update_stakeholder_profile("Трутнев", confidence_score=0.9)
    assert "Старые заметки" in result["content"]
    assert result["metadata"]["confidence_score"] == 0.9
