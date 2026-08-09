---
type: index
status: active
tags: [gsd, knowledge-base, hub]
created: 2026-03-20
updated: 2026-08-09
---

# 🧠 Knowledge Vault Index (MOC)

Этот раздел является "вторым мозгом" проекта и центральным узлом навигации (Map of Content). Здесь хранятся долгосрочные знания, архитектурные решения и контекст, который агент использует для глубокого понимания проекта между сессиями.

## 🏛 [[Architecture]]
- **Decision Records**: [[ADR-004-phase0-scaffold]] · [[ADR-005-phase1-workflows]] · [[ADR-006-phase2-scope-and-ui]] · [[ADR-007-ollama-primary]] · [[ADR-008-ollama-model-tiers]] · [[ADR-009-memory-graph-and-autonomy-ladder]] · [[ADR-010-jarvis-system-prompt]] (плюс отменённый [[ADR-003-ui-strategy]]).
- **Templates**: См. [[ADR_TEMPLATE]] для записи новых архитектурных решений.
- **Storage**: Локальные JSON-хранилища (`storage/tasks_store.py`, `storage/decisions_store.py`) — не Prisma/Supabase, см. [[ADR-004-phase0-scaffold]].

## 📝 [[Sessions]]
- **Chronology**: [[2026-08-09_bootstrap-to-phase2-and-ollama-pivot]] — от чистого репозитория до Phase 2 + смена LLM-провайдера на Ollama.
- **Context Recovery**: Позволяет быстро восстановить нить разработки после перерыва или переключения между задачами.

## 🧩 [[Modules]]
- **Code Documentation**: Техническое описание конкретных модулей, компонентов и интеграций.
- **UI Patterns**: Технические паттерны и переиспользуемые компоненты проекта.

## 💼 Business Context
- **Vision**: Описание бизнес-логики и целей проекта (ссылается на [[PROJECT_IDEA]]).
- **Audience**: Целевая аудитория и ключевые Jobs-to-be-Done.

---

## 🛠 Knowledge Workflow
1. **Search**: Перед началом задачи агент использует `obsidian-skills` для поиска по этому индексу.
2. **Update**: Executor обновляет [[Architecture]] или [[Modules]] при внесении значимых правок.
3. **Persist**: Команда `/save` автоматически линкует новую сессию в раздел [[Sessions]].

> **Engineering Note**: База знаний должна быть такой же чистой и структурированной, как звук **Greco Les Paul 1975**. Никакого мусора, только рабочие связи [[Wikilinks]].