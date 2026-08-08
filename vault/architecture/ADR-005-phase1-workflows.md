---
type: adr
status: accepted
tags: [gsd, architecture, phase1, workflows]
created: 2026-08-08
updated: 2026-08-08
---

# ADR-005: Границы и порядок сборки Phase 1 Core Workflows

## 1. Контекст (The Problem)
Phase 1 должен дать presentation/report/email воркфлоу, Quality Assurance checks, Why Extraction и Mentoring Mode (`PROJECT_IDEA.md` → MVP Scope → Phase 1). Два架構ных риска мешают просто "сесть и написать":

1. **Интерактивность без интерфейса**: воркфлоу в `SPECIFICATION.md` спроектированы как чат-диалог (Viktor подтверждает/правит на каждом шаге), но Web UI и Telegram — это Phase 2. Если жёстко завязать воркфлоу на конкретный интерфейс, придётся всё переписывать через фазу.
2. **Реальные LLM-вызовы**: `core/llm_router.call_model` на Phase 0 — намеренная заглушка (`NotImplementedError`). Presentation/report/email воркфлоу без реальной генерации контента бессмысленны. Но `ANTHROPIC_API_KEY` у Виктора пока не подтверждён как настроенный.

## 2. Предложенное решение (The Decision)
1. **Interface-agnostic workflow engine**: воркфлоу — государственные машины (`workflows/engine.py`), которые получают точку интерактивности через инъекцию `human_input: Callable[[str, dict], Any]`. На Phase 1 дефолтная реализация — блокирующий CLI (`input()`) для ручных прогонов, тесты подставляют скриптованный fake. Phase 2 просто подключит тот же engine к Telegram/Web — без переписывания бизнес-логики.
2. **LLM-вызовы через DI, не через жёсткую зависимость от ключа**: `core/llm_client.py` — реальная обёртка над Anthropic SDK, вызывается воркфлоу через `llm_router.execute_with_fallback(decision, task, caller=llm_client.call_anthropic)`. Тесты воркфлоу инжектят fake `caller`, поэтому вся бизнес-логика (state machine, QA, why-extraction) тестируется без ключа. Ключ нужен только для реального прогона генерации — это ожидаемое ограничение, не архитектурный долг.
3. **Decisions storage**: новый `storage/decisions_store.py` (JSON, зеркалит таблицу `decisions` из `SPECIFICATION.md`) — питает Why Extraction.
4. **Stakeholder write-back**: `core/context_engine` получает `update_stakeholder_profile()` — вносит правки в frontmatter `vault/stakeholders/{name}.md` (создаёт файл, если его нет). Без этого Stakeholder Learning Loop не работает даже в зачаточном виде.
5. **Порядок сборки**: сначала общий engine (движок + decisions + stakeholder write-back), затем **email workflow первым** — он проще всего (letter → thesis → formal → review → save template) и валидирует engine end-to-end дешевле, чем presentation. Затем report, затем самый сложный — presentation (multi-step mockup/approve). QA checks и Mentoring Mode — сквозные, строятся после engine и decisions_store, подключаются к завершающему шагу каждого воркфлоу.

## 3. Порядок сборки (атомарные задачи, для Executor)
1. `storage/decisions_store.py` — JSON-хранилище decisions (decision_type, original_value, new_value, reasoning, task_id).
2. `core/context_engine.update_stakeholder_profile()` — запись/мердж frontmatter стейкхолдера.
3. `core/llm_client.py` — реальная Anthropic-обёртка (`call_anthropic`), явная ошибка при отсутствии `ANTHROPIC_API_KEY`, не заглушка.
4. `workflows/engine.py` — базовый Step/Workflow движок с инъекцией `human_input`, интеграцией с `storage/tasks_store` (статусы) и `storage/decisions_store` (логирование правок + "почему"). *(зависит от 1)*
5. `workflows/email_workflow.py` — первый конкретный воркфлоу поверх engine. *(зависит от 3, 4)*
6. `workflows/report_workflow.py` — data (из `context_engine.get_knowledge` как заглушка вместо живого FusionPOS) → analyze → deliver. *(зависит от 3, 4)*
7. `workflows/presentation_workflow.py` — collect → verify → mockup → fill → approve, использует stakeholder-профиль. *(зависит от 2, 3, 4)*
8. `core/quality_assurance.py` — чеклист из `stakeholder.metadata.usual_checks`. *(зависит от 2)*
9. `core/mentoring.py` — объяснение "почему" на основе `decisions_store` + stakeholder-профиля. *(зависит от 1, 2)*
10. Подключить QA (8) и Mentoring (9) к завершающему шагу каждого воркфлоу (5, 6, 7).
11. pytest-сьют на все новые модули (scripted `human_input` fakes, fake LLM caller) — прогнать, исправить баги.
12. Обновить `requirements.txt` (+`anthropic`), `README.md`, `ROADMAP.md`, `STATE.md`.

## 4. Последствия (Consequences)

### ✅ Плюсы
- Вся бизнес-логика Phase 1 тестируется уже сейчас, без Telegram/Web UI и без реального Anthropic-ключа.
- Переход на Phase 2 (реальный интерфейс) не требует переписывания воркфлоу — только новая реализация `human_input`.
- Decisions/stakeholder write-back дают реальную (не имитационную) базу для Learning Loop уже в Phase 1.

### ❌ Минусы / Риски
- CLI-заглушка `human_input` на Phase 1 неудобна для реальной работы Виктора — Phase 1 годится для разработки/тестов, не для ежедневного использования. Это ожидаемо и не блокирует Phase 2.
- Реальная генерация (не тесты) всё равно ждёт `ANTHROPIC_API_KEY` — открытый вопрос к Виктору.

## 5. Статус (Status)
- [x] **Accepted** (Planner, `/plan` от 2026-08-08)

## 6. Связи (Links)
- Роадмап: [[.planning/ROADMAP]]
- Технический стек: [[SPECIFICATION]]
- Предыдущая фаза: [[ADR-004-phase0-scaffold]]
