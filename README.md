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
core/            intent_router, llm_router, llm_dispatch, llm_client (Anthropic), ollama_client,
                 context_engine, config_loader, quality_assurance, mentoring, learning_loop,
                 estimation, reminders, scheduler
interfaces/      api.py (FastAPI-мост для web/), telegram_bot.py (реальный диспетчер)
workflows/       engine.py (interface-agnostic движок) + presentation/report/email воркфлоу
storage/         локальное хранилище задач и decisions (JSON, без Supabase)
integrations/    obsidian (реальный), bitrix/fusionpos/telegram/google_calendar — заглушки
vault/           Obsidian vault: system/ (конфиги), architecture/ (ADR), sessions/
tests/           pytest-сьют для core/storage/integrations/workflows/interfaces
web/             Next.js 15 MVP UI — чат-экран, только классификация (см. ADR-006)
```

Архитектурные решения: [ADR-004](vault/architecture/ADR-004-phase0-scaffold.md) (backend-скелет), [ADR-005](vault/architecture/ADR-005-phase1-workflows.md) (interface-agnostic воркфлоу), [ADR-006](vault/architecture/ADR-006-phase2-scope-and-ui.md) (Web UI MVP), [ADR-007](vault/architecture/ADR-007-ollama-primary.md)/[ADR-008](vault/architecture/ADR-008-ollama-model-tiers.md) (LLM-провайдер и модели Ollama).

## Запуск (backend)
```bash
pip install -r requirements.txt
python -m pytest -q
uvicorn interfaces.api:app --port 8000
```

Воркфлоу (`workflows/`) полностью тестируются без реального LLM-ключа — LLM-вызовы и человеческий ввод инжектируются (см. ADR-005). Primary LLM сейчас — локальная Ollama (см. ADR-007/008), не Anthropic. Bitrix/FusionPOS/Telegram/Google Calendar — структурные заглушки без реальных API-вызовов.

## Запуск (web MVP)
```bash
cd web
npm install
npm run dev
```

Next.js проксирует `/backend/*` на FastAPI (`JARVIS_API_URL`, по умолчанию `http://localhost:8000`) — backend должен быть поднят отдельно. Или запусти оба сразу через `.claude/launch.json` (backend + web).

## Статус
Текущая фаза и активная задача — см. [.planning/STATE.md](.planning/STATE.md).
