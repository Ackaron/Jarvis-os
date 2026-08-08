---
type: adr
status: accepted
tags: [gsd, architecture, phase2, ui, telegram, calendar]
created: 2026-08-08
updated: 2026-08-08
---

# ADR-006: Границы Phase 2, реальный Telegram-бот и решение по Web UI MVP

## 1. Контекст (The Problem)
Phase 2 по `PROJECT_IDEA.md` включает: автопостроение stakeholder-профилей, улучшение оценки времени, Google Calendar, напоминания, реальный Telegram-бот, "Desktop ↔ Telegram синхронизацию". При декомпозиции всплыли три риска:

1. **Google Calendar** требует OAuth-приложение в Google Cloud (client ID/secret, consent screen) — это может настроить только Виктор.
2. **Реальный Telegram-бот** требует токена от @BotFather — тоже только от Виктора.
3. **"Desktop ↔ Telegram sync"** предполагает существующий Desktop/Web UI. Его никогда не строили: `ADR-004` сознательно отложил UI на Phase 0, а `ADR-003` (Analytic Noir + uipro/21st.dev) Виктор сам отменил как навязанный без его выбора. Повторять эту ошибку — молча выбрать новый дизайн — нельзя.

По пункту 3 решение было явно запрошено у Виктора (не молчаливый выбор): **строим минимальный жизнеспособный Web UI сейчас (Next.js, как и было в SPECIFICATION.md), с приемлемым базовым визуалом, полноценный high-fidelity UI/UX — отдельным проходом позже** (когда до него дойдёт очередь по `CLAUDE.md` lifecycle: `/ui` + `.rules/ui-ux.md`).

## 2. Предложенное решение (The Decision)

### 2a. Строится сейчас (DI/заглушки, без внешних кредов — как Bitrix/FusionPOS/Anthropic на Phase 0-1)
- `core/learning_loop.py` — выводит обновления профиля стейкхолдера (focus_areas/anti_focus) из истории `decisions_store` через LLM-вызов (тот же DI-паттерн, что и в воркфлоу).
- `core/estimation.py` — оценка времени из истории `tasks_store` (avg/variance по task_type, confidence).
- `core/reminders.py` — чистая логика "какому task нужно напоминание" (24ч/4ч/1ч до дедлайна); канал доставки инжектируется (по умолчанию — всё ещё заглушка `integrations.telegram.TelegramClient`).
- `integrations/google_calendar.py` — структурная заглушка (как Bitrix/FusionPOS): dataclasses + `is_configured()` + `NotImplementedError`. Реальный OAuth — когда у Виктора будет Google Cloud проект.
- `core/scheduler.py` — поиск свободных слотов по списку календарных событий (работает с любым источником через DI, тестируется на фейковых событиях, реальный Calendar не нужен).
- `interfaces/telegram_bot.py` — реальная **логика хендлеров** (`/new_task`, `/status`, `/approve`, `/reject`) на `python-telegram-bot`, подключается к `workflows.engine` через Telegram-based `human_input`. Тестируется на фейковых Update/Context объектах; только реальный polling-луп требует `TELEGRAM_BOT_TOKEN`.

### 2b. Web UI MVP (по прямому решению Виктора)
Минимальное веб-приложение на Next.js 15, реализующее **только** Chat Interface экран из wireframes `SPECIFICATION.md`:
- Простой чат-лог + инпут для описания задачи.
- Тонкий backend-мост `interfaces/api.py` (FastAPI) с одним эндпоинтом `POST /api/classify`, который прогоняет ввод через уже готовые `core.intent_router` + `core.llm_router` (без реального LLM-вызова, если `ANTHROPIC_API_KEY` не настроен — просто возвращает routing decision) и возвращает результат классификации.
- Визуал: нейтральная светлая/тёмная Tailwind-палитра по умолчанию, Inter, без брендированной "системы" вроде Analytic Noir и без обязательных внешних UI-skill'ов (uipro/21st.dev остаются вне проекта, см. ADR-003).
- **Явно не входит в MVP**: полноценный многошаговый чат поверх `workflows.engine` (это требует сессионного стейта + WebSocket, отдельный ADR при переходе к high-fidelity UI/UX), "Desktop ↔ Telegram sync" (следующая задача сразу после того, как MVP UI станет стабильным).

### 2c. Блокировано (нужны действия Виктора)
- `TELEGRAM_BOT_TOKEN` — для реального запуска бота.
- `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — для реального Calendar.
- **Node.js 20+ / npm** — не установлены на машине; без них нельзя собрать/запустить даже MVP UI. Ставит сам Виктор (как с Python), это новый системный рантайм.

## 3. Порядок сборки
1. `core/learning_loop.py`, `core/estimation.py`, `core/reminders.py` — независимы друг от друга, можно параллельно.
2. `integrations/google_calendar.py` → `core/scheduler.py` (зависит от 1).
3. `interfaces/telegram_bot.py` — зависит от `workflows/engine.py` (Phase 1).
4. pytest на всё вышеперечисленное.
5. `interfaces/api.py` (FastAPI) — зависит от `core/intent_router`, `core/llm_router` (Phase 0).
6. Next.js MVP (`web/`) — зависит от 5 и от установки Node.js Виктором. **Блокируется до подтверждения, что Node.js установлен.**

## 4. Последствия (Consequences)

### ✅ Плюсы
- Вся Phase 2a тестируется уже сейчас, без токенов/OAuth.
- UI-решение принято Виктором явно, а не навязано повторно.
- MVP UI даёт первый сквозной проход (Next.js → FastAPI → core), не обещая больше, чем реально сделано.

### ❌ Минусы / Риски
- Telegram-бот и Calendar останутся нерабочими до получения кредов — ожидаемо, не блокирует остальную разработку.
- MVP UI не поддерживает полноценный многошаговый воркфлоу-чат — только классификацию. Это осознанное ограничение, а не недоделка: полноценная интеграция требует отдельного архитектурного решения (сессии/WebSocket).

## 5. Статус (Status)
- [x] **Accepted** (Planner, `/plan` от 2026-08-08, UI-решение подтверждено Виктором напрямую)

## 6. Связи (Links)
- Роадмап: [[.planning/ROADMAP]]
- Предыдущие фазы: [[ADR-004-phase0-scaffold]], [[ADR-005-phase1-workflows]]
- Отменённое решение по UI: [[ADR-003-ui-strategy]]
