# 🕹️ CLAUDE.md | Project Control Center (Universal Pro Max)

## 🎯 Core Directives
- **Spec-First**: Никакого кода без актуальной спецификации в `SPECIFICATION.md`.
- **GSD Logic**: Работай строго через субагентов (Planner -> Executor -> Verifier).
- **Atomic Actions**: Одна задача из `ROADMAP.md` = одна итерация изменений.
- **UI/UX Fidelity**: Весь интерфейс строго по `.rules/ui-ux.md`.
- **Super-Informed**: При любых сомнениях используй **MCP Google Search** или **Fetch** для проверки документации.

## 📚 Source of Truth (Hierarchy)
1. **Vision**: `PROJECT_IDEA.md` (Зачем и для кого).
2. **Blueprints**: `SPECIFICATION.md` (Технический чертеж и типы данных).
3. **Task Force**: `.claude/agents/` (Роли: Planner, Executor, Verifier).
4. **Design Code**: `.rules/ui-ux.md` (Дизайн-регламент проекта).
5. **Memory**: `vault/index.md` (Архитектурные решения ADR и логи сессий).

## 🛠 Project Lifecycle
- **Planning**: `/plan` -> обновление `.planning/ROADMAP.md` и `STATE.md` через субагента Planner.
- **Development**: `/execute` -> реализация текущей задачи из плана субагентом Executor.
- **UI Engineering**: `/ui` -> проектирование и внедрение UI-компонентов проекта.
- **Deep Logic**: `/think` -> использование **Sequential Thinking** для сложных архитектурных задач.
- **Validation**: `/review` -> проверка субагентом Verifier (Playwright) на соответствие SPEC и UI-правилам.
- **Persistence**: `/save` -> сохранение лога сессии в `vault/sessions/` и синхронизация связей в Obsidian через `obsidian-skills`.

## ⚙️ Environment & Setup
- **Agent Context**: Будь лаконичен, технически точен и следуй музыкальной философии (надежный тон Greco Les Paul 1975).
- **Capabilities**: Доступен **MCP Protocol** (Magic UI, Search, Sequential Thinking, Fetch, Playwright).
- **Rules Persistence**: Папка `.rules/` обязательна к исполнению для всех операций.

## ⌨️ Quick Commands
- **Dev**: `npm run dev`
- **Build**: `npm run build`

## 🚀 Initial Machine Setup
- **Secret Management**: Никогда не пиши реальные ключи в файлы, кроме `.env`. Добавь `.env` в `.gitignore`.
- **Obsidian Skills (Kepano)**: 
  1. Выполни установку скиллов для OpenCode: 
     `git clone https://github.com/kepano/obsidian-skills.git ~/.opencode/skills/obsidian-skills`.
  2. Скопируй стандарты управления знаниями в `.rules/obsidian.md`.
- **Playwright Skill (Recommended Setup)**: 
    1. `/plugin marketplace add lackeyjb/playwright-skill`.
    2. `/plugin install playwright-skill@playwright-skill`.
    3. `cd ~/.claude/plugins/marketplaces/playwright-skill/skills/playwright-skill && npm run setup`.