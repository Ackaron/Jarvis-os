# Jarvis OS

Автономный ИИ-помощник для управления задачами Виктора (ИНТЦ, Bootlegger, Дом, Образование) — учится на правках, маршрутизирует задачи между LLM и хранит память в Obsidian-vault.

## Source of Truth
1. [PROJECT_IDEA.md](PROJECT_IDEA.md) — видение, боль, пользовательские сценарии, MVP-скоуп.
2. [SPECIFICATION.md](SPECIFICATION.md) — технический чертёж: схема данных, API, routing.yaml, воркфлоу, UI wireframes.
3. [JARVIS_OS_ARCHITECTURE.md](JARVIS_OS_ARCHITECTURE.md) — полная архитектура и storage structure.
4. [CLAUDE.md](CLAUDE.md) — GSD-методология проекта (Planner → Executor → Verifier).
5. [.planning/ROADMAP.md](.planning/ROADMAP.md) / [.planning/STATE.md](.planning/STATE.md) — текущая фаза и атомарные задачи.
6. [vault/](vault/) — Obsidian-хаб: ADR, сессии, память проекта.

## Структура репозитория
```
core/            intent_router, llm_router, llm_client, context_engine, config_loader,
                 quality_assurance, mentoring
interfaces/      web/telegram интерфейсы (появятся в Phase 2)
workflows/       engine.py (interface-agnostic движок) + presentation/report/email воркфлоу
storage/         локальное хранилище задач и decisions (JSON, без Supabase)
integrations/    obsidian (реальный), bitrix/fusionpos/telegram — структурные заглушки
vault/           Obsidian vault: system/ (конфиги), architecture/ (ADR), sessions/
tests/           pytest-сьют для core/storage/integrations/workflows
```

Архитектурные решения: [ADR-004](vault/architecture/ADR-004-phase0-scaffold.md) (Phase 0 — backend-скелет), [ADR-005](vault/architecture/ADR-005-phase1-workflows.md) (Phase 1 — interface-agnostic воркфлоу, LLM-вызовы через DI).

## Запуск
```bash
pip install -r requirements.txt
python -m pytest -q
```

Воркфлоу (`workflows/`) полностью тестируются без реального `ANTHROPIC_API_KEY` — LLM-вызовы и человеческий ввод инжектируются (см. ADR-005). Ключ нужен только для реального прогона генерации. Bitrix/FusionPOS/Telegram — структурные заглушки без реальных API-вызовов (см. ADR-004).

## Статус
Текущая фаза и активная задача — см. [.planning/STATE.md](.planning/STATE.md).
