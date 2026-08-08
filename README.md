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
core/            intent_router, llm_router, context_engine, config_loader
interfaces/      web/telegram интерфейсы (появятся в Phase 2)
workflows/       presentation/report/email воркфлоу (Phase 1)
storage/         локальное хранилище задач (JSON на Phase 0, без Supabase)
integrations/    obsidian, bitrix, fusionpos, telegram — коннекторы
vault/           Obsidian vault: system/ (конфиги), architecture/ (ADR), sessions/
tests/           pytest smoke-тесты для core/storage/integrations
```

Архитектурные решения по Phase 0 (границы скоупа, порядок сборки) — в [ADR-004](vault/architecture/ADR-004-phase0-scaffold.md).

## Запуск (Phase 0)
```bash
pip install -r requirements.txt
python -m pytest -q
```

Phase 0 — чисто backend-скелет на Python: нет Next.js/UI, нет Postgres/Docker, нет реальных вызовов LLM или внешних API (Bitrix/FusionPOS/Telegram — структурные заглушки). Подробности и обоснование — в ADR-004.

## Статус
Текущая фаза и активная задача — см. [.planning/STATE.md](.planning/STATE.md).
