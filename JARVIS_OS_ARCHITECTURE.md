# JARVIS OS - Complete Architecture Document

**Project:** Jarvis OS  
**Owner:** Viktor  
**Status:** Architecture Finalized, Ready for Implementation  
**Last Updated:** 2026-08-08

---

## TABLE OF CONTENTS

1. [Vision](#vision)
2. [Core Principles](#core-principles)
3. [Architecture Overview](#architecture-overview)
4. [Core Components](#core-components)
5. [Interfaces](#interfaces)
6. [Workflows](#workflows)
7. [Storage Structure](#storage-structure)
8. [Learning System](#learning-system)
9. [LLM Routing Strategy](#llm-routing-strategy)
10. [Domain Structure](#domain-structure)
11. [Plugin System](#plugin-system)
12. [Integrations](#integrations)
13. [Task Lifecycle](#task-lifecycle)
14. [Key Features](#key-features)
15. [MVP Roadmap](#mvp-roadmap)
16. [Configuration Templates](#configuration-templates)
17. [Decision Log](#decision-log)

---

## VISION

An autonomous agent that:
- Manages tasks across multiple domains (ИНТЦ, Bootlegger, House, Education)
- Generates high-quality deliverables (presentations, reports, emails, analytics)
- Learns from every correction to improve future work
- Adapts to stakeholder preferences automatically
- Optimizes scheduling and prioritization based on historical data
- Operates via voice, chat, and Telegram
- Runs on multiple LLM backends (Claude, Ollama, LM Studio)
- Executes tasks autonomously or collaboratively

**Metaphor:** Iron Man's Jarvis, but for personal/business operations management.

---

## CORE PRINCIPLES

### Mandatory (Non-negotiable)
1. **Single voice interface** — All interactions via chat (primary) or Telegram (secondary)
2. **Obsidian as source of truth** — All memory, knowledge, decisions stored as structured markdown
3. **Learn from feedback** — Every correction builds stakeholder profiles, improves estimation, updates templates
4. **Modular domains** — Add/edit/delete entire domains (ИНТЦ, Bootlegger, House, Education, etc)
5. **Multi-LLM backend** — Config-driven routing between Claude, Ollama, hybrid learning
6. **Extensible plugins** — Add skills and MCPs via drag-drop or GitHub URLs
7. **Transparent decision-making** — Always explain why (mentoring mode)
8. **Quality assurance** — Pre-completion checks based on stakeholder history

### Design Philosophy
- **Config first, UI second** — Behavior defined in YAML, UI displays configs
- **Fallback chains** — Never fail completely; degrade gracefully
- **Async everywhere** — Telegram, desktop, scheduled tasks all async
- **Privacy by default** — Local models for simple tasks, Claude only when needed
- **User teaches system** — Every "why" question builds better future predictions

---

## ARCHITECTURE OVERVIEW

```
┌─────────────────────────────────────────────────────────────────┐
│                    JARVIS OS CORE                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─ Intent Router ────────────────────────────────────────┐   │
│  │  Detects: task type, urgency, domain, stakeholder      │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─ LLM Router ───────────────────────────────────────────┐   │
│  │  Config-based: Claude vs Ollama vs Hybrid              │   │
│  │  Fallback: chain of models if primary fails            │   │
│  │  Learning: track success rates, suggest overrides      │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─ Context Engine ───────────────────────────────────────┐   │
│  │  Queries Obsidian vault                                │   │
│  │  Pulls: stakeholder profiles, templates, past decisions│   │
│  │  Augments: with live data (FusionPOS, Bitrix, web)     │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─ Task Executor ────────────────────────────────────────┐   │
│  │  Chains skills + MCPs based on task type               │   │
│  │  Handles: autonomy check, parallel execution, queuing  │   │
│  │  Manages: retries, fallbacks, error handling           │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─ Output Generator ─────────────────────────────────────┐   │
│  │  Produces: PPTX, XLSX, DOCX, JSON, Dashboard           │   │
│  │  Uses: templates from vault, applies customizations    │   │
│  └────────────────────────────────────────────────────────┘   │
│                          ↓                                      │
│  ┌─ Learning Loop ────────────────────────────────────────┐   │
│  │  Tracks: actual time vs estimate, quality metrics      │   │
│  │  Updates: stakeholder profiles, templates, tone prefs  │   │
│  │  Suggests: improvements, overrides, automations        │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

              ↓                              ↓
    ┌─────────────────┐          ┌──────────────────┐
    │   WEB UI        │          │  TELEGRAM BOT    │
    │  (Desktop)      │          │   (Mobile/Async) │
    ├─────────────────┤          ├──────────────────┤
    │ • Chat          │          │ • Text input     │
    │ • 3D Graph      │          │ • File upload    │
    │ • Calendar      │          │ • Quick decisions│
    │ • Dashboard     │          │ • Notifications  │
    │ • Plugin Mgr    │          │ • Async preview  │
    │ • Domain Mgr    │          └──────────────────┘
    └─────────────────┘

              ↓
    ┌─────────────────────────┐
    │  OBSIDIAN VAULT         │
    │  (Single Source Truth)  │
    ├─────────────────────────┤
    │ /tasks                  │
    │ /stakeholders           │
    │ /domains                │
    │ /templates              │
    │ /decisions              │
    │ /knowledge_base         │
    └─────────────────────────┘

              ↓
    ┌──────────────────────────────┐
    │  INTEGRATIONS                │
    ├──────────────────────────────┤
    │ • Bitrix API (tasks)         │
    │ • FusionPOS API (bar metrics)│
    │ • Google Calendar            │
    │ • GitHub (skills/MCPs)       │
    │ • N8n (automation)           │
    │ • Web Search                 │
    │ • Telegram Bot API           │
    └──────────────────────────────┘
```

---

## CORE COMPONENTS

### 1. Intent Router
**Purpose:** Classify incoming task and route to appropriate workflow

**Inputs:**
- Task description (chat or Telegram)
- Context (domain, stakeholder if mentioned)
- Historical data (similar tasks)

**Outputs:**
- Task type: `presentation` | `report` | `email` | `analysis` | `automation` | `qa`
- Domain: `ИНТЦ` | `bootlegger` | `house` | `education` | `personal`
- Urgency: `routine` | `priority` | `critical`
- Stakeholder: if identifiable
- Autonomous: `true` | `false` (can system do it alone?)

**Logic:**
```python
if "презентация" in task.lower():
    task_type = "presentation"
    ask_stakeholder = True
    ask_structure = True
elif "отчет" in task.lower():
    task_type = "report"
    autonomy = can_fetch_data(domain) # check if data available
elif "письмо" in task.lower():
    task_type = "email"
    autonomy = True
```

---

### 2. LLM Router
**Purpose:** Route task to appropriate model based on config + learning

**Config-driven routing:**
```yaml
routing_rules:
  email_generation:
    primary: claude-sonnet
    observer: ollama-mistral  # learns from example
    fallback: claude-opus
    
  data_analysis:
    primary: claude-opus
    time_critical: ollama-local
    fallback: claude-sonnet
    
  simple_classification:
    primary: ollama-local
    fallback: claude-sonnet
    
  research:
    primary: claude-opus
    fallback_allowed: false
```

**Learning component:**
- Track success rate per model per task type
- Store in Obsidian: `decisions/llm_routing_metrics.md`
- After 10 tasks: suggest override ("Ollama-local всегда справляется с классификацией, переводить на Claude?")
- Viktor can approve or reject suggestion

**Fallback chain:**
1. Try primary model
2. If error → try fallback_1
3. If error → try fallback_2
4. If all fail → notify Viktor with error details

---

### 3. Context Engine
**Purpose:** Assemble context for task execution

**Data sources:**
1. **Obsidian vault queries:**
   - Stakeholder profile (if known)
   - Past similar tasks and decisions
   - Relevant templates
   - Domain knowledge base

2. **Live data fetchers:**
   - Bitrix API (current tasks, assignments)
   - FusionPOS API (bar metrics, inventory)
   - Google Calendar (availability, scheduling)
   - Web search (if research task)

3. **Cache DB:**
   - Full-text index of Obsidian
   - Query optimization
   - Sync metadata

**Example flow:**
```
Task: "Презентация резидентов для Трутнева"
↓
Fetch Трутнев stakeholder profile:
  - focus_areas: [Инвестиции, Продукты, Выручка]
  - visual_preference: светлый фон, эмодзи
  - past_presentations: [prev_1, prev_2, prev_3]
↓
Query residents data from ИНТЦ knowledge base:
  - Company list with KPIs
  - Recent updates
  - Investment info
↓
Check FusionPOS (if needed):
  - Bar metrics for context
↓
Assemble context bundle → pass to Task Executor
```

---

### 4. Task Executor
**Purpose:** Execute task using appropriate skills + MCPs

**Steps:**
1. Check autonomy (can Viktor be skipped?)
2. Determine skill chain (which skills needed in order)
3. Fetch required data (MCPs)
4. Execute skills sequentially or parallel
5. Handle errors with fallbacks
6. Store intermediate results
7. Generate output

**Example: Presentation generation**
```
1. Data Collection Skill
   - Fetch residents from ИНТЦ KB
   - Fetch metrics from FusionPOS
   - Fetch stakeholder preferences from Трутнев profile
   
2. Content Verification (interactive)
   - Present findings to Viktor in chat
   - Ask for corrections/approvals
   - Update context
   
3. Mockup Generation Skill
   - Create slide structure
   - Apply Трутнев visual preferences
   - Generate preview
   
4. Viktor approval (if needed)
   - Show mockup
   - Request feedback
   
5. Data Filling Skill
   - Fill verified data into mockup
   - Apply formatting
   - Generate PPTX
   
6. Review (Viktor final check)
   - Iterate if corrections needed
   - Complete when satisfied
```

---

### 5. Learning Loop
**Purpose:** Improve future task execution based on feedback

**Tracked metrics:**
- `task_type`: classification accuracy
- `time_estimated` vs `time_actual`: historical data for better estimates
- `quality_feedback`: corrections, iterations needed
- `stakeholder_preferences`: build profile from corrections
- `template_effectiveness`: which templates lead to fewer revisions
- `model_performance`: which LLM handled task best

**Feedback collection:**
1. **Automatic:** time tracking (start → completion)
2. **Interactive:** "почему ты это изменил?" → captures reasoning
3. **Post-task:** quality score, iterations, satisfaction
4. **Manual override:** Viktor can correct any metric

**Storage in Obsidian:**
```yaml
task: Презентация резидентов Трутнев 2026-08
task_type: presentation
completed_at: 2026-08-08T15:30
time_estimated: 45 min
time_actual: 52 min
quality_iterations: 2
stakeholder: Трутнев

decisions:
  - slide_3: убрал партнеров (Трутнев не интересует)
  - visual: светлый фон с эмодзи (как и ожидал)
  
confidence: 0.95 (next time: use template_X, emphasize_focus_Y)
```

---

## INTERFACES

### Web UI (Desktop)

**Tech Stack:**
- Frontend: Next.js + React
- Visualization: Three.js or Babylon.js (3D graph)
- Charts: Chart.js or Recharts
- UI Components: Tailwind CSS or Material-UI
- State: Redux or Zustand
- API: WebSocket for real-time

**Main Views:**

#### 1. Chat Interface (Primary)
```
┌──────────────────────────────────────┐
│ JARVIS OS                      [⚙️]   │
├──────────────────────────────────────┤
│                                      │
│ System: Доброе утро. Начинаю        │
│ собирать материалы для ...           │
│                                      │
│ Viktor: Нужна презентация резидентов│
│                                      │
│ System: Это для Трутнева?           │
│ [Да] [Нет] [Кого-то еще]            │
│                                      │
├──────────────────────────────────────┤
│ [Type message...] [📎] [🎤] [Send]   │
└──────────────────────────────────────┘
```

#### 2. 3D Graph Visualization
```
Obsidian vault rendered as 3D network graph
- Nodes: tasks, stakeholders, templates, decisions, knowledge
- Colors: by domain (ИНТЦ=blue, Bootlegger=red, House=green)
- Size: by relevance/frequency
- Click node → open in sidebar
- Drag to explore → zoom in/out
- Search → highlight paths
```

#### 3. Calendar/Scheduling
```
Week view:
- Tasks with time estimates
- Free slots (where autonomous tasks can run)
- Deadlines
- Reminders (tasks approaching deadline)
- Color-coded by domain
- Conflict detection (impossible deadlines)
```

#### 4. Dashboard
```
Overview metrics:
- Burndown chart (tasks by day)
- Distribution (tasks by domain)
- Quality metrics (estimate vs actual, iterations)
- LLM performance (success rates by model)
- Time tracking (where does Viktor's time go)
- Recent completions
- Upcoming deadlines
```

#### 5. Plugin Manager
```
Available Skills:
[Search...] [+ Add Skill]

Built-in:
- Research
- Analysis
- Design
- Writing

Custom/External:
[Skill Name] [v1.0] [Enabled] [⚙️] [🗑️]
- Dependencies: [shown]
- Last used: [date]
- Success rate: [%]

Add from:
- Local ZIP
- GitHub URL (with validation)
```

#### 6. Domain Manager
```
Domains:

[ИНТЦ]      [Bootlegger]    [Дом]      [Образование]  [+ Add]
├─ 5 modules
├─ 12 skills
├─ 7 stakeholders
└─ [⚙️ Settings] [Edit] [Archive]

Add new domain:
- Name: [input]
- Color: [picker]
- Icon: [selector or emoji]
- Auto-create standard folders? [checkbox]
- Link to skills/MCPs: [multi-select]
```

---

### Telegram Bot

**Capabilities:**
- Text input (task description, corrections, approvals)
- File upload (DOCX, PDF, images for analysis)
- Quick decisions (buttons: Yes/No, Choose from options)
- Status updates (notifications on progress)
- Preview summaries (text or image thumbnails)
- Download links (to full files on desktop UI)

**Example flow:**

```
Viktor (in car):
  /new_task Нужна презентация резидентов для Трутнева

Bot:
  ✅ Начинаю собирать материалы
  Это для Трутнева как обычно? [Да] [Нет]

Viktor:
  [Да]

Bot:
  📊 Собрал данные. Нашел 3 варианта структуры:
  A) 4 компании на слайде (краткий)
  B) 1 компания на слайде (полный)
  C) Миксованный
  
  Для Трутнева обычно [A]. Верно? [Да] [Другой]

Viktor:
  [Да]

Bot:
  Создаю мокап... ⏳
  
  ✅ Готово. Превью: [small image]
  Слайд 1: Титульный лист
  Слайд 4-19: Компании (по 4 на слайде)
  Слайд 20: Будущее ИНТЦ
  
  Одобряешь структуру? [Да] [Правка]

Viktor:
  Правка: добавить слайд про инвестиции после титула

Bot:
  ✅ Переделал. Новая структура:
  [updated structure]
  
  Заполняю данными... ⏳
  
  ✅ Презентация готова: [download link]
  (также доступна в desktop UI для финальной правки)

Viktor:
  Спасибо!

Bot:
  ✅ Задача завершена
  ⏱️ Заняло: 52 мин (оценка была 45)
  📊 Сохранил в базу для Трутнева
```

**Architecture:**
```
telegram_bot.py (handlers)
├─ /new_task (intake)
├─ /status (check progress)
├─ /approve (quick approval)
├─ /reject (with reason)
└─ [button handlers]
    ↓
message_queue.py (async)
├─ Store messages
├─ Retry logic
└─ Sync with desktop
    ↓
sync_service.py
├─ Keep Telegram ↔ Desktop in sync
├─ Update task status both ways
└─ Handle conflicts (same task edited both places)
    ↓
task_executor (same core engine)
├─ Execute regardless of interface
└─ Send updates to both Telegram & Desktop
```

---

## WORKFLOWS

### Workflow 1: Presentation Generation

**Actors:** System (Jarvis), Viktor (approver/corrector)

**Steps:**

1. **Intake**
   ```
   Viktor: "Нужна презентация резидентов для Трутнева"
   System: [parse task, fetch Трутнев profile]
   System: "Это для Трутнева (как в прошлый раз)? 
            Делаю упор на Инвестиции/Продукты? Светлый фон?"
   ```

2. **Data Collection**
   ```
   System: [fetch from ИНТЦ knowledge base]
   - Residents list with KPIs
   - Recent funding/investments
   - Products/services
   - Team info (if relevant)
   ```

3. **Content Verification** (interactive)
   ```
   System: "Вот что нашел:"
   - Компания X: Product Y, Funding $Z, Team: N people
   - Компания A: Product B, Funding $C, Team: M people
   [...]
   
   Viktor: [reviews, corrects]
   "Компания X: Funding actually $Z1 (не $Z)"
   
   System: [updates context]
   ```

4. **Structure Approval**
   ```
   System: "Структура (как для Трутнева):
            Слайд 1: Титульный лист (пилотная площадка ИНТЦ)
            Слайды 2-17: Резиденты (4 на слайде, всего 16)
            Слайд 18: Будущее ИНТЦ (НОКи, школа, жилье)"
   
   Viktor: [approves or suggests changes]
   "Вариант B вместо A" или "Добавить слайд про инвестиции"
   ```

5. **Mockup Generation**
   ```
   System: [generates slide layouts without data]
   - Apply visual preferences (светлый фон, эмодзи)
   - Create structure
   - Show preview to Viktor
   ```

6. **Mockup Approval**
   ```
   Viktor: [reviews mockup]
   "Слайд 3: заголовок переделать, добавить график"
   
   System: [updates mockup]
   ```

7. **Data Filling**
   ```
   System: [fills verified data into mockup]
   - Inserts company info
   - Applies formatting
   - Generates final PPTX
   ```

8. **Final Review**
   ```
   Viktor: [downloads PPTX, reviews]
   - Any corrections?
   ```

9. **Complete & Learn**
   ```
   Viktor: "Готово!"
   
   System: [saves]
   - Final PPTX
   - Decision log (what changed, why)
   - Time tracking (actual: 52 min, estimated: 45 min)
   - Quality score (2 iterations on mockup, 0 on data)
   - Updates Трутнев profile (confidence on preferences)
   - Adds to templates if novel approach
   ```

---

### Workflow 2: Report Generation (Automated)

**Example:** Weekly bar metrics report

**Setup (one-time):**
```
Viktor: "Каждый понедельник выдавай отчет по бару"
System: "Какие метрики? (выручка, расходы, ABC анализ, 
         продукты по дням, целевая vs факт?)"
Viktor: "Все из них, плюс граждане за неделю"
System: "Создаю N8n workflow"
```

**Execution (automated):**
```
Every Monday 8:00 AM:
1. Fetch from FusionPOS API:
   - Sales data (revenue, by product, by day)
   - Expenses (breakdown)
   - Inventory changes
   
2. Analysis skill:
   - ABC анализ продуктов
   - Day-by-day variance
   - Forecast for next week
   
3. Visualization:
   - Revenue chart
   - Product breakdown (pie)
   - Daily comparison
   - Expense breakdown
   
4. Report generation:
   - Markdown summary
   - XLSX with data
   - Dashboard URL
   
5. Delivery:
   - Save to Obsidian
   - Send to Viktor via Telegram + Desktop
   - Store in /knowledge_base/bar/weekly_reports/
```

**Learning:**
```
Store metrics:
- execution_time
- data_freshness (all data available or partial?)
- errors (if any)

Viktor feedback (if any):
- "добавить еще метрику X"
- "этот график не нужен"

System updates N8n workflow automatically
```

---

### Workflow 3: Email Correspondence

**Steps:**

1. **Letter Intake**
   ```
   Viktor: [uploads letter from УК]
   System: [analyzes]
   "От УК. Тема: подтверждение статуса резидента.
    Ключевой вопрос: сроки платежей уточнить?"
   ```

2. **Content Analysis**
   ```
   System: [extracts key points]
   - Sender: УК
   - Topic: resident status confirmation
   - Key questions: payment schedule
   - Tone: formal
   ```

3. **Thesis from Viktor**
   ```
   Viktor: [provides response points]
   "Подтвердить что контракт активен
    Сроки платежа: по графику (ссылка на контракт)
    Добавить про льготу Q4"
   ```

4. **Formal Response Generation**
   ```
   System: [pulls УК email template]
   System: [applies formal tone]
   System: [generates response based on thesis]
   
   ---
   [УК letterhead]
   
   Уважаемый [name]!
   
   Подтверждаем, что статус резидента 
   инновационного центра "Русский" активен...
   [full formal response]
   
   С уважением,
   [signature block]
   ---
   ```

5. **Review & Corrections**
   ```
   Viktor: [reads response]
   "Правка: льготу Q4 описать подробнее"
   
   System: [updates] → new version
   ```

6. **Template Learning**
   ```
   Viktor: "Готово!"
   
   System: [saves]
   ├─ response_text: "Подтверждаем что статус..."
   ├─ recipient: УК
   ├─ topic: resident_status
   ├─ key_elements: [confirmation, schedule, benefit]
   ├─ tone_applied: formal_corporate
   └─ effectiveness: 1.0 (accepted first try)
   
   Next time УК writes about resident status:
   "Похоже на письмо про статус резидента.
    Использую шаблон от Августа?"
   ```

---

### Workflow 4: Task Management (Lifecycle)

**State machine:**
```
                  ┌─────────────┐
                  │   QUEUED    │
                  └──────┬──────┘
                         │ (estimate + schedule)
                         ↓
        ┌─────────────────────────────────┐
        │  CAN SYSTEM EXECUTE ALONE?      │
        └────────────┬────────────────────┘
                     │
         ┌───────────┴───────────┐
         │ YES               NO  │
         ↓                       ↓
    ┌────────┐            ┌──────────────┐
    │READY   │            │AWAITING INPUT│
    └────┬───┘            └──────┬───────┘
         │ (wait for free slot)  │
         │                       │ Viktor says "приступил"
         ↓                       ↓
    ┌────────────────────────────────┐
    │        IN_PROGRESS              │
    │    (start_time = now)           │
    └────────────┬───────────────────┘
                 │ (execute skills)
                 ↓
    ┌────────────────────────────────┐
    │    AWAITING_REVIEW              │
    │  (system generated output)      │
    └────────────┬───────────────────┘
                 │ (Viktor reviews)
    ┌────────────┴──────────────┐
    │ APPROVED          CORRECTED
    │   │                   │
    │   │                   ↓
    │   │            ┌─────────────┐
    │   │            │IN_PROGRESS  │
    │   │            │(iterate)    │
    │   │            └──────┬──────┘
    │   │                   │
    │   └───────┬───────────┘
    │           ↓
    │    ┌──────────────┐
    │    │  COMPLETED   │
    │    │  (learn)     │
    │    └──────────────┘
    │
    └─→ [save to vault, update stakeholder profile, 
         improve estimates, log decisions]
```

**Key timestamps:**
- `created_at`: task intake
- `estimated_at`: system estimates time
- `started_at`: Viktor says "приступил" or system auto-starts
- `completed_at`: Viktor says "готово"
- `actual_duration`: completed_at - started_at

---

## STORAGE STRUCTURE

### Obsidian Vault Organization

```
vault/
├─ tasks/
│  ├─ [task_id]_presentation_intc.md
│  │  ├─ YAML frontmatter (metadata)
│  │  ├─ Description
│  │  ├─ Timeline
│  │  ├─ Decisions made
│  │  └─ Learning outcomes
│  └─ [...]
│
├─ stakeholders/
│  ├─ Трутнев.md
│  │  ├─ Profile (focus areas, preferences)
│  │  ├─ Presentation history
│  │  ├─ Correction patterns
│  │  ├─ Confidence scores
│  │  └─ Next recommendations
│  ├─ Чекунков.md
│  ├─ Фальков.md
│  └─ [others]
│
├─ domains/
│  ├─ ИНТЦ.md
│  │  ├─ Domain settings
│  │  ├─ Associated modules
│  │  ├─ Key stakeholders
│  │  └─ Linked templates/skills
│  ├─ Bootlegger.md
│  ├─ Дом.md
│  ├─ Образование.md
│  └─ [user-created]
│
├─ templates/
│  ├─ presentations/
│  │  ├─ ИНТЦ_резиденты.md
│  │  ├─ ИНТЦ_инвесторы.md
│  │  └─ [others]
│  ├─ emails/
│  │  ├─ УК_письма.md
│  │  ├─ Фонд_письма.md
│  │  └─ [others]
│  ├─ reports/
│  │  ├─ bar_weekly.md
│  │  ├─ ИНТЦ_quarterly.md
│  │  └─ [others]
│  └─ schemas/
│
├─ decisions/
│  ├─ 2026_08_Трутнев_presentation.md
│  │  ├─ Corrections made
│  │  ├─ Reasoning (why Viktor changed each element)
│  │  ├─ Patterns identified
│  │  └─ Confidence update
│  └─ [by date and stakeholder/domain]
│
├─ knowledge_base/
│  ├─ ИНТЦ/
│  │  ├─ residents.md (list with KPIs)
│  │  ├─ market_trends.md
│  │  ├─ investments.md
│  │  ├─ regulations.md
│  │  └─ innovations.md
│  ├─ Bootlegger/
│  │  ├─ menu.md (products, costs, margins)
│  │  ├─ suppliers.md (contacts, terms)
│  │  ├─ customers.md (patterns)
│  │  ├─ weekly_reports/ (archive)
│  │  └─ financial/ (historical)
│  ├─ House/
│  │  ├─ design_decisions.md
│  │  ├─ contractors.md
│  │  ├─ schedule.md
│  │  └─ budget_tracking.md
│  └─ Personal/
│
├─ learning/
│  ├─ llm_routing_metrics.md
│  │  (track which model works best for what)
│  ├─ estimation_accuracy.md
│  │  (historical time estimates vs actual)
│  ├─ stakeholder_learning.md
│  │  (feedback patterns per stakeholder)
│  └─ quality_metrics.md
│
├─ automations/
│  ├─ n8n_workflows.md
│  │  (registry of created workflows)
│  ├─ scheduled_tasks.md
│  │  (recurring reports, monitoring)
│  └─ triggers.md
│     (Bitrix webhooks, etc)
│
└─ system/
   ├─ routing_config.yaml
   ├─ domains_config.yaml
   ├─ plugins_registry.md
   ├─ mcps_registry.md
   └─ tones.yaml
```

---

## LEARNING SYSTEM

### Quality Assurance (Pre-completion)

**Concept:** Before Viktor says "готово", system checks based on stakeholder history

**Example:**

```
Presentation created for Трутнев
System: "Перед тем как ты завершишь, я заметил что 
         для Трутнева ты обычно проверяешь:
         
         ☐ Инвестиционные цифры (правильны?)
         ☐ Цвета бренда ИНТЦ (соответствуют?)
         ☐ Логотипы резидентов (все есть?)
         ☐ Слайд про будущее (актуален?)
         
         Ты все проверил перед завершением?"

Viktor: "Ой, забыл про логотипы! Дай еще минуту"
[fixes]
Viktor: "Готово!"
```

**Implementation:**
```python
def quality_assurance_check(task, stakeholder_profile):
    checks = stakeholder_profile.get('usual_checks', [])
    # Build checklist from past corrections
    
    system_message = f"Перед завершением проверь:"
    for check in checks:
        system_message += f"\n☐ {check}"
    
    return system_message
```

---

### Why Extraction (Learning from Corrections)

**Every correction gets a reason:**

```
Viktor corrects: "Убрать партнеров со слайда"
System: "Почему убирать партнеров? 
         (чтобы я запомнил для следующего раза)"

Viktor: "Трутнев не интересуется экосистемой партнеров.
         Его интересуют только инвестиции и продукты."

System: [saves to Трутнев profile]
{
  anti_focus: [партнеры],
  reason: "не интересует экосистема",
  confidence: 0.9
}

Next time for Трутнев:
"Как обычно, убираю партнеров со слайдов?"
```

---

### Mentoring Mode (Transparency)

**Viktor can ask "почему?"**

```
Viktor: "Почему ты для Трутнева выбрал эту структуру?
         (4 компании на слайде, а не 1?)"

System: "Потому что в последних 3 презентациях для него 
         ты одобрил эту структуру без правок, 
         а альтернативная требовала 2-3 итерации.
         
         Также, с 4 компаниями на слайде:
         - Меньше слайдов (больше фокуса)
         - Лучше для презентации перед инвесторами
         - Трутнев обычно одобряет это с первой попытки"
```

---

### Stakeholder Profiling (Dynamic)

**Not filled at start; built from corrections**

```yaml
stakeholder: Трутнев
presentations_total: 5
profile:
  focus_areas: [Инвестиции, Продукты, Выручка]
  anti_focus: [Партнеры, Экосистема]
  visual_preference:
    background: светлый
    images: только эмодзи/иконки, без фото
    layout: минималистичный
  revision_pattern:
    avg_iterations: 1.2
    typical_changes: [структура, визуал]
  time_to_approval: 25 мин (avg)
  confidence: 0.95
  last_updated: 2026-08-08
  
prev_presentations:
  - 2026-08-01: резиденты (approved no changes)
  - 2026-07-25: инвесторы (2 revisions)
  - 2026-07-10: ecosystem (rejected, redone)
```

---

### Time Estimation & Historical Data

**Improves with every completed task**

```yaml
task_type_estimates:
  presentation:
    avg_time: 45 min
    confidence: 0.92
    variance: ±15 min
    factors:
      - stakeholder: Трутнев (+5 min, focused changes)
      - stakeholder: Фальков (-10 min, flexible)
      - complexity: many_companies (+20 min)
      - complexity: simple_update (-10 min)
  
  email:
    avg_time: 10 min
    confidence: 0.95
  
  report:
    avg_time: 30 min
    confidence: 0.90
```

**When scheduling new task:**
```
Task: "Презентация для Трутнева (много компаний)"
Estimate = 45 (base) + 5 (Трутнев) + 20 (complexity) = 70 min
Confidence = 0.87 (accounting for variance)

Display to Viktor:
"Оценка: 70 мин (±15), уверенность 87%.
 Deadline завтра в 5 PM. Хватит времени?
 Или упростить требования?"
```

---

## LLM ROUTING STRATEGY

### Config File: `routing.yaml`

```yaml
version: 1.0

# Default models
defaults:
  primary_model: claude-opus
  fallback_chain: [claude-sonnet, ollama-local]
  timeout_seconds: 60

# Task-specific routing
routing_rules:
  # Complex analysis
  market_research:
    primary: claude-opus
    fallback: claude-sonnet
    reason: "needs deep reasoning"
    budget_aware: false
  
  # Writing (Opus could be overkill)
  email_generation:
    primary: claude-sonnet
    observer: ollama-mistral
    reason: "Sonnet sufficient, Ollama learns"
    observer_role: "watch and learn tone patterns"
  
  # Simple classification
  task_classification:
    primary: ollama-local
    fallback: claude-sonnet
    reason: "local is instant, no internet"
    fallback_condition: "if confidence < 0.7"
  
  # Data analysis (time-critical in bar context)
  bar_metrics_analysis:
    primary: claude-opus
    time_critical_fallback: ollama-local
    reason: "Opus for accuracy, Ollama for speed"
  
  # Compliance-critical (never local)
  contract_analysis:
    primary: claude-opus
    fallback_allowed: false
    reason: "legal risk - no local models"
  
  # Research
  market_research:
    primary: claude-opus
    requires_web: true
    fallback: false

# Hybrid learning mode
hybrid_mode:
  enabled: true
  observer_models: [ollama-local, ollama-mistral]
  log_to: decisions/llm_learning_log.md
  
  # When to sync observations
  sync_interval: 10 tasks
  
  # Suggest override after N successful tasks
  confidence_threshold: 0.95
  sample_size: 10

# Fallback chain behavior
fallback_behavior:
  retry_delay_seconds: 2
  max_retries: 3
  log_errors: true
  notify_on_fallback: true # alert Viktor if went to fallback
  
# Model-specific settings
models:
  claude-opus:
    cost_per_k_tokens: 0.015
    speed: slow
    reasoning: excellent
    web_search: true
    
  claude-sonnet:
    cost_per_k_tokens: 0.003
    speed: medium
    reasoning: good
    web_search: true
  
  ollama-local:
    cost: 0
    speed: fast
    reasoning: medium
    web_search: false
    models:
      - mistral:7b
      - neural-chat
```

### Routing Logic (Pseudocode)

```python
def route_task(task, config):
    task_type = task.get_type()
    
    # Check config
    routing = config.get(f"routing_rules.{task_type}")
    
    if not routing:
        routing = config.get("defaults")
    
    # Try primary model
    try:
        result = call_model(routing.primary, task)
        if routing.observer:
            observe_with(routing.observer, task, result)
        return result
    
    except Exception as e:
        # Try fallback chain
        for fallback_model in routing.fallback_chain:
            try:
                result = call_model(fallback_model, task)
                notify_viktor(f"Primary failed, used {fallback_model}")
                return result
            except:
                continue
        
        # All failed
        raise TaskExecutionError("All models failed")

def observe_with(observer_model, task, result):
    """
    Run observer model alongside to learn
    Save observations to learning log
    """
    observer_result = call_model(observer_model, task)
    
    # Compare
    log_observation({
        'task_type': task.type,
        'primary_result': result,
        'observer_result': observer_result,
        'similarity': compare(result, observer_result),
        'timestamp': now(),
    })
    
    # Periodically suggest overrides
    check_if_suggest_override()
```

---

## DOMAIN STRUCTURE

### ИНТЦ (Innovation Center)

```
ИНТЦ/
├─ Analytics/
│  ├─ Residents Monitor (track KPIs, trends, investments)
│  ├─ Market Research (competitive landscape, innovations)
│  ├─ Investment Tracking (funding rounds, valuation changes)
│  └─ Innovation Trends (what's happening in tech)
│
├─ Documentation/
│  ├─ Presentations (for stakeholders: investors, governors)
│  ├─ Reports (quarterly KPIs, annual summaries)
│  ├─ Case Studies (resident success stories)
│  └─ Contracts (templates, versions with residents)
│
├─ Communications/
│  ├─ Stakeholder Letters (УК, Фонд, Губернатор)
│  ├─ Resident Support (FAQ, onboarding materials)
│  └─ Media Relations (press releases, announcements)
│
├─ Operations/
│  ├─ Resident Onboarding (flow automation, documents)
│  ├─ KPI Tracking (dashboard, monitoring)
│  ├─ Event Planning (conferences, networking)
│  └─ Resource Allocation (space, services)
│
└─ Knowledge Base/
   ├─ Residents (company profiles, contact, KPIs)
   ├─ Market Data (trends, competitors, opportunities)
   ├─ Regulations (local, federal, tax, labor)
   └─ Best Practices (lessons learned, case studies)
```

### Bootlegger (Bar)

```
Bootlegger/
├─ Sales & Analytics/
│  ├─ Weekly Reports (revenue, costs, ABC analysis, trends)
│  ├─ Menu Optimization (what sells, margins, timing)
│  ├─ Customer Analytics (patterns, preferences, loyalty)
│  └─ Demand Forecasting (weekend vs weekday, seasonality)
│
├─ Finance/
│  ├─ Expense Tracking (automated from FusionPOS)
│  ├─ Supplier Management (orders, contracts, negotiation)
│  ├─ Budget Planning (monthly, quarterly)
│  └─ Tax Reporting (consolidated, ready for accountant)
│
├─ Inventory/
│  ├─ Stock Monitoring (real-time from FusionPOS)
│  ├─ Reorder Alerts (when to order more)
│  ├─ Supplier Comparisons (price, quality, delivery)
│  └─ Waste Analysis (identify patterns)
│
├─ Marketing/
│  ├─ Social Media (content calendar, analytics)
│  ├─ Promotions (planning, tracking effectiveness)
│  └─ Customer Communications (loyalty, special offers)
│
└─ Knowledge Base/
   ├─ Menu (recipes, costs, margins, availability)
   ├─ Suppliers (contacts, terms, quality ratings)
   ├─ Customers (VIP list, preferences, history)
   ├─ Competitors (pricing, menu, location)
   └─ Regulatory (permits, health codes, labor laws)
```

### Дом (House Build)

```
Дом/
├─ Construction/
│  ├─ Schedule Tracking (Gantt chart, % completion, milestones)
│  ├─ Budget Monitoring (spent vs plan, cost overruns, contingency)
│  ├─ Risk Management (delays, quality issues, weather impact)
│  └─ Quality Assurance (inspections, photo documentation)
│
├─ Documentation/
│  ├─ Contracts (with contractors, terms, payment schedule)
│  ├─ Permits (building, environmental, fire safety)
│  ├─ Technical Specs (materials, finishes, appliances)
│  └─ As-built Documentation (final layouts, changes)
│
├─ Finance/
│  ├─ Payment Scheduling (contractor invoices, milestones)
│  ├─ Budget Forecasting (next quarter expenses)
│  ├─ Cost Breakdown (materials, labor, services)
│  └─ Change Order Tracking (scope adjustments, costs)
│
├─ Stakeholder Management/
│  ├─ Contractor Communication (updates, issues, payments)
│  ├─ Regulatory Bodies (permits, inspections, approvals)
│  ├─ Neighbor Relations (construction schedule, noise)
│  └─ Status Reports (for Viktor's family, investors)
│
└─ Knowledge Base/
   ├─ Design Decisions (why X not Y, approved layouts)
   ├─ Supplier/Contractor Contacts (quality, reliability)
   ├─ Building Codes (local, regional, federal)
   ├─ Material Specs (costs, durability, availability)
   └─ Lessons Learned (what worked, what to avoid next time)
```

### Образование (Education - when Viktor enrolls)

```
Образование/
├─ Learning Management/
│  ├─ Curriculum Planning (what to study when)
│  ├─ Study Schedule (integration with main calendar)
│  ├─ Progress Tracking (chapters completed, skills acquired)
│  └─ Assessment Prep (exams, projects, deadlines)
│
├─ Content Organization/
│  ├─ Course Materials (notes, readings, videos)
│  ├─ Key Concepts (mind maps, summaries)
│  ├─ Problem Sets (practice questions, solutions)
│  └─ Reference Library (textbooks, papers, links)
│
├─ Performance/
│  ├─ Grades/Scores (tracking, trends)
│  ├─ Weak Areas (identify topics needing more work)
│  ├─ Learning Patterns (preferred study times, modalities)
│  └─ Goal Progress (towards degree, skills, certifications)
│
└─ Knowledge Base/
   ├─ Course Syllabus (official outline, assignments)
   ├─ Professor Info (office hours, email, expectations)
   ├─ Study Resources (recommended books, websites, tutors)
   └─ Alumni Insights (how others passed, tips)
```

**All domains are:**
- ✅ User-creatable (+ Add domain button)
- ✅ Editable (rename, reorder, recolor)
- ✅ Deletable (archive or hard delete)
- ✅ Modular (modules are templates; custom modules possible)

---

## PLUGIN SYSTEM

### Skill Architecture

**Skill manifest (`SKILL.md` or `manifest.json`):**

```yaml
id: skill_market_research
name: Market Research Pro
version: 1.0.0
author: Viktor
description: |
  Conducts deep market research: 
  - competitive analysis
  - trend identification
  - data aggregation
  - visualization
  
triggers:
  - task_type: research
  - keywords: [market, competitor, trend, opportunity]

inputs:
  - type: text
    name: market_description
    required: true
  - type: url
    name: reference_urls
    required: false
  - type: file
    name: existing_research
    required: false

outputs:
  - format: markdown
    name: research_summary
  - format: json
    name: structured_data
  - format: html
    name: interactive_dashboard

dependencies:
  - web_search
  - data_analysis
  - visualization

resources:
  - llm: claude-opus (primary)
  - storage: 100MB
  - timeout: 3600 seconds

cost:
  per_execution: "based on Claude tokens"

installation:
  - source: github
    url: https://github.com/viktor/skill-market-research
  - source: local
    path: /home/viktor/skills/market_research

enable: true
```

### MCP Architecture

**MCP manifest:**

```yaml
id: mcp_fusionpos
name: FusionPOS Connector
version: 1.0.0
type: data_source
description: |
  Real-time data from FusionPOS API
  - sales transactions
  - inventory levels
  - customer data
  - expense tracking

endpoints:
  - method: GET
    path: /api/v3/orders
    description: Fetch orders for period
    auth: api_key
    
  - method: GET
    path: /api/v3/inventory
    description: Get current inventory
    auth: api_key
  
  - method: POST
    path: /api/v3/orders
    description: Create order (for automation)
    auth: api_key

authentication:
  type: api_key
  location: header
  key_name: X-API-Key
  secret_storage: obsidian_secure_vault

rate_limits:
  requests_per_minute: 100
  requests_per_hour: 5000

cache:
  enabled: true
  ttl_seconds: 300

enable: true
```

### Plugin Manager UI

```
┌─────────────────────────────────────────┐
│ PLUGIN MANAGER                    [🔄]  │
├─────────────────────────────────────────┤
│ Search: [___________] [Filter] [+ Add]  │
├─────────────────────────────────────────┤
│                                         │
│ SKILLS (12)                             │
│ ├─ Market Research Pro [v1.0] [✓ ON]   │
│ │  Dependencies: web_search, analysis   │
│ │  Last used: 2 hours ago              │
│ │  Success rate: 94%                    │
│ │  [⚙️] [🗑️]                             │
│ │                                       │
│ ├─ Email Generator [v1.0] [✓ ON]       │
│ ├─ Presentation Builder [v1.0] [✓ ON]  │
│ ├─ Data Analysis [v2.1] [✓ ON]         │
│ └─ [...]                               │
│                                         │
│ MCPs (8)                                │
│ ├─ FusionPOS Connector [v1.0] [✓ ON]   │
│ │  Endpoints: 15                        │
│ │  Last sync: 5 min ago                │
│ │  Rate limit: 100/min                 │
│ │  [⚙️] [🔑 API Key] [🗑️]                │
│ │                                       │
│ ├─ Bitrix Connector [v1.0] [✓ ON]      │
│ ├─ Obsidian Sync [v1.0] [✓ ON]         │
│ └─ [...]                               │
│                                         │
├─────────────────────────────────────────┤
│ Add new skill/MCP:                      │
│ [📁 Local ZIP] [🔗 GitHub URL]           │
│                                         │
│ Validation:                             │
│ ✓ Manifest valid                        │
│ ✓ Dependencies available                │
│ ✓ API key configured (if needed)       │
│ [INSTALL]                               │
└─────────────────────────────────────────┘
```

---

## INTEGRATIONS

### 1. Obsidian (Core)
- **Purpose:** Source of truth for all memory
- **Sync:** Real-time, bidirectional
- **API:** Obsidian REST API or plugin
- **Fallback:** Direct file system if API unavailable

### 2. Bitrix24 (Work Tasks)
- **Purpose:** Sync task assignments and deadlines
- **API:** Bitrix24 REST API (already known to Viktor)
- **Sync:** Every 1 hour + webhooks for new tasks
- **Features:**
  - Fetch active tasks with deadlines
  - Check task status
  - Create tasks automatically (if needed)
  - Extract task descriptions for analysis

### 3. FusionPOS (Bar Metrics)
- **Purpose:** Real-time sales, inventory, customer data
- **API:** FusionPOS REST API v3 (https://fusionpos.ru/api/v3/)
- **Endpoints used:**
  - GET `/api/v3/orders` — fetch sales
  - GET `/api/v3/inventory` — stock levels
  - GET `/api/v3/analytics` — metrics (if available)
  - POST `/api/v3/orders` — create orders (future)
- **Sync:** 
  - Hourly for reports
  - Real-time for dashboard
  - Cache with 5-min TTL for performance

### 4. Google Calendar
- **Purpose:** Schedule tasks, show availability
- **API:** Google Calendar API
- **Features:**
  - Create events for scheduled tasks
  - Check free slots for auto-execution
  - Pull Viktor's calendar for context
  - Send reminders (integrated)

### 5. GitHub (Skills & MCPs Distribution)
- **Purpose:** Version control for plugins, easy installation
- **Usage:**
  - Store skill repos (`skill-name.md` + code)
  - Store MCP configs
  - Install via: `[GitHub URL]` in Plugin Manager
- **Features:**
  - Semantic versioning
  - Changelog per update
  - Dependency resolution
  - Rollback to previous version

### 6. N8n (Automation Orchestration)
- **Purpose:** Create complex workflows (e.g., weekly reports)
- **Integration:**
  - Claude Code generates N8n JSON config from description
  - Deploy to N8n instance via API
  - N8n executes on schedule
  - Send results back to Jarvis
- **Example workflow:**
  ```
  Weekly report:
  1. FusionPOS API → fetch sales data
  2. Claude analysis → generate insights
  3. Create XLSX + charts
  4. Send to Telegram + Desktop
  ```

### 7. Telegram Bot API
- **Purpose:** Mobile interface for async tasks
- **Features:**
  - Receive messages, file uploads
  - Send status updates, previews
  - Quick decision buttons
  - Download links to files
- **Sync:** Real-time message queue, DB for deduplication

### 8. Web Search (Future)
- **Purpose:** Research tasks requiring current data
- **Service:** SerpAPI or similar
- **Usage:** When research skill needs live data
- **Cache:** Store results in vault for knowledge base

---

## TASK LIFECYCLE

```
┌─────────────────────────────────┐
│  TASK INTAKE (Viktor)           │
│  "Нужна презентация резидентов" │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  INTENT EXTRACTION              │
│  • Type: presentation           │
│  • Domain: ИНТЦ                 │
│  • Stakeholder: [ask]           │
│  • Urgency: [ask]               │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  CONTEXT ASSEMBLY               │
│  • Load stakeholder profile     │
│  • Load past similar tasks      │
│  • Fetch relevant templates     │
│  • Query knowledge base         │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  TIME ESTIMATION                │
│  • Base: 45 min                 │
│  • Stakeholder: Трутнев (+5)    │
│  • Complexity: high (+20)       │
│  • Total: 70 min (±15)          │
│  • Confidence: 0.87             │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  AUTONOMY CHECK                 │
│  Can system do this alone?      │
│  • Data available? YES          │
│  • Skills exist? YES            │
│  • Needs human review? YES      │
│  → Status: READY (await input)  │
└────────────┬────────────────────┘
             │
             ↓ (Viktor "приступил")
┌─────────────────────────────────┐
│  EXECUTION                      │
│  Skill chain:                   │
│  1. Data collection             │
│  2. Content verification        │
│  3. Mockup generation           │
│  4. (Interactive review)        │
│  5. Data filling                │
│  6. Final PPTX generation       │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  REVIEW & ITERATION             │
│  Viktor provides feedback:      │
│  • Approves → continue          │
│  • Corrects → re-execute        │
│  • Asks questions → explain     │
└────────────┬────────────────────┘
             │
             ↓ (Viktor "готово!")
┌─────────────────────────────────┐
│  COMPLETION & LEARNING          │
│  Save:                          │
│  • Final deliverable (PPTX)     │
│  • Decision log (what changed)  │
│  • Time metrics (actual: 52)    │
│  • Quality feedback (2 iter)    │
│  • Update stakeholder profile   │
│  • Suggest improvements         │
└─────────────────────────────────┘
```

---

## KEY FEATURES

### 1. Presentation Generation
- ✅ Multi-step workflow (collect → verify → mockup → fill → review)
- ✅ Stakeholder-aware (Трутнев preferences auto-applied)
- ✅ Template system (reusable structures)
- ✅ Interactive corrections
- ✅ Learning from feedback (correc patterns stored)

### 2. Report Automation
- ✅ Scheduled generation (e.g., every Monday)
- ✅ Data aggregation from multiple sources (FusionPOS, Bitrix, web)
- ✅ Analysis + visualization
- ✅ Multiple output formats (markdown, XLSX, charts, dashboard)
- ✅ Auto-delivery (Telegram + Desktop)

### 3. Email Correspondence
- ✅ Letter analysis (who, what topic, urgency)
- ✅ Formal response generation (with tone modulation)
- ✅ Template saving + learning
- ✅ Version control (track changes)

### 4. Task Management
- ✅ Intake → Estimation → Scheduling → Execution → Learning
- ✅ Autonomy detection (can system do it alone?)
- ✅ Parallel execution (multiple tasks if slots available)
- ✅ Reminder system (deadline approaching)
- ✅ Quality assurance (checklist before completion)

### 5. Stakeholder Learning
- ✅ Dynamic profiles (built from corrections, not hardcoded)
- ✅ Preference extraction (visual, tone, focus areas)
- ✅ Confidence scoring (0.0-1.0, based on consistency)
- ✅ Mentoring mode (explain why)

### 6. Multi-LLM Backend
- ✅ Config-driven routing (Claude vs Ollama)
- ✅ Fallback chains (graceful degradation)
- ✅ Hybrid learning (one executes, other observes)
- ✅ Performance tracking (cost, speed, quality per model)

### 7. Plugin System
- ✅ Drag-drop installation (local ZIP)
- ✅ GitHub integration (one-click from URL)
- ✅ Dependency resolution
- ✅ Enable/disable per skill
- ✅ Version management + rollback

### 8. Telegram Integration
- ✅ Async task intake
- ✅ File upload/download
- ✅ Quick decisions (buttons)
- ✅ Status notifications
- ✅ Sync with desktop

### 9. 3D Memory Visualization
- ✅ Interactive graph (nodes: tasks, stakeholders, templates, knowledge)
- ✅ Color-coded by domain
- ✅ Search + highlight paths
- ✅ Zoom + drag navigation
- ✅ Click node → open details

### 10. Scheduling & Optimization
- ✅ Calendar integration (show free slots)
- ✅ Conflict detection (impossible deadlines)
- ✅ Auto-scheduling (fit tasks in available time)
- ✅ Priority optimization (based on deadline + complexity + learnings)
- ✅ Reminders (24h, 4h, 1h before deadline)

---

## MVP ROADMAP

### Phase 0 (Week 1): Foundation & Core Infrastructure
**Goal:** Basic system running, chat interface working

**Tasks:**
1. Initialize repository structure
2. Set up Obsidian vault integration
3. Implement basic Intent Router
4. Create Chat interface (React/Next)
5. LLM Router (config-based, no learning yet)
6. Context Engine (vault queries + basic aggregation)
7. Task storage (Obsidian + SQLite cache)

**Deliverables:**
- [ ] Repo with folder structure
- [ ] Design Doc complete
- [ ] Chat interface (basic)
- [ ] Obsidian vault template
- [ ] LLM Router config template
- [ ] Skill registry template
- [ ] MCP registry template

**Testing:**
- [ ] Can create task via chat
- [ ] Can route to correct workflow
- [ ] Can query Obsidian successfully
- [ ] LLM routing works (local + Claude)

---

### Phase 1 (Week 2-3): Core Workflows
**Goal:** Full workflow execution (presentation, report, email)

**Tasks:**
1. Implement Presentation Workflow
   - Data collection (vault + FusionPOS)
   - Content verification (interactive)
   - Mockup generation
   - Data filling
   - PPTX output
2. Implement Report Workflow
   - Data aggregation
   - Analysis skill
   - Visualization
   - XLSX/markdown output
3. Implement Email Workflow
   - Letter analysis
   - Response generation
   - Tone modulation
4. Quality Assurance checks
5. Why Extraction (capture correction reasons)
6. Mentoring Mode (explain decisions)

**Deliverables:**
- [ ] Full presentation workflow (text → mockup → fill → approve)
- [ ] Full report workflow (data → analyze → visualize → deliver)
- [ ] Full email workflow (letter → thesis → formal → template)
- [ ] QA checks before completion
- [ ] Reason logging for every correction
- [ ] Decision explanations

**Testing:**
- [ ] Create presentation, iterate 2-3 times, complete
- [ ] Generate weekly bar report
- [ ] Write formal email response

---

### Phase 2 (Week 3-4): Learning & Scheduling
**Goal:** System learns from corrections, schedules intelligently

**Tasks:**
1. Stakeholder Profiling
   - Build profiles from corrections
   - Confidence scoring
   - Preference extraction
2. Time Estimation Improvements
   - Track actual_time vs estimate
   - Adjust estimates by stakeholder + complexity
   - Historical data-based predictions
3. Calendar Integration
   - Google Calendar sync
   - Show free slots
   - Schedule tasks automatically
4. Reminder System
   - 24h, 4h, 1h before deadline
   - Via Telegram + Desktop notification
5. Telegram Bot
   - Basic text + file handling
   - Async workflow
   - Status updates
   - Quick decisions (buttons)

**Deliverables:**
- [ ] Stakeholder profiles auto-built from corrections
- [ ] Time estimates improve by 20%+
- [ ] Calendar integration working
- [ ] Reminders firing on schedule
- [ ] Telegram bot receiving/sending messages
- [ ] Desktop ↔ Telegram sync

**Testing:**
- [ ] Create 5 presentations for same stakeholder, see profile improve
- [ ] Estimate time, track actual, compare
- [ ] Task scheduled in free slot on calendar
- [ ] Received reminder 4h before deadline
- [ ] Use Telegram to create task, see it in desktop UI

---

### Phase 3 (Week 4+): Autonomy & Advanced Features
**Goal:** System auto-executes simple tasks, optimizes prioritization

**Tasks:**
1. Autonomy Detection
   - Classify which tasks system can do alone
   - Which need Viktor's input
   - Execute autonomous tasks in free slots
2. Parallel Execution
   - Queue management
   - Dependency tracking
   - Resource allocation
3. Dashboard
   - Burndown chart (tasks by domain)
   - Quality metrics (estimate vs actual)
   - LLM performance tracking
4. 3D Graph Visualization
   - Render Obsidian vault as 3D graph
   - Interactive exploration
   - Search + highlight

**Deliverables:**
- [ ] System auto-executes weekly bar report in free slot
- [ ] Dashboard shows all metrics
- [ ] 3D graph visualization live
- [ ] Multiple tasks queued and executed in parallel

**Testing:**
- [ ] Weekly report generated automatically on schedule
- [ ] Dashboard updates in real-time
- [ ] Click node in 3D graph → open in sidebar
- [ ] Two tasks executing in parallel without conflicts

---

### Future Phases (Post-MVP)
- [ ] Historical comparison (deadline realism checks)
- [ ] Proactive suggestions ("this is like the task from July")
- [ ] Cross-domain pattern sharing (bar process applies to ИНТЦ?)
- [ ] Energy/cognitive load tracking
- [ ] Audit trail + version control
- [ ] Multi-user support (if Viktor has assistant)
- [ ] Voice interface (STT/TTS)
- [ ] Advanced priority optimization (ML-based)
- [ ] Automated N8n workflow generation
- [ ] Advanced LLM learning (fine-tune local models)

---

## CONFIGURATION TEMPLATES

### `routing.yaml` (LLM Routing)
See LLM Routing Strategy section above

### `domains.yaml` (Domain Configuration)
```yaml
domains:
  ИНТЦ:
    color: "#0066FF"
    icon: "🏢"
    modules:
      - Analytics
      - Documentation
      - Communications
      - Operations
      - Knowledge Base
    stakeholders:
      - Трутнев
      - Чекунков
      - Фальков
    skills:
      - Market Research Pro
      - Presentation Builder
    mcps:
      - FusionPOS (if applicable)
      - Web Search
  
  Bootlegger:
    color: "#FF6600"
    icon: "🍹"
    modules:
      - Sales & Analytics
      - Finance
      - Inventory
      - Marketing
      - Knowledge Base
    mcps:
      - FusionPOS Connector
  
  Дом:
    color: "#00CC00"
    icon: "🏠"
    modules:
      - Construction
      - Documentation
      - Finance
      - Stakeholder Management
      - Knowledge Base
```

### `tones.yaml` (Email Tones)
```yaml
tones:
  formal_corporate:
    description: "Formal, official business correspondence"
    keywords:
      - Уважаемый
      - Подтверждаем
      - В соответствии с
      - С уважением
    examples:
      - УК письма
      - Контрактные письма
    
  friendly_professional:
    description: "Professional but warm, less formal"
    keywords:
      - Привет
      - Спасибо
      - С лучшими пожеланиями
    examples:
      - Письма коллегам
      - Письма партнерам
  
  technical:
    description: "Technical, precise, spec-focused"
    keywords:
      - Согласно спецификации
      - Требуемые характеристики
      - Техническое описание
    examples:
      - Письма подрядчикам
      - Спецификации
  
  investment:
    description: "Investor-focused, opportunities highlighted"
    keywords:
      - Инвестиционный потенциал
      - ROI
      - Стратегический рост
    examples:
      - Письма инвесторам
      - Питч-письма
```

---

## DECISION LOG

### Architecture Decisions Made

**1. Obsidian as Source of Truth**
- **Decision:** All memory stored in Obsidian vault
- **Rationale:** 
  - Viktor already uses Obsidian
  - Markdown is human-readable + machine-queryable
  - Native graph visualization
  - File-based (no proprietary DB)
  - Portable (easy to backup, migrate)
- **Tradeoffs:**
  - Slower than database for complex queries (mitigated with SQLite cache)
  - Requires sync logic with cache

**2. Multi-LLM Backend**
- **Decision:** Config-driven routing (Claude primary, Ollama fallback)
- **Rationale:**
  - Cost optimization (simple tasks on local)
  - Resilience (if Claude API down, use local)
  - Learning (Ollama watches Claude for improvement)
  - Privacy (some data stays local)
- **Tradeoffs:**
  - Complex routing logic
  - Need to maintain local model definitions
  - Requires careful testing of fallbacks

**3. Telegram + Web UI (vs single interface)**
- **Decision:** Two interfaces: Web (desktop, full features) + Telegram (mobile, async)
- **Rationale:**
  - Viktor needs mobile access (on the go, in car)
  - Telegram: quick text + file, async, notifications
  - Web: full visualization, 3D graph, calendar, dashboard
  - Async architecture allows both simultaneously
- **Tradeoffs:**
  - Sync complexity between interfaces
  - Duplicate UI logic (partially)

**4. Chat as Primary Input (vs voice-first)**
- **Decision:** Chat as MVP, voice as Phase 3+
- **Rationale:**
  - Chat faster to implement (no STT/TTS quality issues)
  - More precise (avoid speech recognition errors)
  - Viktor's workflow (already using text in work)
  - Can test learning without voice complexity
- **Tradeoffs:**
  - Voice convenience lost (for now)
  - Will add ~2 week delay to full Jarvis vision

**5. Learning from Corrections (Why extraction)**
- **Decision:** After every correction, ask "почему?" to capture reasoning
- **Rationale:**
  - Feedback alone isn't enough ("removed partner slide")
  - Understanding WHY enables generalization (all Трутнев presentations? only this one?)
  - Builds better stakeholder profiles
  - Transparent (Viktor teaches system)
- **Tradeoffs:**
  - Extra step (one question per correction)
  - Requires Viktor's time to explain
  - False positives possible (system misinterprets reasoning)

**6. Config Files Over UI Builder**
- **Decision:** Routing, tones, domains configured in YAML files
- **Rationale:**
  - Version control (git history of changes)
  - Transparency (system behavior is documented)
  - Easy to rollback (previous config version)
  - No UI builder bugs
  - Can be templated (share configs across users)
- **Tradeoffs:**
  - Requires Viktor to edit YAML (not beginner-friendly)
  - But: UI can auto-generate YAML from form inputs

**7. Plugin System (Drag-drop + GitHub)**
- **Decision:** Two installation methods: local ZIP + GitHub URLs
- **Rationale:**
  - Drag-drop: simple, local, no internet
  - GitHub: version control, easy updates, community sharing
  - Manifest validation (prevent bad skills)
  - Dependency resolution (system knows what's needed)
- **Tradeoffs:**
  - Need to validate both formats
  - Requires GitHub repo structure standards
  - Security risk (arbitrary code execution) — mitigated by sandboxing

---

## GETTING STARTED

### For Claude Code Session

When transferring to Claude Code:

1. **Read this entire document** as context
2. **Ask Viktor clarifications** only on items marked `[?]` (none currently)
3. **Start with Phase 0** (foundation)
4. **Follow the roadmap** sequentially
5. **Update `DECISION LOG`** as new decisions made
6. **Test against `Testing` section** in each phase

### Files to Prepare

1. Email templates (UК, Фонд)
2. PowerPoint templates (for presentations)
3. FusionPOS API documentation (endpoints needed)
4. Bitrix24 API documentation (task sync)
5. Obsidian vault template (folder structure)

### Key Contacts / Resources

- **FusionPOS API:** https://fusionpos.ru/api/v3/
- **Bitrix24 API:** (Viktor's account)
- **Telegram Bot API:** https://core.telegram.org/bots/api
- **Google Calendar API:** https://developers.google.com/calendar
- **N8n Docs:** https://docs.n8n.io/

---

**END OF DOCUMENT**

**Version:** 1.0  
**Last Updated:** 2026-08-08  
**Status:** Ready for Claude Code Implementation  
**Next Step:** Initialize repository in Claude Code
