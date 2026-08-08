# 🚀 Current Project State

## 📍 Активная задача
- **Задача**: Phase 2a — **реализован и запушен** (`learning_loop`, `estimation`, `reminders`, `google_calendar` заглушка, `scheduler`, `telegram_bot` диспетчер, `interfaces/api.py`). Phase 2b (Next.js MVP) заблокирован до установки Node.js.
- **Субагент**: свободен для 2a; ждёт Виктора для 2b (Node.js) и `/execute` дальше.
- **Связанный файл**: `[[ADR-006-phase2-scope-and-ui]]`.

---

## ✅ Последние шаги (Completed)
1. `PROJECT_IDEA.md`/`SPECIFICATION.md` написаны; generic-зависимости (Analytic Noir, uipro/21st.dev, Qwen 32k) вырезаны.
2. **Phase 0**: backend-скелет. См. [[ADR-004-phase0-scaffold]].
3. **Phase 1**: три воркфлоу поверх interface-agnostic `workflows/engine.py`. См. [[ADR-005-phase1-workflows]].
4. **Phase 2 спланирован**: UI-стратегия решена **с Виктором напрямую** (не молча, как в истории с ADR-003) — минимальный Next.js UI сейчас, полноценный high-fidelity проход позже. См. [[ADR-006-phase2-scope-and-ui]].
5. **Phase 2a реализован**: `core/{learning_loop,estimation,reminders,scheduler}.py`, `integrations/google_calendar.py` (заглушка), `interfaces/telegram_bot.py` (реальный диспетчер `/new_task`/`/status` поверх `workflows.engine`), `interfaces/api.py` (FastAPI, `POST /api/classify`). **113/113 pytest зелёные** (79 Phase 0-1 + 34 Phase 2a).
6. Push на GitHub, `main` содержит все коммиты Phase 0-2a.

## 🚧 В работе прямо сейчас
- Ничего не в процессе по 2a. 2b (Next.js MVP) не начат — блокер: Node.js не установлен на машине.

## 🧠 Контекст для модели (Memory)
- **Текущая сессия**: лог ещё не сохранён (`/save` не вызывался).
- **Отклонение от ADR-006**: `interfaces/telegram_bot.py` НЕ использует `python-telegram-bot` (не стал тянуть библиотеку ради галочки в ADR). Вместо этого — чистая dispatch-логика (`TelegramDispatcher` + `TelegramHumanInput` на очереди), полностью переиспользующая `HumanInput`-контракт из `workflows/engine.py`. Реальная библиотека и polling-луп понадобятся только когда появится `TELEGRAM_BOT_TOKEN` — сама логика маршрутизации уже реальна и протестирована на потоках (`threading`), без фейкового обещания.
- **UI-решение**: минимальный Next.js UI (только Chat Interface экран, только классификация через `intent_router`/`llm_router`, БЕЗ многошагового чата поверх `workflows.engine` — то отдельный ADR с сессиями/WebSocket). Нейтральный Tailwind-визуал, без uipro/21st.dev. Backend-мост `interfaces/api.py` уже готов и протестирован.
- **Auth**: push на GitHub — deploy key (`~/.ssh/id_ed25519`, write access).

## 🔴 Блокировки и вопросы
- [ ] **Блокер**: **Node.js 20+ и npm не установлены** — нужны для Phase 2b (`web/`, задачи 9-10 в ROADMAP). Ставит Виктор: https://nodejs.org (LTS) или `winget install OpenJS.NodeJS.LTS`.
- [ ] **Блокер**: `TELEGRAM_BOT_TOKEN` (от @BotFather) — для реального polling-лупа (диспетчер уже реален и протестирован без токена).
- [ ] **Блокер**: `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — для реального Calendar (заглушка не блокирует `scheduler`).
- [x] ~~ANTHROPIC_API_KEY~~ — не блокирует сборку/тесты (DI).

---
*Последнее обновление: 2026-08-08*
