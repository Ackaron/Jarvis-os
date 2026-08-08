from core.quality_assurance import build_checklist, format_qa_prompt


def test_build_checklist_uses_stakeholder_usual_checks():
    stakeholder = {"metadata": {"usual_checks": ["Логотипы резидентов", "Цвета бренда"]}}
    assert build_checklist(stakeholder) == ["Логотипы резидентов", "Цвета бренда"]


def test_build_checklist_falls_back_to_generic_for_new_stakeholder():
    assert build_checklist({"metadata": {}}) == ["Данные проверены", "Форматирование корректно"]


def test_build_checklist_falls_back_when_stakeholder_none():
    assert build_checklist(None) == ["Данные проверены", "Форматирование корректно"]


def test_format_qa_prompt_lists_each_item():
    stakeholder = {"metadata": {"usual_checks": ["A", "B"]}}
    prompt = format_qa_prompt(stakeholder)
    assert "☐ A" in prompt
    assert "☐ B" in prompt
