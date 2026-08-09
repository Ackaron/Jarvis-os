# 💡 PROJECT_IDEA: Jarvis OS — Personal AI Management System

## 1. Проблема (The Pain)

### Суть боли
Viktor (PM, предприниматель, инноватор) решает ежедневно 5-10 задач разного характера:
- Подготовить презентацию для инвесторов ИНТЦ
- Провести анализ рынка для новой инициативы  
- Написать письмо в УК или фонд
- Отслеживать еженедельный отчет по бару
- Управлять строительством дома
- Планировать мониторинг новостей по теме
- Все это требует разного уровня автоматизации, но **нет единой системы**

### Текущий workflow (костыли)
1. **Task intake:** Письма падают в Bitrix, записки в Telegram, идеи в голове
2. **Context switching:** Нужно искать старые презентации, вспоминать как делал раньше, переделывать от руки
3. **No learning:** Каждый раз делает примерно одно и то же, но система не помнит как это было в прошлый раз
4. **Manual prioritization:** Не знает сколько времени займет, когда начать, что срочнее
5. **No templates:** Письма писать с нуля, хотя есть паттерны (письма в УК vs письма в фонд)
6. **Manual execution:** Все делает сам, даже если может делегировать ИИ
7. **Fragmented memory:** Знания рассыпаны по Obsidian, файлам, голове

### Метрики боли
- **40% времени на контекстные переключения** (ищет нужные файлы, вспоминает детали)
- **3-4 итерации на каждой презентации** из-за отсутствия профилей заказчиков (Трутнев хочет одно, Фальков другое)
- **0 переиспользования кода/решений** (каждый раз с нуля, хотя 70% задач повторяются)
- **100% ручная работа** (даже простые отчеты)
- **25% времени на вспоминание как это было в прошлый раз** (архивы в Obsidian, но нужно искать)

---

## 2. Решение (The Concept)

### Основная ценность (One Liner)
**Jarvis OS** — автономный ИИ-помощник, который управляет задачами, генерирует высокие качества deliverables, учится из каждого решения и интеллектуально приоритизирует работу.

### Аналогия
Как Jarvis из "Iron Man" — не просто отвечает на вопросы, но и **предвидит потребности, управляет системами, адаптируется к предпочтениям хозяина**.

### Key differentiator vs просто Claude в чате
- ✅ **Память**: Все решения, stakeholder preferences, templates в Obsidian графе
- ✅ **Autonomy**: Может выполнять задачи БЕЗ запроса Viktor (еженедельный отчет в фоне)
- ✅ **Learning**: Каждая правка → обновляет profile (Трутнев = инвестиции, светлый фон)
- ✅ **Intelligent routing**: Простые задачи → локальная модель (быстро), сложные → Claude (качество)
- ✅ **Multi-interface**: Работает в web (полный контроль), в Telegram (мобильно), запущен как demon (фоновые задачи)
- ✅ **Structured workflows**: Не просто генерирует текст, а проводит interactive verification → mockup → fill → review

### User Journey (Step-by-Step)

#### Сценарий 1: Презентация
```
1. [Viktor в Telegram]: "Нужна презентация резидентов для Трутнева"
   ↓
2. [Jarvis анализирует]:
   - Вспоминает: Трутнева 5 презентаций, он обычно хочет: Инвестиции, Продукты, светлый фон
   - Asks: "Это для Трутнева как обычно?" [Да/Нет buttons]
   ↓
3. [Viktor одобрил]:
   - Jarvis начинает собирать данные (ИНТЦ residents DB)
   - Выписывает: "Вот что нашел: компания X (продукт Y, инвест $Z)"
   - Viktor верифицирует: "Правильно, но инвест $Z1 не $Z"
   ↓
4. [Jarvis создает mockup]:
   - Показывает структуру: "4 компании на слайде (как для Трутнева)"
   - Viktor: "Ок, добавить слайд про инвестиции"
   ↓
5. [Jarvis заполняет данные]:
   - PPTX готов, Viktor проверяет
   - "Слайд 3: переделать заголовок"
   ↓
6. [Итерация, Viktor "Готово!"]:
   - Jarvis СОХРАНЯЕТ:
     - Финальную PPTX
     - Как именно it было сделано (решения, правки)
     - Время: estimated 45 min, actual 52 min
     - Confidence: "Trутнев profile" еще точнее
   ↓
7. [NEXT TIME]:
   - Трутневу нужна новая презентация
   - Jarvis: "Я знаю что Трутневу нужно инвестиции/продукты, светлый фон, 4 компании на слайде. Верно?"
   - Всё строится в разы быстрее
```

#### Сценарий 2: Еженедельный отчет (Автоматизированный)
```
1. [One-time setup]:
   - Viktor: "Каждый понедельник в 8 AM выдавай отчет по бару"
   - Jarvis спрашивает: "Какие метрики? (выручка, расходы, ABC, продукты по дням)"
   - Viktor: "Все"
   ↓
2. [Jarvis создает N8n workflow]:
   - Коннектит FusionPOS API
   - Планирует: каждый понедельник fetch данные
   - Jarvis.analyze() → charts, summary
   ↓
3. [Автоматическое выполнение]:
   - Каждый Monday 8:00 AM
   - FusionPOS → fetch sales, expenses
   - Claude.analyze() → insights
   - Генерирует XLSX + Telegram notification
   - Viktor получает link в Telegram
   ↓
4. [Learning]:
   - Если Viktor добавляет метрику → workflow обновляется
   - Execution metrics: сколько времени заняло, были ли ошибки
```

#### Сценарий 3: Email Correspondence
```
1. [Viktor uploads письмо от УК]:
   - Jarvis: "От УК. Тема: подтверждение статуса резидента. 
              Вопрос: сроки платежей уточнить?"
   ↓
2. [Viktor дает тезисы]:
   - "Подтвердить контракт активен. Платежи по графику. 
     Добавить про льготу Q4"
   ↓
3. [Jarvis генерирует]:
   - Берет шаблон письма УК (из памяти)
   - Применяет formal_corporate tone
   - Вставляет тезисы Viktor
   - Выдает готовое письмо (DOCX для печати)
   ↓
4. [Viktor вносит правку]:
   - "Льготу описать подробнее"
   - Jarvis update → новая версия
   ↓
5. [Learning]:
   - Сохраняет шаблон
   - "Письма УК с темой [resident_status]" — в памяти как best practice
   - Next time похожее письмо: "Использую шаблон от August?"
```

### Autonomous Task Execution
```
[Background daemon]:
- Jarvis видит что завтра deadline по отчету
- Смотрит календарь Viktor: 3 свободных часа
- Проверяет: есть ли данные, задача ясна?
- ДА → запускает выполнение, готовит draft к утру
- Viktor приходит, смотрит ready-to-review результат
```

---

## 3. Анализ рынка (Context)

### Конкуренты и альтернативы
1. **Claude в чате** — просто LLM, нет памяти, нет learning, каждый раз с нуля
2. **Make/Zapier automations** — можно создать workflow, но не адаптируется, нет learning
3. **Notion AI** — в контексте документа, но no autonomy, no multi-interface
4. **Specialized tools** (Prezz.io для презентаций, Jasper для письма) — разрозненные, нет унификации

### Наше отличие (Why we win)
- ✅ **All-in-one unified system** (не нужны 5 инструментов)
- ✅ **Learning from every decision** (stakeholder profiles, templates, time estimates)
- ✅ **True autonomy** (background execution, no "prompt me every time")
- ✅ **Multi-interface** (web for control, Telegram for async, daemon for background)
- ✅ **Local-first with Claude fallback** (privacy + cost optimization)
- ✅ **Transparent** (explain why, mentoring mode)

### Market positioning
- **Not for masses** → highly specialized for operators/PMs like Viktor
- **Proprietary data** → doesn't learn from anyone else's tasks (privacy, no data leakage)
- **Vertical integration** → built specifically for Viktor's multi-domain life (ИНТЦ, bar, house, education)

---

## 4. Целевая аудитория (Audience)

### Primary: Viktor (1 user for MVP)
- **Role**: PM, entrepreneur, innovator
- **Pain points**: 
  - Multiple domains (ИНТЦ, Bootlegger, House, Education)
  - Lots of stakeholders with different preferences (Трутнев, Чекунков, Фальков)
  - Context switching hell
  - No time to leverage past decisions
- **Success metric**: "I spend 80% less time on task preparation, more time on actual work"

### Secondary (Future): Small teams of operators
- Product managers in innovation centers
- Entrepreneurs managing multiple ventures
- Agency founders (need to create custom deliverables for different clients)

### Tertiary (v2+): Enterprise teams
- Corporate offices needing autonomous task management
- Distributed teams across time zones

### Jobs-to-be-Done
1. **"When I get a new task, I want to quickly route it to the right process, so I don't waste time deciding how to approach it"**
2. **"When I need to create similar deliverables for different stakeholders, I want the system to remember their preferences, so I don't redo work"**
3. **"When I'm busy, I want simple tasks to execute automatically, so I can focus on strategy"**
4. **"When I make a decision, I want the system to remember why, so I don't repeat mistakes"**

---

## 5. Экономика и Развитие (Value)

### MVP Scope (Phase 0-3, ~1 month)
**This is where we're building now.**

#### Phase 0 (Week 1): Foundation
- [ ] Chat interface + Intent Router
- [ ] Obsidian vault integration
- [ ] LLM Router (Claude + Ollama)
- [ ] Basic task storage

#### Phase 1 (Week 2-3): Core Workflows
- [ ] Presentation workflow (collect → verify → mockup → fill → approve)
- [ ] Report workflow (data → analyze → visualize → deliver)
- [ ] Email workflow (letter → thesis → formal → template)
- [ ] Quality Assurance checks
- [ ] Why Extraction (learn from corrections)
- [ ] Mentoring Mode (explain decisions)

#### Phase 2 (Week 3-4): Learning & Scheduling
- [ ] Stakeholder profiling (auto-built from corrections)
- [ ] Time estimation improvements
- [ ] Calendar integration
- [ ] Reminders system
- [ ] Telegram bot integration
- [ ] Desktop ↔ Telegram sync

#### Phase 3 (Week 4+): Autonomy
- [ ] Auto-execution in free slots
- [ ] Parallel execution
- [ ] Dashboard (burndown, quality metrics, LLM performance)
- [ ] 2D memory graph (force-directed, not 3D/Three.js — see ADR-009), node click → detail panel with an autonomy ladder (human-led → human-assisted → fully autonomous) instead of a bare boolean
- [ ] Second Brain search: question → answer + cited vault sources (extends `context_engine`)

### Монетизация (Not for MVP, but future)
1. **Personal use** → no monetization, just value creation (time savings)
2. **Team version** → licensing per seat, per-domain
3. **Enterprise** → custom integrations, SLA, advanced automation

### Future Scope (v2+, Not in MVP)
- [ ] Voice interface (STT/TTS, full voice control)
- [ ] Cross-domain pattern sharing (bar process → ИНТЦ?)
- [ ] Energy/cognitive load tracking (suggest easy tasks when tired)
- [ ] Advanced priority optimization (ML-based deadline realism)
- [ ] Fine-tuned local models (learn from Viktor's data)
- [ ] Multi-user support (if Viktor gets assistant)
- [ ] Advanced audit trail + version control
- [ ] Proactive suggestions ("this is like the July task")
- [ ] Historical comparison (deadline realism checks)
- [ ] Integration marketplace (allow external skills/MCPs)

---

## 6. Архитектура и Стек

### Архитектурная модель
```
┌─────────────────────────────────────┐
│     USER INTERFACE LAYER            │
├─────────────────────────────────────┤
│  Web UI (Next.js)                   │
│  ├─ Chat (primary input)            │
│  ├─ Memory Graph (2D, see ADR-009)  │
│  ├─ Calendar (scheduling)           │
│  ├─ Dashboard (metrics)             │
│  └─ Plugin Manager (CRUD)           │
│                                     │
│  Telegram Bot (async/mobile)        │
│  ├─ Quick text input                │
│  ├─ File uploads                    │
│  └─ Notifications                   │
└──────────┬──────────────────────────┘
           │
┌──────────▼──────────────────────────┐
│     JARVIS CORE (Python/FastAPI)    │
├─────────────────────────────────────┤
│  Intent Router                      │
│  LLM Router (config + learning)     │
│  Context Engine (Obsidian queries)  │
│  Task Executor (skill orchestration)│
│  Learning Loop (metrics, profiles)  │
│  Scheduler (cron, N8n integration)  │
└──────────┬──────────────────────────┘
           │
┌──────────▼──────────────────────────┐
│     MEMORY & INTEGRATIONS           │
├─────────────────────────────────────┤
│  Obsidian Vault (source of truth)   │
│  Cache DB (SQLite for fast queries) │
│                                     │
│  External APIs:                     │
│  ├─ FusionPOS (bar metrics)         │
│  ├─ Bitrix24 (tasks sync)           │
│  ├─ Google Calendar                 │
│  ├─ GitHub (skills/MCPs)            │
│  ├─ N8n (automation)                │
│  ├─ Claude API                      │
│  ├─ Ollama (local LLM)              │
│  └─ Telegram Bot API                │
└─────────────────────────────────────┘
```

### Tech Stack

#### Frontend (Web UI)
- **Framework**: Next.js 15 (App Router, Server Components)
- **Language**: TypeScript (strict mode)
- **UI Components**: Shadcn UI + Radix UI (accessible, unstyled)
- **Styling**: Tailwind CSS + CSS Variables
- **Visualization**: Three.js or Babylon.js (3D graph)
- **Charts**: Recharts (data visualization)
- **Animations**: Framer Motion (spring physics)
- **State Management**: Zustand (lightweight, no Redux complexity)
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod (validation)
- **API Client**: tRPC or Fetch (with error handling)

#### Backend (Core Engine)
- **Language**: Python 3.11+ (for AI/data processing) + Node.js (for real-time)
- **Framework**: FastAPI (async, type-safe, OpenAPI docs)
- **Database ORM**: Prisma (TypeScript) or SQLAlchemy (Python)
- **Job Queue**: Celery + Redis (background tasks, scheduled workflows)
- **Real-time**: WebSocket (FastAPI WebSocket or Socket.io)
- **API Gateway**: Could be single FastAPI, or split (Frontend API + Backend API)

#### Database
- **Primary**: PostgreSQL (Supabase for managed hosting)
- **Schema**: All `snake_case`, RLS enabled on every table
- **Migrations**: Prisma migrations or Alembic (SQLAlchemy)
- **Cache**: Redis (session, temporary data)
- **File Storage**: S3 or Supabase Storage (PPTX, XLSX, DOCX files)

#### LLM & AI
- **Primary**: Claude API (claude-opus for complex reasoning, claude-sonnet for speed)
- **Local**: Ollama + Qwen or Mistral (32k context local model)
- **LLM Routing**: Config-driven (routing.yaml), with learning suggestions
- **Embeddings**: Text-embedding-3-small from OpenAI or open-source alternative
- **Vector Store**: Pinecone or Weaviate (future: for semantic search in vault)

#### Automation & Scheduling
- **Workflows**: N8n (visual workflow builder, webhook support)
- **Job Scheduling**: APScheduler (Python) or node-cron (Node.js)
- **Message Queue**: Celery (async tasks)
- **Webhooks**: FusionPOS webhooks → Jarvis API, Bitrix webhooks → Jarvis API

#### Integrations
- **Obsidian**: Direct file system access + REST API plugin
- **Bitrix24**: REST API (already documented for Viktor)
- **FusionPOS**: REST API v3 (https://fusionpos.ru/api/v3/)
- **Google Calendar**: Google Calendar API + OAuth 2.0
- **GitHub**: GraphQL API (for skill/MCP distribution)
- **Telegram**: Telegram Bot API (polling or webhook)
- **N8n**: N8n REST API (create/update workflows)

#### DevOps & Deployment
- **Container**: Docker (for consistency)
- **Orchestration**: Docker Compose (local dev), Kubernetes (production, future)
- **CI/CD**: GitHub Actions (test on push, deploy on main)
- **Monitoring**: Sentry (error tracking), DataDog or Prometheus (metrics)
- **Logging**: Structured logs (JSON), stored in PostgreSQL or S3
- **Environment**: `.env` for secrets, never in code

### Design System & Aesthetic
- **Style**: dark, minimal, data-focused
  - Background: Pure Black (#000000) for main areas
  - Accent: Cyberpunk/cool blue (#0066FF or #00D9FF)
  - Text: Light gray on dark (WCAG AA contrast minimum)
  - Icons: Minimalist line-based (Tabler Icons or Feather)
  
- **Typography**: 
  - Headlines: Geist or Inter (modern, geometric)
  - Body: Inter (readable, web-optimized)
  - Monospace: JetBrains Mono (for data, timestamps, code)
  
- **Layout**: 
  - 8pt grid (all spacing/sizing multiples of 8)
  - Sidebar + Main content (responsive collapse on mobile)
  - Z-index stack: Base → Overlays → Modals → Notifications → Dropdowns
  
- **Animations**: 
  - Spring physics (Framer Motion `damping: 15, mass: 1, stiffness: 300`)
  - Micro-interactions (button scale on hover, fade-in on load)
  - No lag, no jank (60fps target)

---

## 7. Constraints & Non-Goals

### What We DO
✅ Task management with learning  
✅ Interactive content generation (presentations, emails, reports)  
✅ Stakeholder preference learning  
✅ Time estimation & scheduling  
✅ Multi-LLM routing  
✅ Background autonomous execution  
✅ Telegram async interface  

### What We DON'T (for MVP)
❌ Voice interface (future)  
❌ Video processing  
❌ Advanced ML fine-tuning  
❌ Social features  
❌ Real-time collaboration (multiple users on same task)  
❌ Mobile app (Telegram covers mobile for now)  
❌ Third-party marketplace (custom plugins only for now)  

---

## 8. Success Metrics

### User Level (Viktor's Experience)
- **Time savings**: "I spend 60% less time on task prep" (tracked by task completion times)
- **Quality consistency**: "First-draft quality matches approved quality" (fewer revisions)
- **Context switching reduction**: "No more than 2 minutes to context-switch between domains"
- **Satisfaction**: "Jarvis understands my preferences without me asking" (confidence scores > 0.9)

### System Level
- **LLM Router efficiency**: Local model handles 70%+ of simple tasks
- **Time estimation accuracy**: Estimate within ±15% of actual (after 30 tasks)
- **Learning effectiveness**: Stakeholder profile confidence > 0.85 after 5 interactions
- **Autonomy**: 30%+ of tasks execute fully without Viktor input

### Reliability
- **Uptime**: 99.5% (only scheduled downtime)
- **Zero data loss**: All decisions, metadata, outputs stored in vault/DB
- **No hallucinations affecting critical data**: Claude only used for creative tasks, local model for classification

---

## 9. Risk Assessment & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|-----------|
| LLM hallucinations in data | High | Medium | Validation layer (user verify all data before mockup) |
| Integration failures (FusionPOS, Bitrix) | High | Low | Fallback to manual data input, error notifications |
| Context window overflow | Medium | Low | Chunking strategies, archive old sessions in vault |
| Obsidian sync conflicts | Medium | Low | Version control (git-like history), conflict resolution UI |
| Privacy/data leakage | High | Very Low | RLS on all DB tables, local-first processing, no cloud logging of sensitive data |

---

**END OF PROJECT_IDEA**

**Status**: Ready for SPECIFICATION → Implementation  
**Owner**: Viktor  
**Last Updated**: 2026-08-08