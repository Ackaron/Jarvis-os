# 🧠 Obsidian Knowledge Management (Kepano Standard + Skills)

## 1. Automated Knowledge Control
- **Skill Usage**: Агент обязан использовать установленные `obsidian-skills` для поиска, создания и редактирования заметок.
- **Deep Search**: Вместо простого чтения файлов, используй скилл поиска по всему `vault/` для нахождения контекста в старых сессиях или ADR.
- **Link Management**: Используй автоматическое управление `[[Wikilinks]]`, чтобы поддерживать целостность графа знаний без "битых" связей.

## 2. Structural Principles (The Architecture)
- **Atomic Notes**: Одна заметка = одна идея, модуль или ADR. Избегай длинных документов.
- **Maps of Content (MOC)**: Используй `vault/index.md` как центральный узел (Hub). Категории: `Architecture`, `Sessions`, `Database`, `Business Logic`.
- **Kepano Folder Logic**:
  - `vault/architecture/` — проектные решения (ADR).
  - `vault/sessions/` — логи сессий от команды `/save`.
  - `vault/modules/` — документация компонентов кода.

## 3. Metadata Standard (YAML)
Каждая заметка ОБЯЗАНА начинаться с YAML-блока:
```yaml
---
type: {feature | adr | session | module | idea}
status: {idea | in-progress | completed | archived}
tags: [gsd, project-name]
created: YYYY-MM-DD
updated: YYYY-MM-DD
---