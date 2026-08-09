from core.system_prompt import BASE_SYSTEM_PROMPT, with_base


def test_base_prompt_explicitly_denies_being_claude_or_gpt():
    # The prompt legitimately mentions "не Claude, не GPT" to be honest about
    # what it *isn't* — this checks for that negation, not word absence.
    lowered = BASE_SYSTEM_PROMPT.lower()
    assert "не claude" in lowered
    assert "не gpt" in lowered
    assert "anthropic" not in lowered
    assert "openai" not in lowered


def test_base_prompt_names_itself_jarvis():
    assert "Jarvis OS" in BASE_SYSTEM_PROMPT


def test_with_base_returns_base_alone_when_no_task_prompt():
    assert with_base("") == BASE_SYSTEM_PROMPT
    assert with_base() == BASE_SYSTEM_PROMPT


def test_with_base_appends_task_prompt():
    result = with_base("Ты составляешь формальные деловые письма.")
    assert result.startswith(BASE_SYSTEM_PROMPT)
    assert result.endswith("Ты составляешь формальные деловые письма.")
