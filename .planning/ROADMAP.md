# 🗺️ Project Roadmap: [[PROJECT_IDEA]]

## 🎯 Текущая цель
> Phase 2 — Learning & Scheduling + Web UI MVP: автопостроение stakeholder-профилей, оценка времени, напоминания, реальный Telegram-бот (логика, без запуска — нужен токен), заглушка Google Calendar, и минимальный Next.js UI с приемлемым визуалом (полноценный UI/UX — отдельным проходом позже). См. [[ADR-006-phase2-scope-and-ui]].

---

## 🏗 Фазы разработки (Milestones)

### 🟢 Phase 0: Foundation & Core Infrastructure (Week 1)
Источник: `PROJECT_IDEA.md` → MVP Scope → Phase 0, `SPECIFICATION.md` → Архитектурный стек. Архитектурные решения и порядок сборки зафиксированы в [[ADR-004-phase0-scaffold]] — backend-only (без Next.js), single source конфигов в `vault/system/`, Obsidian через прямой файловый доступ, интеграции — структурные заглушки без реальных API-вызовов.

Атомарные задачи (строго в этом порядке, см. ADR-004 §3 для зависимостей):
1. [ ] Folder structure: `core/`, `interfaces/`, `workflows/`, `storage/`, `integrations/`, `vault/system/`.
2. [ ] `vault/system/routing.yaml` (LLM Routing Configuration, по образцу из `SPECIFICATION.md`).
3. [ ] `vault/system/domains.yaml` (ИНТЦ, Bootlegger, Дом, Образование, по образцу из `JARVIS_OS_ARCHITECTURE.md`).
4. [ ] `core/config_loader` — чтение YAML из `vault/system/`. *(зависит от 1-3)*
5. [ ] `core/intent_router` — task_type/domain/urgency/stakeholder. *(зависит от 4)*
6. [ ] `core/llm_router` — маршрутизация + fallback-цепочка. *(зависит от 4)*
7. [ ] `core/context_engine` — файловый доступ к `vault/` (stakeholders, templates, knowledge_base). *(зависит от 1)*
8. [ ] `storage/tasks_store` — минимальная локальная схема задач (SQLite/JSON, без Supabase). *(зависит от 1)*
9. [ ] `integrations/obsidian` — обёртка над файловым доступом для `context_engine`. *(зависит от 7)*
10. [ ] `integrations/bitrix`, `integrations/fusionpos`, `integrations/telegram` — структурные заглушки (можно параллельно). *(зависят от 1)*
11. [ ] Smoke-тесты pytest на 5-10 (импорт + базовый вызов, без реального LLM/API).
12. [ ] `README.md` в корне — короткий Design Doc с навигацией по `PROJECT_IDEA.md`/`SPECIFICATION.md`/структуре папок.

**Definition of Done Phase 0**: репозиторий содержит рабочую структуру папок, `routing.yaml`/`domains.yaml` валидны, core-компоненты импортируются и проходят smoke-тест (без реального LLM-вызова), заглушки интеграций задокументированы, `README.md` создан.

### 🔵 Phase 1: Core Workflows (Week 2-3)
Источник: `PROJECT_IDEA.md` → MVP Scope → Phase 1. Архитектурные решения и порядок сборки — в [[ADR-005-phase1-workflows]]: interface-agnostic engine (инъекция `human_input`, Phase 2 подключит реальный UI), LLM-вызовы через DI (бизнес-логика тестируется без ключа), email-воркфлоу первым как самый дешёвый способ провалидировать engine.

Атомарные задачи (строго в этом порядке, см. ADR-005 §3 для зависимостей):
1. [ ] `storage/decisions_store.py` — JSON-хранилище decisions (Why Extraction).
2. [ ] `core/context_engine.update_stakeholder_profile()` — запись/мердж frontmatter стейкхолдера.
3. [ ] `core/llm_client.py` — реальная Anthropic-обёртка (`call_anthropic`), явная ошибка без `ANTHROPIC_API_KEY`.
4. [ ] `workflows/engine.py` — Step/Workflow движок, инъекция `human_input`, интеграция с `tasks_store`/`decisions_store`. *(зависит от 1)*
5. [ ] `workflows/email_workflow.py` — letter → thesis → formal → review → save template. *(зависит от 3, 4)*
6. [ ] `workflows/report_workflow.py` — data (заглушка через `context_engine.get_knowledge`) → analyze → deliver. *(зависит от 3, 4)*
7. [ ] `workflows/presentation_workflow.py` — collect → verify → mockup → fill → approve. *(зависит от 2, 3, 4)*
8. [ ] `core/quality_assurance.py` — чеклист из `stakeholder.metadata.usual_checks`. *(зависит от 2)*
9. [ ] `core/mentoring.py` — объяснение "почему" из `decisions_store` + профиля. *(зависит от 1, 2)*
10. [ ] Подключить QA (8) и Mentoring (9) к завершающему шагу воркфлоу (5, 6, 7).
11. [ ] pytest-сьют на все новые модули (scripted `human_input`, fake LLM caller) — прогнать, исправить баги.
12. [ ] Обновить `requirements.txt` (+`anthropic`), `README.md`.

**Definition of Done Phase 1**: все три воркфлоу проходят end-to-end через pytest со scripted `human_input` и fake LLM caller (без реального ключа), decisions и stakeholder-правки реально пишутся в vault, QA/Mentoring подключены и покрыты тестами.

### 🟣 Phase 2: Learning & Scheduling + Web UI MVP (Week 3-4)
Источник: `PROJECT_IDEA.md` → MVP Scope → Phase 2. Границы и UI-решение (подтверждено Виктором напрямую, не навязано) — в [[ADR-006-phase2-scope-and-ui]]. **LLM primary — Ollama, не Anthropic** (omniroute-ключ не прошёл авторизацию), провайдер-агностичная развязка через `core/llm_dispatch.call_model` — см. [[ADR-007-ollama-primary]]. При дизайне UI (2b) — использовать skill `anthropic-skills:ui-ux-pro-max` и команду `/ui` (прямое указание Виктора).

**2a — реализовано:**
1. [x] `core/learning_loop.py` — profile updates из `decisions_store` через LLM (DI).
2. [x] `core/estimation.py` — оценка времени из истории `tasks_store` (avg/variance/confidence по task_type).
3. [x] `core/reminders.py` — логика "кому нужно напоминание" (24ч/4ч/1ч до дедлайна), канал доставки через DI.
4. [x] `integrations/google_calendar.py` — структурная заглушка (как Bitrix/FusionPOS).
5. [x] `core/scheduler.py` — поиск свободных слотов по календарным событиям (DI, без реального Calendar).
6. [x] `interfaces/telegram_bot.py` — реальный диспетчер `/new_task`/`/status` через очередь (`TelegramDispatcher`/`TelegramHumanInput`), без `python-telegram-bot` — переиспользует `human_input`-контракт `workflows/engine.py` напрямую (см. STATE.md, отклонение от исходного плана).
7. [x] pytest на 1-6 — зелёные.

**2b — Web UI MVP: реализовано и провалидировано в браузере.**
8. [x] `interfaces/api.py` (FastAPI) — `POST /api/classify`, прогоняет ввод через `intent_router`+`llm_router`.
9. [x] `web/` — минимальный Next.js 15 чат-экран (только классификация, БЕЗ многошагового воркфлоу-чата), дизайн-токены через `anthropic-skills:ui-ux-pro-max` (синий `#2563EB`, Inter, light+dark), `next.config.ts` rewrites `/backend/*` → FastAPI (без CORS).
10. [x] `npm run build` + `npm run lint` — чисто. Ручной прогон в браузере через `.claude/launch.json` (backend+web) — оба сценария (presentation/email) отработали end-to-end на реальных Ollama-моделях, 0 ошибок консоли.

**2c — заблокировано, требует действий Виктора:**
- `TELEGRAM_BOT_TOKEN` (от @BotFather) — для реального запуска polling-лупа диспетчера из 6.
- `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — для реального Calendar вместо заглушки из 4.

**Явно не входит в Phase 2** (см. ADR-006 §2b): "Desktop ↔ Telegram sync" — следующая задача сразу после стабилизации Web UI MVP; полноценный high-fidelity UI/UX — отдельный проход через `/ui` + `.rules/ui-ux.md` позже.

### 🔴 Phase 3: Autonomy (Week 4+)
UI-направление для этой фазы — референс [skilltree.altari.ai](https://skilltree.altari.ai), решение зафиксировано в [[ADR-009-memory-graph-and-autonomy-ladder]].

- [ ] Автовыполнение в свободных слотах календаря.
- [ ] Параллельное выполнение задач.
- [ ] Dashboard (burndown, quality metrics, LLM performance) — KPI-строка + график + список сигналов.
- [ ] Memory Graph — 2D force-directed (не 3D/Three.js), клик по ноде → детальная панель с autonomy ladder (human-led/human-assisted/fully-autonomous) вместо булева `autonomous`.
- [ ] Second Brain поиск: вопрос → ответ с цитируемыми источниками из vault (расширение `context_engine`).

---

## 🚩 Критерии готовности (Definition of Done)
- Код соответствует `.rules/` (UI, TS, Database, Testing).
- Изменения отражены в `[[vault/index.md]]` и соответствующих ADR.
- Пройден `/review` от субагента `verifier`.
- Ни один core-компонент не завязан на внешний skill/CLI, не согласованный явно с Виктором.
