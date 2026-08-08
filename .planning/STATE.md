# 🚀 Current Project State

## 📍 Активная задача
- **Задача**: Phase 1 — **завершена и запушена**. Следующий шаг: `/plan` для Phase 2 (Learning & Scheduling: stakeholder profiling автоматизация, Calendar, Telegram bot реальный, UI-стратегия).
- **Субагент**: свободен, ждёт следующего `/plan` или `/execute`.
- **Связанный файл**: `[[ADR-005-phase1-workflows]]`, `.planning/ROADMAP.md`.

---

## ✅ Последние шаги (Completed)
1. Написаны `PROJECT_IDEA.md` и `SPECIFICATION.md` (дизайн-документ и технический чертёж Jarvis OS).
2. Создан GSD-скелет: `.claude/agents/`, `.claude/commands/`, `.rules/`; generic-зависимости (Analytic Noir, uipro/21st.dev, Qwen 32k) вырезаны по запросу Виктора.
3. **Phase 0 реализован**: `core/{config_loader,intent_router,llm_router,context_engine}.py`, `storage/tasks_store.py`, `integrations/{obsidian,bitrix,fusionpos,telegram}.py`, `vault/system/{routing,domains}.yaml`. См. [[ADR-004-phase0-scaffold]].
4. **Phase 1 реализован**: `storage/decisions_store.py`, `core/{llm_client,quality_assurance,mentoring}.py`, `context_engine.update_stakeholder_profile()`, `obsidian.write_note_with_frontmatter()`, `workflows/{engine,email_workflow,report_workflow,presentation_workflow}.py`. Interface-agnostic движок (инъекция `human_input`), LLM-вызовы через DI (`llm_client.call_anthropic` как дефолтный caller). См. [[ADR-005-phase1-workflows]].
5. **79/79 pytest — зелёные** (46 Phase 0 + 33 Phase 1). Один реальный баг найден и исправлен по ходу: `ObsidianVault.parse_frontmatter` терял trailing newline тела заметки при round-trip (splitlines() схлопывал финальный `\n`) — переписан на точный срез по строке-разделителю.
6. Репозиторий синхронизирован с GitHub (`git@github.com:Ackaron/Jarvis-os.git`, deploy key с write access), несколько коммитов на `main`.

## 🚧 В работе прямо сейчас
- Ничего не в процессе. Phase 1 закрыт по Definition of Done из ROADMAP: все три воркфлоу проходят end-to-end через pytest со scripted `human_input` и fake LLM caller, decisions и stakeholder-правки реально пишутся в vault, QA (`quality_assurance.format_qa_prompt`) подключена в `presentation_workflow.approve_structure`, Mentoring (`explain()`) доступен на всех воркфлоу через базовый класс `Workflow`.

## 🧠 Контекст для модели (Memory)
- **Текущая сессия**: лог ещё не сохранён (`/save` не вызывался).
- **Важное примечание**: UI-стратегия не определена — ADR-003 снят, решение отдельным ADR на Phase 2.
- **Auth**: push на GitHub идёт через deploy key (`~/.ssh/id_ed25519`, без passphrase) с write access.
- **Отклонение от ROADMAP task 10**: QA-чеклист подключён только к `presentation_workflow` (там есть реальное понятие stakeholder + структурное одобрение, как в примере из SPECIFICATION.md), а не ко всем трём воркфлоу — email/report не имеют аналогичного stakeholder-driven approval шага. Mentoring (`explain()`) подключён универсально через базовый класс `Workflow`, доступен всем.

## 🔴 Блокировки и вопросы
- [ ] **Question**: Подтвердить у Виктора реальные креды интеграций (Bitrix24, FusionPOS, Telegram Bot Token) — понадобятся к Phase 2.
- [ ] **Question**: `ANTHROPIC_API_KEY` — нужен для реального прогона email/report/presentation воркфлоу (сборку/тесты не блокирует — LLM-вызовы через DI).
- [x] ~~README.md нужен отдельным файлом?~~ — создан, входит в Phase 0.

---
*Последнее обновление: 2026-08-08*
