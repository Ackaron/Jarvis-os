# 🗺️ Project Roadmap: [[PROJECT_IDEA]]

## 🎯 Текущая цель
> Phase 0 — Foundation: заложить структуру репозитория, конфиги и заглушки core-компонентов, на которых будут строиться все воркфлоу (презентации, отчёты, письма) из `PROJECT_IDEA.md`.

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

### 🟣 Phase 2: Learning & Scheduling (Week 3-4)
- [ ] Stakeholder profiling (автопостроение из правок).
- [ ] Улучшение оценки времени (estimation accuracy).
- [ ] Календарная интеграция (Google Calendar).
- [ ] Система напоминаний.
- [ ] Telegram bot интеграция (полный флоу, не заглушка).
- [ ] Desktop ↔ Telegram синхронизация.
- [ ] UI-стратегия для Web UI определяется отдельно через `/plan` (ADR-003 снят, см. `vault/architecture/`).

### 🔴 Phase 3: Autonomy (Week 4+)
- [ ] Автовыполнение в свободных слотах календаря.
- [ ] Параллельное выполнение задач.
- [ ] Dashboard (burndown, quality metrics, LLM performance).
- [ ] 3D Graph визуализация памяти (Three.js/Babylon.js).

---

## 🚩 Критерии готовности (Definition of Done)
- Код соответствует `.rules/` (UI, TS, Database, Testing).
- Изменения отражены в `[[vault/index.md]]` и соответствующих ADR.
- Пройден `/review` от субагента `verifier`.
- Ни один core-компонент не завязан на внешний skill/CLI, не согласованный явно с Виктором.
