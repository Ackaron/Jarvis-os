# 📐 TECHNICAL SPECIFICATION: Jarvis OS

**Version**: 1.0  
**Last Updated**: 2026-08-08  
**Status**: Ready for Implementation (Phase 0)  
**Owner**: Viktor  

---

## TABLE OF CONTENTS
1. [Архитектурный стек](#архитектурный-стек)
2. [Модель данных (Schema)](#модель-данных-schema)
3. [API & Server Actions](#api--server-actions)
4. [LLM Routing Configuration](#llm-routing-configuration)
5. [Business Logic & Workflows](#business-logic--workflows)
6. [User Stories & Features](#user-stories--features)
7. [UI/UX Экраны (Wireframes)](#uiux-экраны-wireframes)
8. [Security & RLS Policies](#security--rls-policies)
9. [Error Handling & Edge Cases](#error-handling--edge-cases)
10. [Testing Strategy](#testing-strategy)
11. [Deployment & Infrastructure](#deployment--infrastructure)

---

## Архитектурный стек

### Frontend (Web UI)
```
Technology Stack:
- Runtime: Node.js 20+
- Framework: Next.js 15+ (App Router, Server Components)
- Language: TypeScript 5+ (strict mode, no `any`)
- UI Framework: Shadcn UI + Radix UI (composition-based)
- Styling: Tailwind CSS 3+ with CSS custom properties
- Visualization: Three.js (3D graph) or Babylon.js
- Charts: Recharts for data visualization
- Animations: Framer Motion (spring physics)
- State: Zustand for global state
- Data Fetching: TanStack Query (React Query)
- Forms: React Hook Form + Zod (for validation)
- HTTP Client: Fetch API with custom wrapper
- Real-time: WebSocket via NextAuth or Socket.io

Deployment:
- Platform: Vercel (auto-deploy from GitHub)
- Edge Functions: For auth middleware
- CDN: Vercel Edge Network
- Database Proxy: Vercel KV (for caching)
```

### Backend (Core Engine)
```
Technology Stack:
- Language: Python 3.11+ (AI/data) + Node.js/TypeScript (API)
- Framework: FastAPI 0.100+ (async, type-safe)
- ASGI Server: Uvicorn
- Job Queue: Celery + Redis
- Real-time: FastAPI WebSocket or Socket.io
- Authentication: OAuth 2.0 + JWT (FastAPI dependency injection)
- Logging: Structured logging (JSON format to PostgreSQL)

Deployment:
- Container: Docker (Dockerfile + docker-compose)
- Orchestration: Docker Compose (local), Kubernetes (production)
- CI/CD: GitHub Actions (test → lint → build → deploy)
- Environment: .env (secrets via GitHub Secrets)
```

### Database
```
Technology Stack:
- Primary DB: PostgreSQL 15+ (via Supabase or self-hosted)
- ORM: Prisma (TypeScript) + SQLAlchemy (Python compatibility)
- Migrations: Prisma migrate (version controlled)
- Cache Layer: Redis (session, temporary data)
- File Storage: Supabase Storage (S3-compatible) for PPTX/XLSX/DOCX
- Search: Full-text search via PostgreSQL (tsvector)
- Real-time: Supabase Realtime (WebSocket subscriptions)

Security:
- All tables: Row Level Security (RLS) enabled
- Auth: User must be authenticated (Supabase Auth)
- Policies: auth.uid() = user_id for all user-owned data
```

### LLM & AI Stack
```
Technology Stack:
- Primary LLM: Claude 3.5 Opus / Sonnet (via Anthropic API)
- Local LLM: Ollama (Qwen 14B or Mistral 7B, 32k context)
- Embedding Model: text-embedding-3-small (OpenAI) or local alternative
- Vector Store: Weaviate or Pinecone (future)
- Orchestration: LangChain Python for model routing

Configuration:
- routing.yaml: LLM routing rules (which model for which task)
- learning.yaml: Model performance tracking
- Skills registry: Python modules (skill_*.py)
- MCPs registry: YAML manifests for external connectors
```

### Integrations & External APIs
```
Connectors:
- Obsidian: File system access + REST Plugin API
- Bitrix24: REST API (tasks, CRM)
- FusionPOS: REST API v3 (sales, inventory, analytics)
- Google Calendar: Google Calendar API + OAuth 2.0
- GitHub: GraphQL API (skill/MCP distribution)
- Telegram: Telegram Bot API (polling or webhook)
- N8n: N8n REST API (workflow CRUD)
- OpenAI: Embeddings API (if using)
- Anthropic: Claude API (primary LLM)

Authentication:
- Each service: API key stored in .env, loaded via ConfigParser
- No hardcoded secrets anywhere
- Rotation: Instructions in .env.example
```

---

## Модель данных (Schema)

### Design Principles
1. **All snake_case**: Tables, columns, enums
2. **UUID primary keys**: `id: UUID DEFAULT gen_random_uuid()`
3. **Timestamps everywhere**: `created_at`, `updated_at` (timestamptz)
4. **RLS enabled**: Every table must have RLS policy `auth.uid() = user_id`
5. **JSONB for flexibility**: `metadata`, `config`, `feedback` columns for unstructured data
6. **Enums for status**: `status` field uses PostgreSQL enum type
7. **Foreign keys**: Strict referential integrity

### Core Tables

#### 1. `users`
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  avatar_url TEXT,
  timezone TEXT DEFAULT 'UTC', -- for scheduling
  preferences JSONB DEFAULT '{}', -- {language, theme, etc}
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS: Users see only themselves
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only read themselves"
  ON users FOR SELECT
  USING (auth.uid() = id);
```

#### 2. `tasks`
```sql
CREATE TYPE task_status AS ENUM ('queued', 'in_progress', 'awaiting_review', 'completed', 'failed');
CREATE TYPE task_type AS ENUM ('presentation', 'report', 'email', 'research', 'analysis', 'automation', 'other');

CREATE TABLE tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  -- Basic info
  title TEXT NOT NULL,
  description TEXT,
  task_type task_type NOT NULL,
  domain_id UUID REFERENCES domains(id), -- which domain (ИНТЦ, bar, house, etc)
  
  -- Status & timing
  status task_status DEFAULT 'queued',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deadline TIMESTAMPTZ,
  
  -- Estimation
  time_estimated_seconds INT, -- estimated duration in seconds (e.g., 45 min = 2700)
  time_actual_seconds INT, -- actual duration after completion
  
  -- Context
  stakeholder_id UUID REFERENCES stakeholders(id), -- if applicable
  parent_task_id UUID REFERENCES tasks(id), -- for subtasks
  
  -- Execution
  started_at TIMESTAMPTZ,
  completed_at TIMESTAMPTZ,
  approved_at TIMESTAMPTZ, -- when Viktor said "готово"
  
  -- Quality metrics
  iterations_count INT DEFAULT 0, -- how many revisions
  quality_score FLOAT, -- 0.0 to 1.0
  
  -- Storage
  metadata JSONB DEFAULT '{}', -- {domain_specific_data}
  result_file_url TEXT, -- S3 URL to PPTX/XLSX/DOCX
  
  -- Autonomy
  can_execute_autonomous BOOLEAN DEFAULT FALSE, -- can system do this alone?
  
  CHECK (time_estimated_seconds > 0 OR time_estimated_seconds IS NULL),
  CHECK (time_actual_seconds > 0 OR time_actual_seconds IS NULL),
  CHECK (quality_score >= 0 AND quality_score <= 1 OR quality_score IS NULL)
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_deadline ON tasks(deadline);
CREATE INDEX idx_tasks_domain_id ON tasks(domain_id);

-- RLS
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their tasks"
  ON tasks FOR ALL
  USING (auth.uid() = user_id);
```

#### 3. `domains`
```sql
-- Dynamic domain/module system (ИНТЦ, Bootlegger, House, Education, etc)
CREATE TABLE domains (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  name TEXT NOT NULL, -- "ИНТЦ", "Bootlegger", "Дом"
  description TEXT,
  icon TEXT, -- emoji or icon name
  color_hex TEXT, -- "#0066FF" or similar
  
  is_active BOOLEAN DEFAULT TRUE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  metadata JSONB DEFAULT '{}' -- custom config per domain
);

CREATE INDEX idx_domains_user_id ON domains(user_id);

ALTER TABLE domains ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their domains"
  ON domains FOR ALL
  USING (auth.uid() = user_id);
```

#### 4. `stakeholders`
```sql
-- Profiles of people/entities (Трутнев, Чекунков, Фальков, УК, Фонд)
CREATE TABLE stakeholders (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  name TEXT NOT NULL, -- "Трутнев", "Чекунков"
  role TEXT, -- "Инвестор", "Партнер", "Государственный орган"
  email TEXT,
  phone TEXT,
  
  -- Learned preferences (auto-built from corrections)
  focus_areas TEXT[], -- array of strings: ["Инвестиции", "Продукты"]
  anti_focus TEXT[], -- what NOT to focus on
  visual_preferences JSONB, -- {background: "светлый", colors: [...]}
  tone_preference TEXT, -- "formal_corporate", "friendly", "technical"
  revision_pattern TEXT, -- how they usually revise
  
  -- Metrics
  interaction_count INT DEFAULT 0, -- how many tasks for this stakeholder
  avg_time_to_approval_seconds INT, -- average approval time
  confidence_score FLOAT DEFAULT 0.0, -- 0.0-1.0, how sure are we about preferences
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  
  metadata JSONB DEFAULT '{}' -- custom notes
);

CREATE INDEX idx_stakeholders_user_id ON stakeholders(user_id);

ALTER TABLE stakeholders ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their stakeholders"
  ON stakeholders FOR ALL
  USING (auth.uid() = user_id);
```

#### 5. `decisions`
```sql
-- Log of every correction/decision made (for learning)
CREATE TYPE decision_type AS ENUM ('content', 'visual', 'structure', 'tone', 'other');

CREATE TABLE decisions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  decision_type decision_type NOT NULL,
  
  -- What changed
  original_value TEXT,
  new_value TEXT,
  field_changed TEXT, -- which field was changed
  
  -- Why (captured from Viktor)
  reasoning TEXT, -- why did Viktor make this change?
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  
  metadata JSONB DEFAULT '{}' -- context-specific
);

CREATE INDEX idx_decisions_task_id ON decisions(task_id);
CREATE INDEX idx_decisions_user_id ON decisions(user_id);

ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their decisions"
  ON decisions FOR ALL
  USING (auth.uid() = user_id);
```

#### 6. `templates`
```sql
-- Reusable templates (presentations, email responses, report schemas)
CREATE TYPE template_category AS ENUM ('presentation', 'email', 'report', 'other');

CREATE TABLE templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  name TEXT NOT NULL,
  category template_category NOT NULL,
  description TEXT,
  
  -- Content
  content_markdown TEXT, -- base template in markdown
  content_structure JSONB, -- structured schema (slides, sections, etc)
  
  -- Associated data
  domain_id UUID REFERENCES domains(id),
  stakeholder_id UUID REFERENCES stakeholders(id), -- if template is for specific stakeholder
  
  tags TEXT[], -- ["ИНТЦ", "investor", "quarterly"]
  
  usage_count INT DEFAULT 0, -- how many times used
  effectiveness_score FLOAT, -- feedback score
  
  is_public BOOLEAN DEFAULT FALSE, -- can be shared (future)
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_templates_user_id ON templates(user_id);
CREATE INDEX idx_templates_category ON templates(category);

ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their templates"
  ON templates FOR ALL
  USING (auth.uid() = user_id);
```

#### 7. `skills`
```sql
-- Registry of installed skills (AI modules)
CREATE TABLE skills (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  name TEXT NOT NULL,
  version TEXT NOT NULL, -- "1.0.0"
  description TEXT,
  
  -- Installation
  source_type TEXT, -- "local", "github", "marketplace"
  source_url TEXT, -- path or GitHub URL
  
  -- Metadata
  triggers TEXT[], -- which task types trigger this skill
  dependencies TEXT[], -- other skills needed
  
  is_enabled BOOLEAN DEFAULT TRUE,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

Create INDEX idx_skills_user_id ON skills(user_id);

ALTER TABLE skills ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their skills"
  ON skills FOR ALL
  USING (auth.uid() = user_id);
```

#### 8. `mcps` (Model Context Providers)
```sql
-- Registry of external data connectors (Bitrix, FusionPOS, etc)
CREATE TABLE mcps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  name TEXT NOT NULL, -- "FusionPOS Connector", "Bitrix24"
  type TEXT NOT NULL, -- "data_source", "action", "notification"
  description TEXT,
  
  -- Configuration
  config JSONB NOT NULL, -- connection details (API key stored here, encrypted in production)
  status TEXT, -- "connected", "disconnected", "error"
  last_sync TIMESTAMPTZ,
  
  is_enabled BOOLEAN DEFAULT TRUE,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE mcps ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their MCPs"
  ON mcps FOR ALL
  USING (auth.uid() = user_id);
```

#### 9. `calendar_events`
```sql
-- Scheduled events/tasks on Viktor's calendar
CREATE TABLE calendar_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  title TEXT NOT NULL,
  description TEXT,
  
  start_time TIMESTAMPTZ NOT NULL,
  end_time TIMESTAMPTZ NOT NULL,
  
  task_id UUID REFERENCES tasks(id), -- link to task if applicable
  
  -- Metadata
  is_free_slot BOOLEAN DEFAULT FALSE, -- for autonomous task execution
  calendar_source TEXT, -- "google", "manual", "system"
  
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_calendar_events_user_id ON calendar_events(user_id);
CREATE INDEX idx_calendar_events_start_time ON calendar_events(start_time);

ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their events"
  ON calendar_events FOR ALL
  USING (auth.uid() = user_id);
```

#### 10. `learning_metrics`
```sql
-- Metrics for learning (LLM performance, time estimates, quality trends)
CREATE TABLE learning_metrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  metric_type TEXT NOT NULL, -- "llm_routing", "time_estimation", "stakeholder_profile"
  
  -- What we're measuring
  task_type TEXT, -- "presentation", "report", etc
  model_name TEXT, -- "claude-opus", "ollama-mistral"
  stakeholder_id UUID REFERENCES stakeholders(id),
  
  -- The measurements
  success_rate FLOAT, -- 0.0-1.0
  avg_duration_seconds INT,
  variance_seconds INT, -- standard deviation
  
  sample_size INT, -- how many data points
  
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_learning_metrics_user_id ON learning_metrics(user_id);

ALTER TABLE learning_metrics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their metrics"
  ON learning_metrics FOR ALL
  USING (auth.uid() = user_id);
```

#### 11. `llm_router_suggestions`
```sql
-- System-generated suggestions for LLM routing improvements
CREATE TABLE llm_router_suggestions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  
  suggestion TEXT, -- "Ollama-mistral handles classification perfectly, override routing?"
  
  from_model TEXT, -- current primary model
  to_model TEXT, -- suggested model
  task_type TEXT,
  
  confidence_score FLOAT,
  is_applied BOOLEAN DEFAULT FALSE,
  
  created_at TIMESTAMPTZ DEFAULT NOW(),
  applied_at TIMESTAMPTZ
);

ALTER TABLE llm_router_suggestions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can only access their suggestions"
  ON llm_router_suggestions FOR ALL
  USING (auth.uid() = user_id);
```

---

## API & Server Actions

### Architecture
- **Framework**: FastAPI (Python backend)
- **Endpoints**: RESTful + WebSocket for real-time
- **Authentication**: OAuth 2.0 with JWT, Supabase Auth
- **Request/Response**: JSON, strict schema validation via Pydantic
- **Error Handling**: Standard HTTP codes + structured error messages
- **Rate Limiting**: 100 req/min per user (configurable)

### Task Management Endpoints

#### POST `/api/tasks`
**Create a new task**

```typescript
// Request
POST /api/tasks
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "title": "Презентация резидентов для Трутнева",
  "description": "Подготовить презентацию для встречи с инвесторами",
  "task_type": "presentation", // enum: presentation | report | email | research | analysis
  "domain_id": "uuid-of-intc",
  "stakeholder_id": "uuid-of-trutnev", // optional
  "deadline": "2026-08-15T17:00:00Z",
  "metadata": {
    "presentation_type": "residents",
    "num_companies": 16,
    "target_audience": "investors"
  }
}

// Response (201 Created)
{
  "id": "task-uuid",
  "user_id": "user-uuid",
  "title": "Презентация резидентов для Трутнева",
  "status": "queued",
  "created_at": "2026-08-08T12:00:00Z",
  "time_estimated_seconds": 2700, // auto-calculated from history
  "confidence_score": 0.87
}

// Errors
- 400: Missing required fields, invalid enum
- 401: Not authenticated
- 403: No access to this domain
- 422: Validation error (Pydantic)
```

#### GET `/api/tasks`
**Fetch all tasks (with filtering)**

```typescript
GET /api/tasks?status=queued&domain_id=uuid&limit=20&offset=0
Authorization: Bearer <JWT>

// Response
{
  "tasks": [
    {
      "id": "task-uuid",
      "title": "...",
      "status": "queued",
      "deadline": "2026-08-15T17:00:00Z",
      "time_estimated_seconds": 2700,
      "time_actual_seconds": null,
      "stakeholder": { "id": "uuid", "name": "Трутнев", ... }
    }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

#### PATCH `/api/tasks/{task_id}`
**Update task status or metadata**

```typescript
PATCH /api/tasks/task-uuid
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "status": "awaiting_review", // enum transition
  "time_actual_seconds": 3120, // when task completed
  "quality_score": 0.95,
  "approved_at": "2026-08-08T14:30:00Z" // when Viktor approved
}

// Response (200 OK)
{
  "id": "task-uuid",
  "status": "completed",
  "completed_at": "2026-08-08T14:30:00Z",
  ...
}
```

#### POST `/api/tasks/{task_id}/decisions`
**Log a decision/correction**

```typescript
POST /api/tasks/task-uuid/decisions
Authorization: Bearer <JWT>
Content-Type: application/json

{
  "decision_type": "content",
  "field_changed": "slide_3_title",
  "original_value": "Компания X - Overview",
  "new_value": "Компания X - Инвестиционный фокус",
  "reasoning": "Трутнев не интересуется обзором, только инвестициями"
}

// Response (201 Created)
{
  "id": "decision-uuid",
  "task_id": "task-uuid",
  "decision_type": "content",
  "reasoning": "Трутнев не интересуется обзором, только инвестициями",
  "created_at": "2026-08-08T14:30:00Z"
}
```

### Stakeholder Endpoints

#### GET `/api/stakeholders/{stakeholder_id}`
**Get stakeholder profile (with learned preferences)**

```typescript
GET /api/stakeholders/uuid
Authorization: Bearer <JWT>

// Response
{
  "id": "uuid",
  "name": "Трутнев",
  "role": "Инвестор",
  "focus_areas": ["Инвестиции", "Продукты", "Выручка"],
  "anti_focus": ["Партнеры", "Экосистема"],
  "visual_preferences": {
    "background": "светлый",
    "images": "only emojis/icons, no photos",
    "layout": "minimalist"
  },
  "tone_preference": "formal_corporate",
  "interaction_count": 5,
  "avg_time_to_approval_seconds": 1800,
  "confidence_score": 0.95
}
```

### Template Endpoints

#### GET `/api/templates?category=email&stakeholder_id=uuid`
**Search templates**

```typescript
GET /api/templates?category=email&domain_id=uuid&tags=УК

// Response
{
  "templates": [
    {
      "id": "template-uuid",
      "name": "Письма УК - Подтверждение статуса",
      "category": "email",
      "content_markdown": "Уважаемый [name]! ...",
      "tags": ["УК", "formal"],
      "effectiveness_score": 0.98,
      "usage_count": 3
    }
  ]
}
```

### LLM Routing Endpoints

#### GET `/api/llm-router/suggestions`
**Get system suggestions for LLM routing improvements**

```typescript
GET /api/llm-router/suggestions?applied=false
Authorization: Bearer <JWT>

// Response
{
  "suggestions": [
    {
      "id": "suggestion-uuid",
      "suggestion": "Ollama-mistral successfully handles email classification. Consider setting as primary?",
      "from_model": "claude-sonnet",
      "to_model": "ollama-mistral",
      "task_type": "email",
      "confidence_score": 0.92,
      "is_applied": false
    }
  ]
}
```

#### POST `/api/llm-router/suggestions/{id}/apply`
**Apply LLM routing suggestion**

```typescript
POST /api/llm-router/suggestions/suggestion-uuid/apply
Authorization: Bearer <JWT>

// Response: Updates routing.yaml and records approval
{
  "is_applied": true,
  "applied_at": "2026-08-08T14:30:00Z"
}
```

### Real-time WebSocket

#### `/ws/tasks/{task_id}/updates`
**Subscribe to real-time task updates**

```typescript
// Connection
ws://localhost:8000/ws/tasks/task-uuid?token=<JWT>

// Messages (server → client)
{
  "event": "task_started",
  "data": { "task_id": "...", "started_at": "..." }
}

{
  "event": "task_progress",
  "data": { "status": "in_progress", "current_step": "content_verification" }
}

{
  "event": "task_completed",
  "data": { "status": "awaiting_review", "result_file_url": "..." }
}
```

### Error Response Format

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Field 'time_estimated_seconds' must be positive integer or null",
  "details": {
    "field": "time_estimated_seconds",
    "value": -100,
    "constraint": "positive"
  },
  "request_id": "req-12345", // for logging
  "timestamp": "2026-08-08T14:30:00Z"
}
```

---

## LLM Routing Configuration

### routing.yaml Structure

```yaml
version: 1.0

# Default settings
defaults:
  primary_model: claude-opus
  fallback_chain: [claude-sonnet, ollama-local]
  timeout_seconds: 60
  retry_attempts: 3

# Task-specific routing rules
routing_rules:
  # Presentations: Quality > Speed
  presentation:
    primary: claude-opus
    fallback: [claude-sonnet]
    reason: "Complex stakeholder preferences, needs creative synthesis"
    budget_aware: false
    confidence_threshold: 0.8
  
  # Reports: Balance
  report:
    primary: claude-opus
    fallback: [claude-sonnet]
    reason: "Data accuracy important, some creativity needed"
    budget_aware: true
  
  # Emails: Use local if confident, fallback to Claude
  email:
    primary: claude-sonnet
    observer: ollama-mistral # Learn from this interaction
    fallback: [claude-opus]
    reason: "Sonnet handles tone modulation well, Ollama learns style"
    confidence_threshold: 0.85
  
  # Simple classification: Local first
  task_classification:
    primary: ollama-local
    fallback: [claude-sonnet]
    reason: "Fast, deterministic, no need for Opus"
    confidence_threshold: 0.7
  
  # Data analysis: Accuracy critical
  data_analysis:
    primary: claude-opus
    fallback: false # No fallback for critical data tasks
    reason: "Number accuracy non-negotiable"
  
  # Research: Needs reasoning
  research:
    primary: claude-opus
    fallback: [claude-sonnet]
    reason: "Needs deep reasoning"

# Hybrid learning mode
hybrid_mode:
  enabled: true
  observer_models: [ollama-local, ollama-mistral]
  sync_interval_tasks: 10 # Check every 10 tasks
  suggest_override_threshold: 0.95 # If observer > 95%, suggest override

# Model-specific config
models:
  claude-opus:
    api_provider: anthropic
    cost_per_1k_tokens: 0.015
    speed_tier: slow
    reasoning_quality: excellent
    supports_web_search: true
    context_window: 200000
    estimated_latency_ms: 2000
  
  claude-sonnet:
    api_provider: anthropic
    cost_per_1k_tokens: 0.003
    speed_tier: medium
    reasoning_quality: good
    supports_web_search: true
    context_window: 200000
    estimated_latency_ms: 1200
  
  ollama-local:
    api_provider: local
    cost_per_1k_tokens: 0.0
    speed_tier: very-fast
    reasoning_quality: medium
    supports_web_search: false
    context_window: 8192 # For Mistral 7B
    estimated_latency_ms: 500
    
    # Available local models
    available_models:
      - name: mistral:7b
        context_window: 32768
        reasoning: medium
      - name: neural-chat:7b
        context_window: 8192
        reasoning: medium

# Fallback behavior
fallback_behavior:
  max_retries: 3
  retry_delay_seconds: 2
  backoff_strategy: exponential # linear | exponential
  notify_on_fallback: true # Alert user if used fallback

# Cost tracking
cost_tracking:
  enabled: true
  monthly_budget_dollars: 100
  alert_threshold_percent: 80
  log_to_db: true
```

---

## Business Logic & Workflows

### Workflow 1: Presentation Generation (Interactive)

```
STATE MACHINE:

[QUEUED]
  ↓ (Intent recognized: presentation)
  
[ANALYZE]
  - Router identifies: presentation task
  - Context pulls: stakeholder profile, past presentations
  - System suggests: "Это для Трутнева как обычно?"
  ↓
  
[CONTEXT_ASSEMBLY]
  - Fetch residents data from ИНТЦ knowledge base
  - Fetch stakeholder preferences
  - Query templates for similar presentations
  ↓
  
[CONTENT_VERIFICATION] (Interactive)
  - System shows: "Вот что нашел: Компания X, Product Y, Investment $Z"
  - Viktor verifies: "Правильно, но Investment $Z1"
  - System updates context with verified data
  ↓
  
[STRUCTURE_APPROVAL] (Interactive)
  - System proposes: "4 компании на слайде (как для Трутнева)"
  - Viktor approves or suggests changes
  ↓
  
[MOCKUP_GENERATION]
  - LLM generates slide layouts (no data yet)
  - Apply visual preferences (светлый фон, эмодзи)
  - Show preview
  ↓
  
[MOCKUP_APPROVAL] (Interactive)
  - Viktor reviews, provides corrections
  - System updates mockup
  ↓
  
[DATA_FILLING]
  - Insert verified data into mockup
  - Generate PPTX file
  - Save to S3
  ↓
  
[FINAL_REVIEW] (Interactive)
  - Viktor reviews final PPTX
  - Makes any final corrections (iterate back to MOCKUP_GENERATION if needed)
  ↓
  
[AWAITING_COMPLETION]
  - Viktor says "Готово!"
  ↓
  
[COMPLETED]
  - Save all metadata:
    {
      task_status: "completed",
      result_file_url: "s3://...",
      time_actual: 3120,
      iterations_count: 2,
      quality_score: 0.95
    }
  - Log decisions: what changed and why
  - Update stakeholder profile with learnings
  - Calculate time estimate confidence
  ↓
  
[LEARNING]
  - Trутнев profile confidence += 0.05
  - Template usage_count += 1
  - Decision log recorded
```

### Workflow 2: Autonomous Report (Background)

```
TRIGGER: Schedule (e.g., Every Monday 8:00 AM)

[SCHEDULED_EXECUTION]
  - Time: Monday 8:00 AM (from Viktor's timezone)
  - Task: Weekly bar report
  ↓
  
[DATA_FETCH]
  - FusionPOS API → fetch sales, expenses, inventory
  - Handle errors: if API down, skip and notify
  ↓
  
[ANALYSIS]
  - Claude (or Ollama) analyzes data
  - Calculates: ABC analysis, trends, variances
  - Generates insights
  ↓
  
[VISUALIZATION]
  - Recharts: Revenue chart, product breakdown, daily comparison
  - Markdown summary
  ↓
  
[REPORT_GENERATION]
  - Creates XLSX with raw data + formulas
  - Markdown summary
  - Dashboard URL (if using Supabase)
  ↓
  
[DELIVERY]
  - Saves to vault/bar/weekly_reports/
  - Sends Telegram notification: "Weekly report ready: [link]"
  - Sends Desktop notification
  ↓
  
[LOGGING]
  - Record task: time taken, data freshness, any errors
  - Store metrics for future estimates
```

### Validation & Safety Checks

```
BEFORE EXECUTION:
1. Verify data exists and is fresh
2. Check for required fields
3. Validate stakeholder profile (if applicable)
4. Check calendar for conflicts
5. Ensure sufficient context available

DURING EXECUTION:
1. Rate limit API calls (e.g., FusionPOS: 100 req/min)
2. Timeout protection (e.g., 60 sec max per LLM call)
3. Logging all decisions and model outputs
4. Graceful error handling

BEFORE COMPLETION:
1. Quality Assurance checks (based on stakeholder history)
   "For Трутнев: verify инвестиции numbers, colors, slide structure"
2. Data validation (all numbers reasonable)
3. File integrity check (PPTX/XLSX not corrupted)

AFTER COMPLETION:
1. Save all metadata
2. Update learning metrics
3. Suggest improvements if accuracy < threshold
```

---

## User Stories & Features

### Story 1: "Fast Presentation Creation"
**As** Viktor  
**I want** to create a presentation for a known stakeholder in minimal time  
**So that** I can focus on strategy, not busywork

**Acceptance Criteria:**
- [ ] System auto-fills stakeholder preferences (< 1 second)
- [ ] Content verification step completes in < 2 minutes
- [ ] Mockup generation happens async (< 30 seconds)
- [ ] First iteration approval rate > 80% (Viktor approves without changes)

### Story 2: "Learn from Corrections"
**As** Jarvis OS  
**I want** to understand WHY Viktor makes corrections  
**So that** I improve future deliverables

**Acceptance Criteria:**
- [ ] For every correction, ask "Why?" (interactive prompt)
- [ ] Store reasoning in decisions table
- [ ] Use reasoning to update stakeholder profiles
- [ ] After 5 interactions, confidence score > 0.8

### Story 3: "Autonomous Weekly Reports"
**As** Viktor  
**I want** the system to generate weekly bar reports automatically  
**So that** I don't have to remind it or manually pull data

**Acceptance Criteria:**
- [ ] Report generated every Monday 8:00 AM
- [ ] FusionPOS data is current (< 1 hour old)
- [ ] Report includes: revenue, expenses, ABC analysis, trends
- [ ] Telegram notification sent when ready
- [ ] Error notifications if data unavailable

### Story 4: "Intelligent Task Scheduling"
**As** Viktor  
**I want** the system to suggest when to work on tasks  
**So that** I maximize productive hours

**Acceptance Criteria:**
- [ ] System shows calendar with free slots
- [ ] For each task: estimated time + complexity
- [ ] Suggests optimal ordering (deadline + complexity)
- [ ] Alerts if impossible deadlines detected
- [ ] Auto-schedules autonomous tasks in free slots

### Story 5: "Multi-Interface Access"
**As** Viktor  
**I want** to interact with Jarvis via web, Telegram, or voice  
**So that** I can manage tasks from anywhere

**Acceptance Criteria (MVP):**
- [ ] Web UI: full control, visualizations, settings
- [ ] Telegram: quick text + file upload, async updates
- [ ] Voice: later (Phase 3+)
- [ ] Desktop ↔ Telegram sync in real-time

---

## UI/UX Экраны (Wireframes)

### Design System
```
Color Palette:
- Background: Pure Black (#000000)
- Accent: Cyberpunk Blue (#0066FF)
- Light Blue: (#00D9FF) for highlights
- Text Primary: Light Gray (#F0F0F0)
- Text Secondary: Medium Gray (#A0A0A0)
- Success: Green (#00CC00)
- Warning: Orange (#FF9900)
- Error: Red (#FF3366)

Typography:
- Headlines: Geist or Inter Bold, 24px-32px
- Body: Inter Regular, 14px-16px
- Monospace: JetBrains Mono, 12px (for data/timestamps)
- Line height: 1.6 for readability

Grid: 8pt (all spacing/sizing)
Animations: Framer Motion spring (damping: 15, stiffness: 300)
Contrast: WCAG AA minimum (#000000 on light backgrounds)
```

### Screen 1: Dashboard (Home)

```
┌─────────────────────────────────────────────────────────────┐
│ JARVIS OS                         [Settings] [Help] [Logout] │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│ DOMAINS      │  DASHBOARD                                  │
│              │  ├─ Quick Stats (widgets)                   │
│ [ИНТЦ]       │  │  ├─ Tasks This Week: 8                   │
│ [Bootlegger] │  │  ├─ Completed: 6                         │
│ [Дом]        │  │  └─ Avg Quality: 0.92                    │
│              │  │                                          │
│ + Add        │  ├─ Burndown Chart (Recharts)               │
│              │  │  [line graph: tasks completed over time]│
│              │  │                                          │
│              │  ├─ Tasks Today                              │
│              │  │  ┌─────────────────────────────────────┐│
│              │  │  │ ☐ Презентация Трутнева              ││
│              │  │  │   Domain: ИНТЦ | Deadline: 5h left  ││
│              │  │  │   Status: Awaiting review            ││
│              │  │  │   [View] [Approve] [Correct]         ││
│              │  │  └─────────────────────────────────────┘│
│              │  │                                          │
│              │  │  ┌─────────────────────────────────────┐│
│              │  │  │ ☐ Weekly Bar Report (Auto)          ││
│              │  │  │   Domain: Bootlegger | Scheduled... ││
│              │  │  │   Status: In progress (7:00 AM)     ││
│              │  │  │   [Details]                          ││
│              │  │  └─────────────────────────────────────┘│
│              │  │                                          │
│              │  └─ Recent Actions                           │
│              │     • Completed: Email to УК (12:30 PM)    │
│              │     • Updated: Трутнев profile (10:15 AM)  │
│              │                                          │
└──────────────┴──────────────────────────────────────────────┘

Interactions:
- Click domain → filter tasks by domain
- Click [Quick Start] button → new task modal
- Click task card → open task details
```

### Screen 2: Task Chat (Interactive Creation)

```
┌─────────────────────────────────────────────────────────────┐
│ New Task: Presentation                                   [x] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ System: Доброе утро! Начинаю собирать материалы...          │
│                                                              │
│ System: Это для Трутнева как в прошлый раз?                │
│         [Да] [Нет] [Кого-то еще]                            │
│                                                              │
│ Viktor: [Да]                                                 │
│                                                              │
│ System: Отлично. Я сейчас соберу данные. Вот что нашел:    │
│         • Компания X: Product Y, Investment $50M             │
│         • Компания A: Product B, Investment $20M             │
│         [...]                                                │
│                                                              │
│         Данные верны? Какие-то исправления?                │
│                                                              │
│ Viktor: Компания X: Investment $75M (не 50)                │
│                                                              │
│ System: Обновил. Дальше:                                    │
│         Структура (как для Трутнева):                       │
│         • Слайд 1: Титульный лист                           │
│         • Слайды 2-17: 4 компании на слайде (всего 16)     │
│         • Слайд 18: Будущее ИНТЦ                            │
│                                                              │
│         Одобряешь? [Да] [Правка]                            │
│                                                              │
│ Viktor: [Да]                                                 │
│                                                              │
│ System: Создаю мокап...                                     │
│         [Loading spinner]                                    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ [Type message...] [📎 Attach] [🎤 Voice] [Send ↵]          │
└─────────────────────────────────────────────────────────────┘

Real-time updates: Task progresses as conversation flows
```

### Screen 3: Task Details & Approval

```
┌─────────────────────────────────────────────────────────────┐
│ Task: Презентация резидентов ИНТЦ              [Close]      │
├──────────────────────────┬──────────────────────────────────┤
│ METADATA                 │ INTERACTIVE VIEW                 │
│                          │                                  │
│ Domain: ИНТЦ             │ Current Step: Mockup Review      │
│ Type: Presentation       │                                  │
│ Stakeholder: Трутнев     │ Mockup Preview:                  │
│ Deadline: 2h 15m left    │ [Slide 1] [Slide 2] [Slide 3]   │
│                          │                                  │
│ Status: Awaiting Review  │ Slide 3 (Sample):               │
│ Created: 08:30 AM        │ ┌────────────────────────────┐  │
│ Est. Time: 45 min        │ │ Компания X                 │  │
│ Actual Time: 52 min      │ │ Product: Y                 │  │
│ Iterations: 2            │ │ Investment: $75M           │  │
│ Quality: 0.95            │ │                            │  │
│                          │ │ [✓] Logo present           │  │
│ Decisions:               │ │ [✓] Colors match brand     │  │
│ • Слайд 3: убрал парт… │ │ [!] Layout could tighten   │  │
│   "Трутнев не интереса…"│ │                            │  │
│                          │ └────────────────────────────┘  │
│ Result File:             │                                  │
│ presentation_final.pptx  │ Quality Assurance:               │
│ [Download]               │ ☐ Numbers verified               │
│                          │ ☐ Colors match brand             │
│                          │ ☐ Logos present                  │
│                          │ ☐ Structure clear                │
│                          │                                  │
│                          │ Feedback (optional):             │
│                          │ [Text area for corrections]      │
│                          │                                  │
│                          │ [Approve] [Correct] [Reject]     │
│                          │                                  │
└──────────────────────────┴──────────────────────────────────┘
```

### Screen 4: Calendar & Scheduling

```
┌─────────────────────────────────────────────────────────────┐
│ Calendar                                            [< Aug >] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Mon 08    Tue 09    Wed 10    Thu 11    Fri 12    Sat 13   │
│                                                              │
│ 08:00 AM  Free      Free      Free      Free      Free     │
│           (slot)    (slot)    (slot)    (slot)             │
│                                                              │
│ 09:00 AM  Email to  Free      Free      Meeting   Free     │
│           УК (30m)  (slot)    (slot)    Чекунков          │
│           [Auto]                        (1h)               │
│                                                              │
│ 10:00 AM  Free      Free      Free      Free      Free     │
│           (slot)    (slot)    (slot)    (slot)             │
│                                                              │
│ 11:00 AM  Presenta- Free      Presenta- Free      Free     │
│           tion prep (slot)    tion prep (slot)             │
│           Трутнев           Фалькова                        │
│           (est. 45m)        (est. 60m)                      │
│                                                              │
│ 12:00 PM  [Continue...]                                    │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ Pending Tasks (Auto-schedule?)                              │
│                                                              │
│ □ Weekly Bar Report (Bootlegger)                            │
│   Autonomy: YES | Est. Time: 30m | Ideal: Monday 8:00 AM   │
│   [Schedule Auto] [Manual]                                  │
│                                                              │
│ □ Market Research (ИНТЦ)                                    │
│   Autonomy: NO (needs Viktor input) | Est. Time: 2h         │
│   Suggested slots: Wed 2-4 PM, Thu 3-5 PM                  │
│   [Schedule]                                                │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Screen 5: 3D Graph Visualization

```
(3D node graph rendering with Three.js)

Nodes:
- Blue circles: Tasks (color: domain)
- Green circles: Stakeholders
- Yellow squares: Templates
- Red stars: Decisions/corrections
- Gray nodes: Knowledge base

Interactions:
- Rotate: Mouse drag
- Zoom: Scroll
- Click node: Show details in sidebar
- Search: Filter nodes, highlight paths
- Zoom to cluster: Double-click domain node

Example view:
- Center: Трутнев node (green)
- Connected to: 5 presentations (blue)
- Each presentation connected to: Templates (yellow), Decisions (red)
- Time-based coloring: Recent (bright), Old (dim)
- Edge thickness: Frequency of interaction

Sidebar:
┌──────────────────┐
│ Selected: Трутнев│
│                  │
│ Role: Инвестор   │
│ Interactions: 5  │
│ Confidence: 0.95 │
│                  │
│ Preferences:     │
│ • Инвестиции    │
│ • Продукты       │
│ • Светлый фон    │
│                  │
│ Recent Tasks:    │
│ • Presentation.. │
│ • Email to...    │
│                  │
│ [Details]        │
└──────────────────┘
```

### Screen 6: Plugin Manager

```
┌─────────────────────────────────────────────────────────────┐
│ Plugin Manager                                   [+ Add]     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ [Search plugins...] [Filter: All] [Installed] [Available]   │
│                                                              │
│ SKILLS (12 installed)                                        │
│                                                              │
│ ┌─ Market Research Pro                          [v1.0] [✓] ┐
│ │  Description: Conducts market analysis                   │
│ │  Dependencies: web_search, analysis                      │
│ │  Last used: 2 hours ago                                  │
│ │  Success rate: 94%                                       │
│ │  [⚙️ Config] [🗑️ Uninstall] [⬇️ Download]               │
│ └────────────────────────────────────────────────────────┘
│
│ ┌─ Email Generator                              [v1.0] [✓] ┐
│ │  ...                                                     │
│ └────────────────────────────────────────────────────────┘
│
│ MCPs (8 installed)                                           │
│
│ ┌─ FusionPOS Connector                          [v1.0] [✓] ┐
│ │  Endpoints: 15 | Last sync: 5 min ago                    │
│ │  Rate limit: 100/min | Status: Connected                │
│ │  [⚙️ Config API Key] [Test] [🗑️ Remove]                 │
│ └────────────────────────────────────────────────────────┘
│
│ ADD NEW PLUGIN                                               │
│                                                              │
│ [📁 Local ZIP] [🔗 GitHub URL] [Browse Marketplace]         │
│                                                              │
│ Validation (for file upload):                                │
│ ✓ Manifest found                                             │
│ ✓ Dependencies available                                    │
│ ✓ No conflicts                                              │
│                                                              │
│ [INSTALL]                                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Security & RLS Policies

### Row Level Security (RLS) Strategy

**Principle**: Every table must enforce `auth.uid() = user_id` except for system tables

```sql
-- Generic RLS Policy Pattern
ALTER TABLE table_name ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can only access their own data"
  ON table_name
  FOR ALL
  USING (auth.uid() = user_id);

-- For tables without user_id (rare)
-- Example: shared templates (future)
CREATE POLICY "Users can read public templates or their own"
  ON templates
  FOR SELECT
  USING (
    is_public = true 
    OR auth.uid() = user_id
  );

-- For update/delete (more restrictive)
CREATE POLICY "Users can only modify their own data"
  ON tasks
  FOR UPDATE
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);
```

### Input Validation (Pydantic)

```python
# Example: Task creation schema
from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum
from datetime import datetime

class TaskTypeEnum(str, Enum):
    PRESENTATION = "presentation"
    REPORT = "report"
    EMAIL = "email"
    RESEARCH = "research"
    ANALYSIS = "analysis"

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=500)
    description: Optional[str] = Field(None, max_length=2000)
    task_type: TaskTypeEnum
    domain_id: Optional[str] = None # UUID
    stakeholder_id: Optional[str] = None
    deadline: Optional[datetime] = None
    metadata: Optional[dict] = Field(default_factory=dict)
    
    @validator('deadline')
    def deadline_in_future(cls, v):
        if v and v < datetime.utcnow():
            raise ValueError('Deadline must be in the future')
        return v
    
    @validator('metadata')
    def metadata_not_too_large(cls, v):
        import json
        if len(json.dumps(v)) > 10000: # 10KB limit
            raise ValueError('Metadata too large')
        return v
```

### API Rate Limiting

```python
# Using slowapi (rate limiting middleware)
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/api/tasks")
@limiter.limit("100/minute")
async def get_tasks(request: Request, ...):
    pass

# Rate limits:
# - General: 100 req/min per user
# - Create task: 10 req/min per user
# - LLM calls: 50 req/hour per user (throttles expensive operations)
# - File uploads: 50 MB/hour per user
```

### Secret Management

```python
# .env file structure (never commit)
ANTHROPIC_API_KEY=sk-xxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxx
OLLAMA_BASE_URL=http://localhost:11434
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=xxxxx
BITRIX24_WEBHOOK_URL=https://...
TELEGRAM_BOT_TOKEN=xxxxxx:xxxxx
DATABASE_URL=postgresql://user:pass@localhost/jarvis
REDIS_URL=redis://localhost:6379

# Load via python-dotenv
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
```

### Data Encryption (At Rest)

```sql
-- Sensitive fields: encrypt in PostgreSQL
ALTER TABLE mcps ADD COLUMN config_encrypted TEXT;

-- Store raw API keys encrypted via pgcrypto extension
INSERT INTO mcps (name, config_encrypted)
VALUES ('FusionPOS', PGP_SYM_ENCRYPT('{"api_key": "xxx"}', 'secret_key'));

-- Decrypt on retrieval (only in backend)
SELECT PGP_SYM_DECRYPT(config_encrypted, 'secret_key');
```

---

## Error Handling & Edge Cases

### Common Error Scenarios

| Scenario | HTTP Code | Response | Mitigation |
|----------|-----------|----------|-----------|
| User not authenticated | 401 | `{error: "UNAUTHENTICATED"}` | Redirect to login |
| User lacks permissions | 403 | `{error: "FORBIDDEN"}` | Show "Access denied" |
| Invalid task ID format | 400 | `{error: "INVALID_ID"}` | Client-side validation |
| Task deadline in past | 422 | `{error: "INVALID_DEADLINE"}` | Validator rejects |
| FusionPOS API offline | 503 | `{error: "SERVICE_UNAVAILABLE"}` | Use cached data, notify user |
| Obsidian sync conflict | 409 | `{error: "CONFLICT"}` | Show merge UI |
| File too large (> 50MB) | 413 | `{error: "PAYLOAD_TOO_LARGE"}` | Client split upload |
| Rate limit exceeded | 429 | `{error: "TOO_MANY_REQUESTS"}` | Exponential backoff |
| LLM timeout (>60s) | 504 | `{error: "TIMEOUT"}` | Use fallback model |

### Offline Mode

```javascript
// Frontend: LocalStorage fallback
if (navigator.onLine) {
  // Sync with server
  await fetch('/api/tasks', { method: 'POST', body })
} else {
  // Save to localStorage
  localStorage.setItem(`task_draft_${uuid}`, JSON.stringify(task))
  showNotification("Saved offline. Will sync when online.")
}

// OnLine event: sync all drafts
window.addEventListener('online', async () => {
  const drafts = Object.keys(localStorage)
    .filter(k => k.startsWith('task_draft_'))
  for (const draft of drafts) {
    await syncDraft(draft)
  }
})
```

### Empty States

```
When no tasks exist:
┌─────────────────────────────────┐
│                                 │
│  📋 No tasks yet                │
│                                 │
│  Create your first task to      │
│  get started                    │
│                                 │
│  [+ New Task]                   │
│  [Learn more]                   │
│                                 │
└─────────────────────────────────┘
```

---

## Testing Strategy

### Unit Tests (Python backend)

```python
# test_llm_router.py
import pytest
from jarvis.llm_router import route_task

def test_email_routes_to_claude_sonnet():
    """Email tasks should route to claude-sonnet"""
    task = {"type": "email", "title": "Reply to УК"}
    model = route_task(task)
    assert model == "claude-sonnet"

def test_fallback_chain():
    """If primary fails, try fallback"""
    with patch('anthropic.Anthropic.messages.create', side_effect=Exception):
        result = route_task({"type": "email"}, use_fallback=True)
        # Should fall back to ollama-mistral
        assert result is not None

def test_confidence_threshold():
    """Ollama must exceed confidence threshold"""
    task = {"type": "classification"}
    model = route_task(task)
    # Should use ollama if confidence > 0.85
    assert model in ["ollama-local", "claude-sonnet"]

@pytest.mark.asyncio
async def test_task_creation_stores_metadata():
    """Creating a task should persist all metadata"""
    task = await create_task(
        user_id="uuid",
        title="Test",
        task_type="presentation",
        metadata={"key": "value"}
    )
    assert task.metadata["key"] == "value"
    assert task.created_at is not None
```

### Integration Tests (API)

```python
# test_api_tasks.py
@pytest.mark.asyncio
async def test_create_task_end_to_end(client, db):
    """Full flow: create task → get task → update status"""
    # Create
    response = await client.post(
        "/api/tasks",
        json={"title": "Test", "task_type": "presentation"}
    )
    assert response.status_code == 201
    task_id = response.json()["id"]
    
    # Get
    response = await client.get(f"/api/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "queued"
    
    # Update
    response = await client.patch(
        f"/api/tasks/{task_id}",
        json={"status": "completed"}
    )
    assert response.status_code == 200
    assert response.json()["completed_at"] is not None
```

### E2E Tests (Playwright)

```python
# test_presentation_workflow.py
async def test_presentation_creation_workflow():
    """User creates presentation from start to approval"""
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        
        # Navigate
        await page.goto("http://localhost:3000")
        
        # Click "New Task"
        await page.click("[data-testid='btn-new-task']")
        
        # Type task
        await page.fill(
            "[data-testid='input-title']",
            "Презентация резидентов"
        )
        
        # Select task type
        await page.click("[data-testid='select-type']")
        await page.click("text=Presentation")
        
        # Wait for interactive chat to appear
        await page.wait_for_selector("[data-testid='chat-container']")
        
        # System should ask confirmation
        assert await page.text_content("text=Это для Трутнева")
        
        # Click "Да"
        await page.click("text=Да")
        
        # Wait for mockup
        await page.wait_for_timeout(3000)
        
        # System should show preview
        assert await page.text_content("text=Mockup готов")
        
        # Approve
        await page.click("[data-testid='btn-approve']")
        
        # Verify completion
        assert await page.text_content("text=Completed")
        
        await browser.close()
```

---

## Deployment & Infrastructure

### Docker Setup

```dockerfile
# Dockerfile (backend)
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Run
CMD ["uvicorn", "jarvis.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://user:pass@postgres:5432/jarvis
      REDIS_URL: redis://redis:6379
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis
  
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: jarvis
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    ports:
      - "6379:6379"
  
  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    environment:
      MODEL: mistral:7b

volumes:
  postgres_data:
```

### CI/CD (GitHub Actions)

```yaml
name: CI/CD

on:
  push:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest
      
      - name: Lint
        run: black --check . && flake8
  
  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v3
      - uses: docker/build-push-action@v4
        with:
          push: true
          tags: ghcr.io/viktor/jarvis-os:latest
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
  
  deploy:
    runs-on: ubuntu-latest
    needs: build
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # SSH to server, pull latest, restart
          ssh root@production "cd /app && docker-compose pull && docker-compose up -d"
```

---

**END OF SPECIFICATION**

**Status**: Ready for Phase 0 Implementation  
**Owner**: Viktor  
**Last Updated**: 2026-08-08  
**Next**: Share with development team, initialize repository
