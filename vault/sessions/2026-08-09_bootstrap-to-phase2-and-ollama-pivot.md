---
type: session
status: completed
tags: [gsd, session, phase0, phase1, phase2, ollama, system-prompt]
created: 2026-08-09
updated: 2026-08-09
---

# Сессия: от чистого репозитория до Phase 2 + смена LLM-провайдера

Одна длинная сессия (2026-08-08 → 2026-08-09), охватившая весь путь от пустого GSD-скелета до рабочего backend+UI на реальных моделях. Полная история решений — в ADR, здесь только сводка и связи.

## Что сделано (по порядку)

1. **Онбординг и зачистка generic-шаблона**. Из `CLAUDE.md`, `.claude/`, `.rules/`, `PROJECT_IDEA.md` вырезаны навязанные generic-зависимости: стандарт "Analytic Noir", иерархия `uipro`/`21st.dev`, ограничение локальной модели Qwen 32k-контекста — по прямому запросу Виктора.
2. **Phase 0 — Foundation** ([[ADR-004-phase0-scaffold]]): backend-only Python скелет. `core/{config_loader,intent_router,llm_router,context_engine}.py`, `storage/tasks_store.py`, `integrations/{obsidian,bitrix,fusionpos,telegram}.py` (заглушки), `vault/system/{routing,domains}.yaml`.
3. **Phase 1 — Core Workflows** ([[ADR-005-phase1-workflows]]): interface-agnostic `workflows/engine.py` (инъекция `human_input`), три воркфлоу (email/report/presentation), `storage/decisions_store.py`, `core/{quality_assurance,mentoring}.py`.
4. **Phase 2a — Learning & Scheduling**: `core/{learning_loop,estimation,reminders,scheduler}.py`, `integrations/google_calendar.py` (заглушка), `interfaces/telegram_bot.py` — реальный диспетчер `/new_task`/`/status` на очередях, без `python-telegram-bot` (переиспользует `HumanInput`-контракт напрямую).
5. **Anthropic → Ollama pivot** ([[ADR-007-ollama-primary]]): ключ Anthropic через omniroute-прокси (`http://localhost:20128`) не прошёл авторизацию (401 invalid x-api-key, причина не расследована). По решению Виктора — переключились на локальную Ollama. Добавлен `core/llm_dispatch.call_model` — провайдер-агностичная развязка по `api_provider` из `routing.yaml`.
6. **Три tier'а моделей Ollama** ([[ADR-008-ollama-model-tiers]]): `ollama-fast`=qwen2.5:7b-instruct (task_classification), `ollama-main`=qwen2.5:14b-instruct (presentation/email), `ollama-deep`=qwen2.5:32b-instruct (report/analysis/research) — подобраны под задачи и железо (RTX 5080 16GB + 64GB DDR5). Живой прогон выявил: `ollama-fast` иногда съезжает в китайский на свободной генерации (не на своей штатной задаче) — убран из fallback-цепочки presentation/email.
7. **Phase 2b — Web UI MVP** ([[ADR-006-phase2-scope-and-ui]]): Next.js 15 в `web/`, дизайн-токены через `anthropic-skills:ui-ux-pro-max` (синий `#2563EB`, Inter, light+dark — не Analytic Noir). `next.config.ts` проксирует `/backend/*` → FastAPI без CORS. Провалидировано вживую в браузере на реальных Ollama-моделях.
8. **Phase 3 UI-направление** ([[ADR-009-memory-graph-and-autonomy-ladder]]): референс Виктора [skilltree.altari.ai](https://skilltree.altari.ai) — уточнено, что их "tree map" на самом деле узловой граф, не оргчарт. Решение: 2D force-graph вместо Three.js, autonomy ladder вместо булева `autonomous`, second-brain поиск с источниками. Пока только доки, кода нет.
9. **Базовый системный промпт Jarvis** ([[ADR-010-jarvis-system-prompt]]): Виктор принёс файл, оказавшийся системным промптом самого Claude (Claude Fable 5) — отказался от инъекции (модель начала бы врать про идентичность, ссылаться на несуществующие тулы), написал новый с нуля (`core/system_prompt.py`), честный про идентичность, с открытым списком задач (поправка Виктора после ревью черновика).

## Итоговое состояние
- **134/134 pytest зелёные.**
- Репозиторий на GitHub: `git@github.com:Ackaron/Jarvis-os.git`, ветка `main`, push через deploy key.
- Backend (FastAPI) + Web UI (Next.js) запускаются вместе через `.claude/launch.json`.
- LLM primary — локальная Ollama (не Anthropic), три модельных tier'а.

## Открытые вопросы (актуальны на конец сессии)
- Причина 401 от omniroute не расследована — если опечатка в ключе, возврат на Claude тривиален (правка `routing.yaml`).
- `TELEGRAM_BOT_TOKEN`, `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — блокеры для реальных Telegram/Calendar (логика уже готова и протестирована на заглушках).
- Phase 3 (Autonomy) и "Desktop ↔ Telegram sync" — ждут решения Виктора о приоритете.

## Связи
[[PROJECT_IDEA]] · [[SPECIFICATION]] · [[ADR-004-phase0-scaffold]] · [[ADR-005-phase1-workflows]] · [[ADR-006-phase2-scope-and-ui]] · [[ADR-007-ollama-primary]] · [[ADR-008-ollama-model-tiers]] · [[ADR-009-memory-graph-and-autonomy-ladder]] · [[ADR-010-jarvis-system-prompt]]
