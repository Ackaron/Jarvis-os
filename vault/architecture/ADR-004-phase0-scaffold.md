---
type: adr
status: accepted
tags: [gsd, architecture, phase0, backend]
created: 2026-08-08
updated: 2026-08-08
---

# ADR-004: Границы и порядок сборки Phase 0 Foundation

## 1. Контекст (The Problem)
Phase 0 из `ROADMAP.md` требует создать структуру `core/interfaces/workflows/storage/integrations`, конфиги `routing.yaml`/`domains.yaml`, core-компоненты (`intent_router`, `llm_router`, `context_engine`) и заглушки интеграций (Obsidian, Bitrix, FusionPOS, Telegram). Без явных архитектурных решений возникают три риска:
- Где физически живут `routing.yaml`/`domains.yaml` — в `vault/system/` (Obsidian as source of truth) или в отдельном `config/` каталоге бэкенда — раздвоение конфигурации.
- Нужен ли уже сейчас Next.js/frontend слой, или Phase 0 — чисто backend-скелет.
- Насколько "живыми" должны быть заглушки интеграций (Bitrix/FusionPOS/Telegram) — реальные HTTP-клиенты без ключей, или чистые структуры данных/интерфейсы.

## 2. Предложенное решение (The Decision)
1. **Single config source**: `routing.yaml` и `domains.yaml` живут только в `vault/system/` (см. `JARVIS_OS_ARCHITECTURE.md` → Storage Structure). `core/llm_router` и `core/intent_router` читают их напрямую оттуда через общий config-loader — никакого дублирующего `config/` каталога.
2. **Backend-only Phase 0**: Phase 0 не включает Next.js/Web UI. Все core-компоненты — чистый Python, тестируемые через pytest без поднятия сервера. UI-стратегия (тема, компоненты) откладывается на Phase 2 и будет решена отдельным ADR (ADR-003 уже снят как навязанный generic-шаблоном).
3. **Obsidian — прямой файловый доступ**: На Phase 0 `context_engine` читает/пишет `vault/` напрямую через файловую систему. Интеграция через Obsidian REST API Plugin откладывается — не нужна для локальной разработки одним пользователем (Виктор).
4. **Интеграции — структурные заглушки**: `integrations/bitrix`, `integrations/fusionpos`, `integrations/telegram` содержат интерфейсы/dataclass-модели запросов-ответов и клиентский класс с методами, поднимающими `NotImplementedError` или возвращающими фикстуры — без реальных HTTP-вызовов и без реальных ключей в `.env`. Реальные креды и вызовы — вопрос к Виктору, отмечен как блокер в `STATE.md`.

## 3. Порядок сборки (атомарные задачи, для Executor)
1. Создать структуру папок `core/`, `interfaces/`, `workflows/`, `storage/`, `integrations/`, `vault/system/`.
2. `vault/system/routing.yaml` — по образцу из `SPECIFICATION.md` → LLM Routing Configuration.
3. `vault/system/domains.yaml` — 4 домена (ИНТЦ, Bootlegger, Дом, Образование) по образцу из `JARVIS_OS_ARCHITECTURE.md` → Domain Structure.
4. `core/config_loader` — общая функция чтения YAML из `vault/system/`. (Зависит от 1-3.)
5. `core/intent_router` — классификация task_type/domain/urgency, читает `domains.yaml` через `config_loader`. (Зависит от 4.)
6. `core/llm_router` — маршрутизация + fallback-цепочка, читает `routing.yaml` через `config_loader`. (Зависит от 4.)
7. `core/context_engine` — файловый доступ к `vault/` (stakeholders, templates, knowledge_base). (Зависит от 1.)
8. `storage/tasks_store` — минимальная локальная схема задач (SQLite или JSON, без Supabase). (Зависит от 1.)
9. `integrations/obsidian` — тонкая обёртка над файловым доступом, используемая `context_engine`. (Зависит от 7.)
10. `integrations/bitrix`, `integrations/fusionpos`, `integrations/telegram` — структурные заглушки (параллельно, зависят только от 1).
11. Smoke-тесты pytest на 5-10 (импорт + базовый вызов без реального LLM/API).
12. `README.md` в корне — короткий Design Doc с навигацией по `PROJECT_IDEA.md`/`SPECIFICATION.md`/структуре папок.

## 4. Последствия (Consequences)

### ✅ Плюсы
- Один источник правды для конфигов — нет риска рассинхронизации `routing.yaml`.
- Backend-скелет тестируется без внешних сервисов и без UI-зависимостей.
- Заглушки интеграций явно помечены как нерабочие — Executor не будет тратить время на реальные API до получения кредов.

### ❌ Минусы / Риски
- Потребуется рефакторинг config-loader'а, если позже понадобится Obsidian REST API (hot-reload из работающего приложения Obsidian).
- Backend-only старт означает, что Phase 0 не даёт визуального результата для демонстрации Виктору — только programmatic smoke-тесты.

## 5. Статус (Status)
- [x] **Accepted** (Planner, в рамках `/plan` от 2026-08-08)

## 6. Связи (Links)
- Роадмап: [[.planning/ROADMAP]]
- Технический стек: [[SPECIFICATION]]
- Структура хранилища: [[JARVIS_OS_ARCHITECTURE]]
- Снятое решение по UI: [[ADR-003-ui-strategy]]
