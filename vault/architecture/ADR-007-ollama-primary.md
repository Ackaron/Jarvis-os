---
type: adr
status: accepted
tags: [gsd, architecture, llm, ollama, anthropic]
created: 2026-08-08
updated: 2026-08-08
---

# ADR-007: Ollama — временный primary вместо Anthropic/Claude

## 1. Контекст (The Problem)
Виктор получил ключ Anthropic через локальный прокси **omniroute** (`http://localhost:20128`). `core/llm_client.py` был расширен поддержкой кастомного `ANTHROPIC_BASE_URL`, коннект до прокси подтверждён (HTTP 307 на root), но сам ключ omniroute отклонил: `401 authentication_error: invalid x-api-key`. Причина не выяснена (опечатка, протухший ключ, другой формат авторизации у omniroute) — решили не расследовать сейчас, а переключиться на локальную Ollama, которую Виктор разворачивает параллельно.

## 2. Предложенное решение (The Decision)
1. **Провайдер-агностичный вызов**: новый `core/llm_dispatch.call_model(model_name, task, config)` смотрит `api_provider` модели в `routing.yaml` и делегирует в `core.llm_client.call_anthropic` (provider: anthropic) или `core.ollama_client.call_ollama` (provider: local). Все воркфлоу (`email_workflow`, `report_workflow`, `presentation_workflow`), `interfaces/telegram_bot.py` и `core/learning_loop.py` переключены на `call_model` как дефолтный `llm_caller` вместо жёстко зашитого `call_anthropic`.
2. **`core/ollama_client.py`** — реальный клиент к локальному Ollama REST API (`POST /api/chat` на `OLLAMA_BASE_URL`, по умолчанию `http://localhost:11434`). HTTP-клиент инжектируется — тестируется без запущенной Ollama.
3. **`routing.yaml`**: `ollama-local` теперь primary во всех `routing_rules` (presentation/report/email/task_classification/analysis/research), `fallback: false` (фолбэк на Claude сейчас всё равно не сработает). `hybrid_mode` выключен (observer-паттерн предполагал рабочий cloud-primary для сравнения — сейчас его нет). Модели `claude-opus`/`claude-sonnet` **не удалены** из `models:` — обратное переключение на Anthropic, когда ключ заработает, это правка `routing_rules`, а не код.
4. **`api_model_id` для `ollama-local`** временно `llama3.1` — placeholder. Виктор ещё не выполнил `ollama pull <model>` (сервер поднят, `GET /api/tags` вернул пустой список моделей). Нужно поправить `vault/system/routing.yaml` → `models.ollama-local.api_model_id` на реальный тег после `ollama pull`.

## 3. Последствия (Consequences)

### ✅ Плюсы
- Переключение провайдера — это правка одного YAML-файла, а не код. Когда Anthropic-доступ через omniroute починится, включить его обратно — тривиально.
- Ничего не сломалось: все 127 pytest всё ещё зелёные, воркфлоу/диспетчер/learning_loop не заметили смену провайдера (DI сработал ровно так, как задумывался в ADR-005/006).

### ❌ Минусы / Риски
- Ollama-модели (7-14B локально) заметно слабее Claude Opus/Sonnet по качеству — воркфлоу презентаций/писем может давать более грубый результат, пока не вернёмся на Claude.
- `api_model_id: llama3.1` — placeholder, требует подтверждения после `ollama pull`.
- Причина 401 от omniroute не расследована — если это просто опечатка в ключе, вернуться на Claude можно уже сейчас.

## 4. Статус (Status)
- [x] **Accepted** (2026-08-08, по прямому решению Виктора: "убираем антропик с клодом... ставлю оллама")

## 5. Связи (Links)
- Роадмап: [[.planning/ROADMAP]]
- Предыдущие решения: [[ADR-005-phase1-workflows]], [[ADR-006-phase2-scope-and-ui]]
