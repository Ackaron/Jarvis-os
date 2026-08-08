# 🚀 Current Project State

## 📍 Активная задача
- **Задача**: Модели Ollama подобраны и разложены на 3 tier'а в `routing.yaml` (Qwen2.5 7b/14b/32b) — Виктор запустил `ollama pull`, качается. Node.js установлен. Готовы двигаться к Phase 2b (Next.js MVP UI), как только модели докачаются (не блокирует старт UI-работы, только реальные LLM-ответы).
- **Субагент**: свободен, ждёт: (1) подтверждения, что `ollama pull` завершился и реальный smoke-тест прошёл, (2) `/execute` для `web/`.
- **Связанный файл**: `[[ADR-008-ollama-model-tiers]]`, `[[ADR-006-phase2-scope-and-ui]]`.

---

## ✅ Последние шаги (Completed)
1. `PROJECT_IDEA.md`/`SPECIFICATION.md` написаны; generic-зависимости вырезаны.
2. **Phase 0-1**: backend-скелет + три воркфлоу. См. [[ADR-004-phase0-scaffold]], [[ADR-005-phase1-workflows]].
3. **Phase 2 спланирован**: UI-стратегия решена с Виктором напрямую. См. [[ADR-006-phase2-scope-and-ui]].
4. **Phase 2a реализован**: learning_loop/estimation/reminders/scheduler/google_calendar-заглушка/telegram-диспетчер/FastAPI-мост.
5. **Anthropic → Ollama pivot**: omniroute-ключ не прошёл авторизацию (`401 invalid x-api-key`, не расследовано). Добавлен `core/llm_dispatch.call_model` (провайдер-агностичная развязка по `api_provider`), `core/ollama_client.py` (реальный клиент к Ollama REST API). См. [[ADR-007-ollama-primary]].
6. **Три tier'а моделей** подобраны под задачи и железо (RTX 5080 16GB + 64GB DDR5): `ollama-fast`=qwen2.5:7b-instruct (task_classification), `ollama-main`=qwen2.5:14b-instruct (presentation/email, default), `ollama-deep`=qwen2.5:32b-instruct (report/analysis/research). Fallback-цепочки внутри Ollama (deep→main→fast) вместо бесполезного `fallback: false`. Заодно поймал и починил баг: `call_ollama` не передавал `num_ctx`, Ollama резала контекст до 2048 токенов дефолтом. См. [[ADR-008-ollama-model-tiers]].
7. Node.js установлен (`v24.19.0`/npm `11.17.0`).
8. **129/129 pytest зелёные** (проверено через DI/fake HTTP-клиент — реальных моделей ещё нет на диске). Push на GitHub.

## 🚧 В работе прямо сейчас
- `ollama pull qwen2.5:7b-instruct / 14b-instruct / 32b-instruct` запущен Виктором, не завершён (~34GB суммарно).
- Как докачается — нужен один реальный smoke-тест (аналогично тому, что делали для omniroute) на каждый tier, прежде чем считать Phase 2 полностью рабочим end-to-end.
- Phase 2b (Next.js MVP) технически разблокирован (Node.js есть) — ждёт команды на старт. При дизайне — обязательно `anthropic-skills:ui-ux-pro-max` + `/ui` (прямое указание Виктора).

## 🧠 Контекст для модели (Memory)
- **Текущая сессия**: лог ещё не сохранён (`/save` не вызывался).
- **Отклонение от ADR-006**: `interfaces/telegram_bot.py` не использует `python-telegram-bot` — своя dispatch-логика на очередях.
- **UI-решение**: минимальный Next.js UI (только Chat Interface, только классификация, БЕЗ многошагового чата поверх `workflows.engine`). При реализации UI — `anthropic-skills:ui-ux-pro-max` + `/ui`.
- **Auth**: push на GitHub — deploy key (`~/.ssh/id_ed25519`, write access).
- **Модельные теги** (`qwen2.5:*-instruct` в routing.yaml) выбраны по знаниям на январь 2026 — стоит свериться с `ollama.com/library`, вдруг Qwen3 к этому моменту стал более зрелым вариантом на тех же размерах.

## 🔴 Блокировки и вопросы
- [ ] **В процессе**: `ollama pull` для 3 моделей — после завершения нужен реальный smoke-тест каждого tier'а.
- [ ] **Не расследовано**: причина 401 от omniroute — если опечатка в ключе, можно вернуться на Claude в любой момент (правка `routing.yaml`).
- [x] ~~Node.js не установлен~~ — установлен.
- [ ] **Блокер**: `TELEGRAM_BOT_TOKEN` — для реального polling-лупа.
- [ ] **Блокер**: `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — для реального Calendar.

---
*Последнее обновление: 2026-08-08*
