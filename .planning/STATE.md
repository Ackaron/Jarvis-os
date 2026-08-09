# 🚀 Current Project State

## 📍 Активная задача
- **Задача**: Базовый системный промпт Jarvis написан с нуля и подключён ко всем LLM-вызовам воркфлоу (не заимствован из принесённого файла — это был системный промпт самого Claude). Phase 2 полностью закрыт. UI-направление Phase 3 определено. Следующий шаг — `/plan` для Phase 3 (Autonomy) или Desktop↔Telegram sync поверх MVP UI.
- **Субагент**: свободен, ждёт направления от Виктора.
- **Связанный файл**: `[[ADR-010-jarvis-system-prompt]]`, `[[ADR-009-memory-graph-and-autonomy-ladder]]`.

---

## ✅ Последние шаги (Completed)
0. **Базовый системный промпт Jarvis** (2026-08-09): Виктор принёс файл с Рабочего стола для "инъекции в модели" — оказался системным промптом самого Claude (Claude Fable 5, похоже на утёкший/внутренний промпт Anthropic), включая тул-дефиниции под claude.ai-специфичную инфраструктуру. Отказался от буквальной инъекции (модель начала бы врать, что она Claude, и ссылаться на несуществующие инструменты), написал новый короткий промпт с нуля (`core/system_prompt.py`), взяв только переносимые поведенческие принципы. Виктор поймал реальную проблему в черновике — фраза про "воркфлоу (презентация/отчёт/письмо)" читалась как исчерпывающий список и заставила бы модель отказываться от непредвиденных задач — переписал на явно открытый список. Заодно поднял дублировавшийся 1-в-1 в трёх воркфлоу `_call_llm` в базовый класс `Workflow`. Проверено вживую на `ollama-main`: честно называет себя (не Claude), не отказывается от нестандартной задачи (план подкаста). 134/134 pytest. См. [[ADR-010-jarvis-system-prompt]].
1. **Phase 3 UI-направление зафиксировано** (2026-08-09): изучил референс Виктора [skilltree.altari.ai](https://skilltree.altari.ai) сам (не только по пересказу) — уточнил, что их "tree map" на самом деле узловой граф (не оргчарт-дерево), просто 2D/плоский вместо WebGL-3D. Взял два конкретных паттерна: карточка ноды с "лестницей автономности" (human-led/human-assisted/fully-autonomous вместо булева `autonomous`) и second-brain поиск с цитируемыми источниками. Обновлены `PROJECT_IDEA.md` (Key Feature, Phase 3 scope), `SPECIFICATION.md` (Screen 5/5b), `ROADMAP.md` (Phase 3). См. [[ADR-009-memory-graph-and-autonomy-ladder]]. Кода Phase 3 ещё не писал — это только doc/ADR обновление.
2. `PROJECT_IDEA.md`/`SPECIFICATION.md` написаны; generic-зависимости вырезаны.
3. **Phase 0-1**: backend-скелет + три воркфлоу. См. [[ADR-004-phase0-scaffold]], [[ADR-005-phase1-workflows]].
4. **Phase 2a**: learning_loop/estimation/reminders/scheduler/google_calendar-заглушка/telegram-диспетчер.
5. **Anthropic → Ollama pivot** + **три tier'а моделей подобраны и провалидированы вживую**: `ollama-fast`=qwen2.5:7b (task_classification), `ollama-main`=qwen2.5:14b (presentation/email), `ollama-deep`=qwen2.5:32b (report/analysis/research). Найден и исправлен реальный баг: `fast` иногда съезжает в китайский на свободной генерации — убран из fallback-цепочки presentation/email. См. [[ADR-007-ollama-primary]], [[ADR-008-ollama-model-tiers]].
6. **Phase 2b — Web UI MVP реализован и провалидирован в браузере** (2026-08-09): дизайн-токены через `anthropic-skills:ui-ux-pro-max` (синий `#2563EB`, Inter, light+dark — не Analytic Noir, без uipro/21st.dev), Next.js 15 (App Router, Tailwind v4, Turbopack) в `web/`, `next.config.ts` проксирует `/backend/*` → FastAPI (`interfaces/api.py`) без CORS. Прогнал вживую через Browser-инструмент: presentation → `intc`/`ollama-main`/автономно=Нет, email → автономно=Да — оба корректно, история накапливается, 0 ошибок консоли. `npm run build` и `npm run lint` — чисто. `.claude/launch.json` поднимает backend+web одной командой.
7. **134/134 pytest зелёные** (backend). Push на GitHub, `main` содержит всё по Phase 0-2b + системный промпт.

## 🚧 В работе прямо сейчас
- Ничего не в процессе. Backend и MVP UI полностью рабочие end-to-end на реальных моделях.

## 🧠 Контекст для модели (Memory)
- **Текущая сессия**: сохранена — [[2026-08-09_bootstrap-to-phase2-and-ollama-pivot]].
- **Отклонение от ADR-006**: `interfaces/telegram_bot.py` не использует `python-telegram-bot` — своя dispatch-логика на очередях (`TelegramDispatcher`/`TelegramHumanInput`), переиспользует `human_input`-контракт `workflows/engine.py` напрямую.
- **UI-решение реализовано**: `web/` — только Chat Interface, только классификация (`POST /api/classify`), БЕЗ многошагового чата поверх `workflows.engine` (нужны сессии/WebSocket — отдельный ADR, когда дойдём до high-fidelity прохода). Client Component на всей странице (весь UI интерактивный, серверных данных при загрузке нет).
- **Надёжность моделей**: `ollama-fast` (7B) годен только для constrained-задач (классификация, JSON). Не использовать как fallback для presentation/email.
- **Auth**: push на GitHub — deploy key (`~/.ssh/id_ed25519`, write access).
- **Dev launch**: `.claude/launch.json` в корне репо — конфиги `backend` (uvicorn --app-dir) и `web` (npm --prefix), оба через preview_start.

## 🔴 Блокировки и вопросы
- [x] ~~`ollama pull`~~, ~~Node.js~~ — оба закрыты и провалидированы.
- [x] ~~Web UI MVP~~ — реализован, собирается, проверен в браузере.
- [ ] **Не расследовано**: причина 401 от omniroute — если опечатка в ключе, можно вернуться на Claude в любой момент (правка `routing.yaml`).
- [ ] **Блокер**: `TELEGRAM_BOT_TOKEN` — для реального polling-лупа диспетчера.
- [ ] **Блокер**: `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` — для реального Calendar.
- [ ] **Открыто**: "Desktop ↔ Telegram sync" (следующий логичный шаг теперь, когда MVP UI существует) и Phase 3 (Autonomy) — ждут решения Виктора о приоритете.

---
*Последнее обновление: 2026-08-09*
