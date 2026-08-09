# 🚀 Current Project State

## 📍 Активная задача
- **Задача**: Ollama-модели скачаны и провалидированы вживую. LLM-слой Phase 0-2a полностью рабочий end-to-end. Следующий шаг — Phase 2b: Next.js MVP UI.
- **Субагент**: свободен, ждёт `/execute` для `web/`.
- **Связанный файл**: `[[ADR-008-ollama-model-tiers]]`, `[[ADR-006-phase2-scope-and-ui]]`.

---

## ✅ Последние шаги (Completed)
1. `PROJECT_IDEA.md`/`SPECIFICATION.md` написаны; generic-зависимости вырезаны.
2. **Phase 0-1**: backend-скелет + три воркфлоу. См. [[ADR-004-phase0-scaffold]], [[ADR-005-phase1-workflows]].
3. **Phase 2 спланирован**: UI-стратегия решена с Виктором напрямую. См. [[ADR-006-phase2-scope-and-ui]].
4. **Phase 2a реализован**: learning_loop/estimation/reminders/scheduler/google_calendar-заглушка/telegram-диспетчер/FastAPI-мост.
5. **Anthropic → Ollama pivot**: omniroute-ключ не прошёл авторизацию (`401 invalid x-api-key`, не расследовано). `core/llm_dispatch.call_model` — провайдер-агностичная развязка. См. [[ADR-007-ollama-primary]].
6. **Три tier'а моделей подобраны и провалидированы вживую** (2026-08-09): `ollama-fast`=qwen2.5:7b-instruct, `ollama-main`=qwen2.5:14b-instruct (presentation/email), `ollama-deep`=qwen2.5:32b-instruct (report/analysis/research). Реальный прогон на деловом письме: `main` (7.7с) и `deep` (35.8с) — стабильно корректный русский; `fast` один раз съехал в китайский на генерации письма (на классификации/JSON — 3/3 корректно). **Следствие**: `presentation`/`email` fallback изменён с `[ollama-fast]` на `false` — чистая ошибка лучше кривого письма от имени Виктора. См. [[ADR-008-ollama-model-tiers]] (аддендум).
7. `call_ollama` теперь передаёт `num_ctx` (был баг — Ollama резала контекст до 2048 дефолтом).
8. Node.js установлен (`v24.19.0`/npm `11.17.0`).
9. **129/129 pytest зелёные**. Push на GitHub, `main` содержит всё по Phase 0-2a + Ollama pivot + real model validation.

## 🚧 В работе прямо сейчас
- Ничего не в процессе. LLM-слой полностью рабочий на реальных моделях.
- Phase 2b (Next.js MVP) — следующий шаг, ничем не заблокирован. При дизайне — обязательно `anthropic-skills:ui-ux-pro-max` + `/ui` (прямое указание Виктора).

## 🧠 Контекст для модели (Memory)
- **Текущая сессия**: лог ещё не сохранён (`/save` не вызывался).
- **Отклонение от ADR-006**: `interfaces/telegram_bot.py` не использует `python-telegram-bot` — своя dispatch-логика на очередях.
- **UI-решение**: минимальный Next.js UI (только Chat Interface, только классификация, БЕЗ многошагового чата поверх `workflows.engine`). При реализации UI — `anthropic-skills:ui-ux-pro-max` + `/ui`.
- **Auth**: push на GitHub — deploy key (`~/.ssh/id_ed25519`, write access).
- **Надёжность моделей**: `ollama-fast` (7B) годен только для constrained-задач (классификация, JSON) — на свободной генерации показал разовый сбой (переключение на китайский). Не использовать как fallback для presentation/email.

## 🔴 Блокировки и вопросы
- [x] ~~`ollama pull`~~ — завершён, все 3 тега подтверждены (`ollama list`), реальный smoke-тест пройден.
- [x] ~~Node.js не установлен~~ — установлен.
- [ ] **Не расследовано**: причина 401 от omniroute — если опечатка в ключе, можно вернуться на Claude в любой момент (правка `routing.yaml`).
- [ ] **Блокер**: `TELEGRAM_BOT_TOKEN` — для реального polling-лупа.
- [ ] **Блокер**: `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — для реального Calendar.

---
*Последнее обновление: 2026-08-09*
