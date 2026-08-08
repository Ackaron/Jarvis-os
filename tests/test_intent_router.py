from core.intent_router import classify_intent

DOMAINS_CONFIG = {
    "domains": {
        "intc": {"name": "ИНТЦ", "aliases": ["интц"]},
        "bootlegger": {"name": "Bootlegger", "aliases": ["бар"]},
    }
}


def test_classifies_presentation():
    result = classify_intent("Нужна презентация резидентов ИНТЦ для Трутнева", DOMAINS_CONFIG)
    assert result.task_type == "presentation"
    assert result.domain == "intc"
    assert result.autonomous is False


def test_classifies_email_as_autonomous():
    result = classify_intent("Напиши письмо в УК про статус резидента", DOMAINS_CONFIG)
    assert result.task_type == "email"
    assert result.autonomous is True


def test_classifies_report_for_bootlegger_domain():
    result = classify_intent("Сделай отчет по бару за неделю", DOMAINS_CONFIG)
    assert result.task_type == "report"
    assert result.domain == "bootlegger"


def test_research_takes_priority_over_analysis():
    result = classify_intent("Нужен анализ рынка для новой инициативы", DOMAINS_CONFIG)
    assert result.task_type == "research"


def test_plain_analysis_without_market_keyword():
    result = classify_intent("Сделай анализ прошлых продаж", DOMAINS_CONFIG)
    assert result.task_type == "analysis"


def test_unclassified_task_falls_back_to_other():
    result = classify_intent("Просто зайди и посмотри что там", DOMAINS_CONFIG)
    assert result.task_type == "other"
    assert result.autonomous is False


def test_critical_urgency_detected():
    result = classify_intent("Срочно как можно быстрее письмо в фонд", DOMAINS_CONFIG)
    assert result.urgency == "critical"


def test_stakeholder_matched_when_known():
    result = classify_intent(
        "Презентация для Трутнева",
        DOMAINS_CONFIG,
        known_stakeholders=["Трутнев", "Чекунков"],
    )
    assert result.stakeholder == "Трутнев"


def test_no_stakeholder_when_not_mentioned():
    result = classify_intent(
        "Презентация резидентов",
        DOMAINS_CONFIG,
        known_stakeholders=["Трутнев"],
    )
    assert result.stakeholder is None
