# 🚀 Current Project State

## 📍 Активная задача
- **Задача**: LLM-провайдер переключён на Ollama (primary), Node.js установлен — готовы двигаться к Phase 2b (Next.js MVP UI).
- **Субагент**: свободен, ждёт: (1) реальный тег Ollama-модели от Виктора, (2) `/execute` для `web/`.
- **Связанный файл**: `[[ADR-007-ollama-primary]]`, `[[ADR-006-phase2-scope-and-ui]]`.

---

## ✅ Последние шаги (Completed)
1. `PROJECT_IDEA.md`/`SPECIFICATION.md` написаны; generic-зависимости вырезаны (Analytic Noir, uipro/21st.dev, Qwen 32k).
2. **Phase 0-1**: backend-скелет + три воркфлоу. См. [[ADR-004-phase0-scaffold]], [[ADR-005-phase1-workflows]].
3. **Phase 2 спланирован**: UI-стратегия решена с Виктором напрямую. См. [[ADR-006-phase2-scope-and-ui]].
4. **Phase 2a реализован**: learning_loop/estimation/reminders/scheduler/google_calendar-заглушка/telegram-диспетчер/FastAPI-мост.
5. **Anthropic → Ollama pivot**: ключ через omniroute (`http://localhost:20128`) не прошёл авторизацию (`401 invalid x-api-key`, причина не расследована). По решению Виктора переключились на Ollama. Добавлен `core/llm_dispatch.call_model` — провайдер-агностичная развязка по `api_provider` из `routing.yaml`; все воркфлоу/диспетчер/learning_loop переключены на него. `core/ollama_client.py` — реальный клиент к локальному Ollama REST API. `routing.yaml`: `ollama-local` primary везде, `claude-*` модели оставлены в конфиге (не удалены) для лёгкого возврата. См. [[ADR-007-ollama-primary]].
6. **Node.js установлен** (`v24.19.0`/npm `11.17.0`) — просто был PATH-кэш в моей сессии, `winget` подтвердил "already installed".
7. **127/127 pytest зелёные**. Push на GitHub, `main` содержит все коммиты Phase 0-2a + Ollama pivot.

## 🚧 В работе прямо сейчас
- Ollama-сервер уже поднят локально (`GET /api/tags` отвечает), но моделей ещё не подтянуто (`{"models":[]}`). `routing.yaml` → `models.ollama-local.api_model_id: llama3.1` — **placeholder**, нужно поправить на реальный тег после `ollama pull <model>`.
- Phase 2b (Next.js MVP) не начат — теперь разблокирован (Node.js есть), ждёт команды на старт. Instrukция от Виктора: при дизайне интерфейса обязательно использовать skill `anthropic-skills:ui-ux-pro-max` и команду `/ui`.

## 🧠 Контекст для модели (Memory)
- **Текущая сессия**: лог ещё не сохранён (`/save` не вызывался).
- **Отклонение от ADR-006**: `interfaces/telegram_bot.py` не использует `python-telegram-bot` — своя dispatch-логика на очередях, переиспользующая `HumanInput`-контракт. Реальный токен нужен только для polling-лупа.
- **UI-решение**: минимальный Next.js UI (только Chat Interface, только классификация, БЕЗ многошагового чата поверх `workflows.engine` — для этого отдельный ADR с сессиями/WebSocket). При реализации UI — использовать `anthropic-skills:ui-ux-pro-max` + `/ui` (прямое указание Виктора, не uipro/21st.dev из отменённого ADR-003 — это другой, актуальный skill).
- **Auth**: push на GitHub — deploy key (`~/.ssh/id_ed25519`, write access).

## 🔴 Блокировки и вопросы
- [ ] **Вопрос**: какую модель Виктор планирует использовать в Ollama (`ollama pull <model>`)? Нужно поправить `api_model_id` в `routing.yaml`.
- [ ] **Не расследовано**: причина 401 от omniroute — если опечатка в ключе, можно вернуться на Claude в любой момент (routing.yaml правка).
- [x] ~~Node.js не установлен~~ — установлен, `v24.19.0`.
- [ ] **Блокер**: `TELEGRAM_BOT_TOKEN` — для реального polling-лупа (диспетчер уже реален и протестирован без токена).
- [ ] **Блокер**: `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — для реального Calendar.

---
*Последнее обновление: 2026-08-08*
