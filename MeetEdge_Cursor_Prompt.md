# MeetEdge — Master Cursor AI Prompt
**Project:** MeetEdge | **Company:** Secure Edge Pvt Ltd | **Author:** Kumar Martand  
**Stack:** FastAPI · PostgreSQL · Redis · Celery · Next.js 14 · Tailwind CSS · Google Calendar API

---

> **HOW TO USE THIS PROMPT IN CURSOR**
> Open Cursor → press `Cmd+L` to open AI chat → paste this entire prompt.
> Cursor will read your project files automatically since it has full codebase context.
> Let it run. If it stops, type **"continue"** — do not modify anything manually until it finishes all phases.

---

## SYSTEM CONTEXT

You are an expert senior full-stack engineer building **MeetEdge**, an AI-powered meeting intelligence platform for Secure Edge Pvt Ltd. The project scaffold already exists with stub files in place. Your job is to implement every single file completely — no placeholders, no `# TODO`, no `pass` statements, no `raise NotImplementedError`. Every function must be fully working code.

**You have full autonomy.** Do not ask clarifying questions. Make the best engineering decision and implement it. Work through all phases sequentially. Do not skip any file. Do not summarize what you're about to do — just do it.

---

## PROJECT STRUCTURE (already exists — implement every file)

```
meetedge/
├── docker-compose.yml              ✅ already written
├── .gitignore                      ✅ already written
├── README.md                       ✅ already written
├── scripts/
│   ├── google_auth.py              🔧 implement
│   └── seed_db.py                  🔧 implement
├── backend/
│   ├── requirements.txt            ✅ already written
│   ├── .env.example                ✅ already written
│   ├── alembic.ini                 ✅ already written
│   ├── alembic/
│   │   ├── env.py                  ✅ already written
│   │   ├── script.py.mako          ✅ already written
│   │   └── versions/               🔧 generate first migration
│   ├── app/
│   │   ├── main.py                 ✅ already written
│   │   ├── core/
│   │   │   ├── config.py           ✅ already written
│   │   │   ├── database.py         ✅ already written
│   │   │   ├── deps.py             ✅ already written
│   │   │   ├── logging.py          ✅ already written
│   │   │   └── security.py         🔧 implement
│   │   ├── models/
│   │   │   ├── meeting.py          ✅ already written
│   │   │   ├── attendee.py         ✅ already written
│   │   │   ├── action_item.py      ✅ already written
│   │   │   └── tenant.py           🔧 implement
│   │   ├── schemas/
│   │   │   ├── meeting.py          ✅ already written
│   │   │   ├── attendee.py         ✅ already written
│   │   │   └── action_item.py      ✅ already written
│   │   ├── api/
│   │   │   ├── router.py           ✅ already written
│   │   │   └── routes/
│   │   │       ├── health.py       ✅ already written
│   │   │       ├── meetings.py     🔧 implement fully
│   │   │       ├── calendar.py     🔧 implement fully
│   │   │       └── action_items.py 🔧 implement fully
│   │   ├── services/
│   │   │   ├── calendar_service.py 🔧 implement fully
│   │   │   ├── meeting_service.py  🔧 implement fully
│   │   │   └── notification_service.py 🔧 implement fully
│   │   ├── tasks/
│   │   │   ├── celery_app.py       ✅ already written
│   │   │   ├── calendar_tasks.py   🔧 implement fully
│   │   │   └── notification_tasks.py 🔧 implement fully
│   │   └── utils/
│   │       ├── datetime_utils.py   🔧 implement fully
│   │       └── google_auth.py      🔧 implement fully
│   └── tests/
│       ├── conftest.py             🔧 implement fully
│       ├── test_meetings.py        🔧 implement fully
│       └── test_calendar.py        🔧 implement fully
└── frontend/
    ├── package.json                ✅ already written
    ├── next.config.ts              🔧 implement
    ├── tailwind.config.ts          🔧 implement
    ├── tsconfig.json               🔧 implement
    └── src/
        ├── app/
        │   ├── layout.tsx          🔧 implement
        │   ├── page.tsx            🔧 implement (redirect to dashboard)
        │   ├── globals.css         🔧 implement
        │   ├── dashboard/page.tsx  🔧 implement fully
        │   ├── meetings/
        │   │   ├── page.tsx        🔧 implement fully
        │   │   └── [id]/page.tsx   🔧 implement fully
        │   ├── chat/page.tsx       🔧 implement fully
        │   ├── action-items/page.tsx 🔧 implement fully
        │   └── login/page.tsx      🔧 implement fully
        ├── components/
        │   ├── layout/
        │   │   ├── Sidebar.tsx     🔧 implement fully
        │   │   └── Header.tsx      🔧 implement fully
        │   ├── meetings/
        │   │   ├── MeetingCard.tsx       🔧 implement fully
        │   │   ├── MeetingList.tsx       🔧 implement fully
        │   │   ├── TranscriptViewer.tsx  🔧 implement fully
        │   │   └── SummaryPanel.tsx      🔧 implement fully
        │   └── chat/
        │       └── ChatInterface.tsx     🔧 implement fully
        ├── hooks/
        │   ├── useMeetings.ts      🔧 implement fully
        │   └── useChat.ts          🔧 implement fully
        ├── lib/
        │   ├── api.ts              ✅ already written
        │   └── utils.ts            🔧 implement
        └── types/
            ├── meeting.ts          ✅ already written
            └── api.ts              ✅ already written
```

---

## PHASE 1 — BACKEND CORE (implement in this exact order)

### 1.1 — `backend/app/core/security.py`
Implement full JWT authentication:
- `create_access_token(data: dict, expires_delta: timedelta)` — creates RS256 JWT
- `create_refresh_token(data: dict)` — longer-lived refresh token
- `verify_token(token: str)` — decode and validate JWT, raise HTTPException 401 if invalid
- `get_password_hash(password: str)` — bcrypt hash
- `verify_password(plain: str, hashed: str)` — bcrypt verify
- Use `python-jose` for JWT, `passlib[bcrypt]` for passwords
- Read `SECRET_KEY` from `settings`
- Token expiry: access = 60 min, refresh = 7 days

### 1.2 — `backend/app/models/tenant.py`
Implement `Tenant` SQLAlchemy model:
- Fields: `id` (UUID PK), `name` (String 255), `slug` (String 100, unique), `google_credentials_encrypted` (Text, nullable), `notification_channels` (JSONB, default `{}`), `retention_days` (Integer, default 365), `is_active` (Boolean, default True), `created_at`, `updated_at`
- Import `Base` from `app.core.database`

### 1.3 — `backend/app/utils/datetime_utils.py`
Implement:
- `utcnow()` → aware datetime
- `parse_google_datetime(dt_str: str)` → parse ISO 8601 strings from Google API including `Z` suffix and date-only strings
- `minutes_until(dt: datetime)` → float minutes from now until given datetime
- `is_within_minutes(dt: datetime, minutes: int)` → bool, true if dt is between now and now+minutes
- `format_duration(start: datetime, end: datetime)` → human string like "1h 23m"

---

## PHASE 2 — SERVICES (implement fully, no stubs)

### 2.1 — `backend/app/services/calendar_service.py`
Fully implement the `CalendarService` class:

```
class CalendarService:
    __init__(self, db: AsyncSession = None)
    _get_credentials(self) → Credentials | None
    check_auth(self) → bool
    _get_service(self) → googleapiclient Resource
    fetch_upcoming_events(self, hours_ahead: int = None) → List[dict]
    _extract_meet_url(self, event: dict) → str | None
    sync_upcoming_meetings(self) → dict   # returns {"synced": N, "skipped": M}
    _upsert_meeting(self, event: dict, db: AsyncSession) → Meeting
    _upsert_attendees(self, meeting: Meeting, attendees: list, db: AsyncSession)
```

- `fetch_upcoming_events`: call Google Calendar API `events().list()`, filter only events with a valid conferencing URL, return list of dicts
- `_extract_meet_url`: check `conferenceData.entryPoints` first (type=video), fallback to scanning description and location fields for `meet.google.com` links
- `sync_upcoming_meetings`: fetch events, for each one call `_upsert_meeting` and `_upsert_attendees`, commit, return summary counts
- `_upsert_meeting`: use `INSERT ... ON CONFLICT (external_id) DO UPDATE` pattern via SQLAlchemy — update title, start_time, end_time, meet_url if changed
- Handle `FileNotFoundError` if `credentials.json` is missing — log clear error, return gracefully, do not crash
- Handle Google API `HttpError` — log and raise `HTTPException(503)`

### 2.2 — `backend/app/services/meeting_service.py`
Fully implement:

```
class MeetingService:
    get_all(status, limit, offset) → List[Meeting]   # with eager-loaded attendees
    get_by_id(meeting_id) → Meeting | None            # with attendees + action_items
    get_by_external_id(external_id) → Meeting | None
    create(data: MeetingCreate) → Meeting
    update(meeting_id, data: MeetingUpdate) → Meeting | None
    delete(meeting_id) → bool
    get_upcoming(minutes_ahead: int = 20) → List[Meeting]  # for notification check
    mark_notified(meeting_id, attendee_email) → None
    search(query: str, limit: int = 20) → List[Meeting]    # full-text search on title
```

- Use `selectinload` for relationships
- `get_upcoming`: query meetings where `start_time BETWEEN now() AND now() + interval`, status = `scheduled`
- `search`: use `ilike` on title field

### 2.3 — `backend/app/services/notification_service.py`
Fully implement:

```
class NotificationService:
    send_email(to_emails, subject, body_html) → None
    send_meeting_reminder(meeting, attendee_emails) → None
    send_summary_ready(meeting, attendee_emails) → None
    send_slack_message(channel, text, blocks=None) → None
    send_slack_reminder(meeting) → None
    _build_reminder_email(meeting) → str   # returns HTML string
    _build_summary_email(meeting) → str    # returns HTML string
```

- Email: use `aiosmtplib`, check `settings.SMTP_USERNAME` before attempting — log warning and skip silently if not configured
- Slack: use `slack_sdk.web.async_client.AsyncWebClient`, check `settings.SLACK_BOT_TOKEN` before attempting
- `_build_reminder_email`: proper branded HTML email with MeetEdge branding, meeting title, start time, join button
- `_build_summary_email`: HTML email with executive summary, bullet list of action items, join link
- All methods must catch exceptions, log the error with `structlog`, and NOT raise — notifications must never crash the main app flow

---

## PHASE 3 — API ROUTES (implement all endpoints fully)

### 3.1 — `backend/app/api/routes/meetings.py`

Implement ALL endpoints with real logic (no stubs):

```
GET    /meetings/                   list_meetings(status, limit, offset, search)
GET    /meetings/{meeting_id}       get_meeting(meeting_id)
POST   /meetings/                   create_meeting(payload)
PATCH  /meetings/{meeting_id}       update_meeting(meeting_id, payload)
DELETE /meetings/{meeting_id}       delete_meeting(meeting_id)
GET    /meetings/{meeting_id}/attendees    get_meeting_attendees(meeting_id)
GET    /meetings/{meeting_id}/action-items get_meeting_action_items(meeting_id)
POST   /meetings/{meeting_id}/summary     store_summary(meeting_id, payload)
```

- All routes use `Depends(get_db)` and call `MeetingService`
- Return proper HTTP status codes: 200, 201, 204, 404
- Use `response_model` on every GET route

### 3.2 — `backend/app/api/routes/calendar.py`

```
POST  /calendar/sync               trigger_calendar_sync()  — background task
GET   /calendar/upcoming           get_upcoming_meetings()  — live from Google API
GET   /calendar/auth/status        google_auth_status()
GET   /calendar/events             list_synced_meetings()   — from DB
```

### 3.3 — `backend/app/api/routes/action_items.py`

```
GET    /action-items/              list_action_items(status, assigned_to, meeting_id, priority)
GET    /action-items/{item_id}     get_action_item(item_id)
PATCH  /action-items/{item_id}     update_action_item(item_id, payload)
DELETE /action-items/{item_id}     delete_action_item(item_id)
GET    /action-items/export/csv    export_action_items_csv()   # returns StreamingResponse
```

- `export_action_items_csv`: use `csv` module + `io.StringIO`, return `StreamingResponse` with `text/csv` content-type and `Content-Disposition: attachment; filename=action_items.csv`

---

## PHASE 4 — CELERY TASKS (implement fully)

### 4.1 — `backend/app/tasks/calendar_tasks.py`

```python
@celery_app.task(name="app.tasks.calendar_tasks.poll_calendar", bind=True, max_retries=3)
def poll_calendar(self):
    # Run async sync in event loop
    # Call CalendarService().sync_upcoming_meetings()
    # Log result: how many synced, how many skipped
    # On exception: retry with countdown=30 * (self.request.retries + 1)
```

Use `asyncio.new_event_loop()` — do NOT use `asyncio.run()` inside Celery as it conflicts.

### 4.2 — `backend/app/tasks/notification_tasks.py`

```python
@celery_app.task(name="app.tasks.notification_tasks.send_upcoming_reminders")
def send_upcoming_reminders():
    # 1. Query DB for meetings where:
    #    start_time BETWEEN now()+14min AND now()+16min
    #    AND status = 'scheduled'
    # 2. For each meeting, check attendees where notified_at IS NULL
    # 3. Call NotificationService.send_meeting_reminder()
    # 4. Update attendee.notified_at = now() for each notified attendee
    # 5. Log how many reminders were sent

@celery_app.task(name="app.tasks.notification_tasks.send_summary_notification")
def send_summary_notification(meeting_id: str):
    # Called after summary is generated and stored
    # Fetch meeting with attendees from DB
    # Call NotificationService.send_summary_ready()
```

---

## PHASE 5 — DATABASE MIGRATION

After implementing all models, run and commit the initial Alembic migration:

Generate the file `backend/alembic/versions/001_initial_schema.py` with the complete `upgrade()` and `downgrade()` functions that create and drop these tables in the correct order (respecting FK constraints):

1. `tenants`
2. `meetings`
3. `attendees`
4. `action_items`

Include all indexes:
- `ix_meetings_external_id` (unique)
- `ix_meetings_start_time`
- `ix_meetings_status`
- `ix_attendees_meeting_id`
- `ix_attendees_email`
- `ix_action_items_meeting_id`
- `ix_action_items_status`

---

## PHASE 6 — TESTS

### 6.1 — `backend/tests/conftest.py`
Implement a full async test setup:
- `@pytest.fixture` for async test DB (use SQLite in-memory `aiosqlite` for tests, or override DATABASE_URL env var to a test Postgres DB)
- `@pytest.fixture` for `AsyncClient` pointing at the FastAPI app
- `@pytest.fixture` for sample meeting data factory
- `@pytest.fixture` for sample attendee data factory

### 6.2 — `backend/tests/test_meetings.py`
Write tests for:
- `GET /api/v1/health/` → 200 ok
- `GET /api/v1/meetings/` → 200, returns empty list
- `POST /api/v1/meetings/` → 201, returns created meeting
- `GET /api/v1/meetings/{id}` → 200 with correct data
- `GET /api/v1/meetings/{bad-uuid}` → 404
- `PATCH /api/v1/meetings/{id}` → 200 with updated fields
- `DELETE /api/v1/meetings/{id}` → 204
- `GET /api/v1/action-items/export/csv` → 200, content-type text/csv

### 6.3 — `backend/tests/test_calendar.py`
Write tests for:
- `GET /api/v1/calendar/auth/status` with mocked `CalendarService.check_auth()` returning True and False
- `POST /api/v1/calendar/sync` → 200 response, verify background task was added
- Mock Google API calls with `unittest.mock.patch` — do NOT make real Google API calls in tests

---

## PHASE 7 — FRONTEND (Next.js 14, App Router, TypeScript, Tailwind CSS)

Implement a clean, professional dark-themed dashboard UI. Color scheme: dark navy (`#0F172A`) background, electric blue (`#0066CC`) accents, white text.

### 7.1 — `frontend/next.config.ts`
```typescript
// Enable: output standalone for Docker, image domains for avatars
// API rewrites: /api/v1/* → http://localhost:8000/api/v1/*
```

### 7.2 — `frontend/tailwind.config.ts`
Extend with custom colors matching MeetEdge brand:
- `primary`: `#0066CC`
- `surface`: `#1E293B`
- `background`: `#0F172A`
- `border`: `#334155`
- `muted`: `#64748B`

### 7.3 — `frontend/src/app/globals.css`
Set dark background, custom scrollbar styles, base font (Inter from Google Fonts).

### 7.4 — `frontend/src/app/layout.tsx`
Root layout with:
- `<html lang="en" className="dark">`
- Import globals.css
- Include `<Sidebar />` and `<Header />` from components
- Tanstack Query `QueryClientProvider` wrapping children
- Metadata: title "MeetEdge", description "AI-powered meeting intelligence"

### 7.5 — `frontend/src/app/page.tsx`
Redirect to `/dashboard` using `redirect()` from next/navigation.

### 7.6 — `frontend/src/app/login/page.tsx`
Clean login page:
- MeetEdge logo / wordmark centered
- "Sign in with Google" button (styled, with Google icon SVG inline)
- "Or continue with email" section with email + password inputs
- Submit calls `POST /api/auth/login` (stub for now, show success toast)
- Dark themed, full-screen centered card

### 7.7 — `frontend/src/app/dashboard/page.tsx`
Dashboard with 4 stat cards at top:
- Total Meetings Today
- Live Now (pulsing green dot)
- Action Items Open
- Meetings This Week

Below: two columns:
- Left (60%): "Upcoming Meetings" — list of next 5 meetings with status badge, time, join button
- Right (40%): "Recent Action Items" — last 10 open action items with assignee and deadline

All data fetched from API using Tanstack Query. Show skeleton loaders while loading.

### 7.8 — `frontend/src/app/meetings/page.tsx`
Full meetings list page:
- Search bar at top (debounced, 300ms, calls API with `?search=`)
- Filter tabs: All | Scheduled | Live | Completed
- Meeting cards in a responsive grid (2 cols on md, 3 on lg)
- Pagination controls (Previous / Next)
- "Sync Calendar" button top-right that calls `POST /api/v1/calendar/sync`

### 7.9 — `frontend/src/app/meetings/[id]/page.tsx`
Meeting detail page with tabbed layout:
- Tab 1 "Summary": `<SummaryPanel />` component
- Tab 2 "Transcript": `<TranscriptViewer />` component
- Tab 3 "Action Items": table of action items with inline status update dropdown
- Tab 4 "Attendees": avatar + name + email + response status list

Header: meeting title, date/time, organizer, status badge, "Join Meeting" button (opens meet_url)

### 7.10 — `frontend/src/app/chat/page.tsx`
Full-screen AI chat interface:
- `<ChatInterface />` component taking full remaining height
- Sidebar on left showing recent queries (stored in localStorage)
- "Ask anything about your meetings..." placeholder

### 7.11 — `frontend/src/app/action-items/page.tsx`
Kanban board with 3 columns: Open | In Progress | Completed
- Each card shows: description, assignee avatar initials, deadline badge (red if overdue), priority chip
- Drag-and-drop between columns updates status via `PATCH /api/v1/action-items/{id}`
- "Export CSV" button top-right calling `/api/v1/action-items/export/csv`
- Filter by: assignee, priority, meeting

### 7.12 — `frontend/src/components/layout/Sidebar.tsx`
Left sidebar (collapsible, 240px expanded / 64px collapsed):
- MeetEdge logo + wordmark at top
- Nav items with icons (lucide-react):
  - Dashboard → `/dashboard`
  - Meetings → `/meetings`
  - AI Chat → `/chat`
  - Action Items → `/action-items`
- Active state: blue left border + blue text + subtle blue background
- Collapse toggle button at bottom
- User avatar + name + "Secure Edge Pvt Ltd" at very bottom

### 7.13 — `frontend/src/components/layout/Header.tsx`
Top header bar:
- Page title (derived from current route)
- Right side: Calendar sync status indicator, notification bell (badge count), user avatar dropdown (Profile, Settings, Logout)

### 7.14 — `frontend/src/components/meetings/MeetingCard.tsx`
Card component showing:
- Meeting title (truncated to 2 lines)
- Date and time formatted as "Today at 2:30 PM" or "Mon, Jan 15 at 10:00 AM"
- Duration ("1h 30m")
- Organizer name
- Attendee avatar stack (up to 4, then "+N more")
- Status badge: Scheduled (blue), Live (green pulsing), Completed (gray), Failed (red)
- "Join" button (only shown if status is scheduled or live, links to meet_url)
- "View Details" link

Props: `meeting: Meeting`, `onClick?: () => void`

### 7.15 — `frontend/src/components/meetings/MeetingList.tsx`
Wrapper that:
- Takes `meetings: Meeting[]` and `isLoading: boolean`
- Shows skeleton grid of 6 cards when loading
- Shows "No meetings found" empty state with an icon when empty
- Renders `<MeetingCard />` for each meeting

### 7.16 — `frontend/src/components/meetings/TranscriptViewer.tsx`
Transcript display:
- Scrollable container with sticky speaker labels
- Each segment: speaker color-coded avatar circle (consistent color per speaker label), timestamp on right, text
- Search within transcript (highlight matching text yellow)
- "Jump to timestamp" on click
- "Copy full transcript" button
- Shows "Transcript not yet available" state if `transcript_path` is null

Props: `meetingId: string`

### 7.17 — `frontend/src/components/meetings/SummaryPanel.tsx`
Meeting summary display:
- "Executive Summary" section in a callout box
- "Key Discussion Points" as a numbered list
- "Decisions Made" as a list with checkmark icons
- "Action Items" as a mini Kanban-style list with assignee and deadline
- "Follow-ups" section
- Shows skeleton loader while fetching
- Shows "Summary being generated..." state with spinner if meeting completed but summary is null
- "Copy Summary" button that copies formatted text to clipboard

Props: `meeting: Meeting`

### 7.18 — `frontend/src/components/chat/ChatInterface.tsx`
Full AI chat component:
- Message list with auto-scroll to bottom on new message
- User messages: right-aligned, blue bubble
- Assistant messages: left-aligned, dark surface bubble
- Each assistant message shows source citations as small pill badges (meeting title + timestamp)
- Loading state: animated typing indicator (three bouncing dots)
- Input bar pinned to bottom: text input + send button (Enter or click)
- "Suggested questions" shown when chat is empty:
  - "What action items are assigned to me?"
  - "Summarize last week's product meetings"
  - "What decisions were made about the API redesign?"
- On submit: POST to `http://localhost:8000/api/v1/chat/query` with `{ query, history }`
- Show error toast if API fails

Props: none (manages its own state)

---

## PHASE 8 — HOOKS AND UTILITIES

### 8.1 — `frontend/src/hooks/useMeetings.ts`
```typescript
export function useMeetings(params?: { status?: string; search?: string; limit?: number })
// Uses Tanstack Query to fetch meetings
// Returns: { meetings, isLoading, error, refetch }

export function useMeeting(id: string)
// Fetch single meeting by ID
// Returns: { meeting, isLoading, error }

export function useSyncCalendar()
// Mutation to POST /calendar/sync
// Returns: { sync, isSyncing }
```

### 8.2 — `frontend/src/hooks/useChat.ts`
```typescript
export function useChat()
// Manages chat state: messages array, isLoading
// sendMessage(query: string) → appends user message, calls API, appends response
// clearChat() → reset messages
// Returns: { messages, isLoading, sendMessage, clearChat }
```

### 8.3 — `frontend/src/lib/utils.ts`
```typescript
export function cn(...classes: string[]) // clsx utility
export function formatDate(date: string | Date, format?: string) // date-fns formatting
export function formatDuration(startTime: string, endTime: string) // "1h 23m"
export function getStatusColor(status: MeetingStatus) // returns Tailwind class string
export function getInitials(name: string) // "Kumar Martand" → "KM"
export function truncate(str: string, length: number) // truncate with ellipsis
export function debounce<T extends (...args: any[]) => any>(fn: T, delay: number) // debounce
```

---

## PHASE 9 — SCRIPTS

### 9.1 — `scripts/google_auth.py`
Complete, runnable OAuth flow:
- Print instructions to user
- Open browser for Google OAuth consent
- Save token to `backend/token.json`
- Verify token works by making a test calendar API call
- Print success with next steps

### 9.2 — `scripts/seed_db.py`
Seed with realistic data:
- 10 meetings (mix of scheduled, live, completed)
- 3-6 attendees per meeting
- 2-5 action items per completed meeting (mix of statuses)
- Meeting titles from realistic business context: "Q3 Planning", "API Architecture Review", "Daily Standup", etc.
- One meeting "live" right now, two "scheduled" in next 2 hours

---

## PHASE 10 — FINAL CHECKS

After implementing every file, do the following verification pass:

1. **Import check**: verify every `import` statement in every Python file references a module that actually exists in the project or requirements.txt

2. **Circular import check**: ensure no circular imports between `models`, `services`, `schemas`, and `api/routes`

3. **Async consistency**: every function that uses `await` must be declared `async def`; every Celery task must use a sync wrapper around async code

4. **Environment variable completeness**: every setting referenced in code must exist in `.env.example`

5. **Type annotation completeness**: every function in Python must have type annotations on parameters and return types

6. **Frontend type safety**: no `any` types in TypeScript unless absolutely necessary and commented with reason

7. **Error handling**: every `try/except` block must log the error with structlog before handling it

8. **Missing `__init__.py` files**: ensure all Python packages have `__init__.py`

---

## CODING STANDARDS TO FOLLOW

### Python
- Python 3.11+ syntax, use `X | None` instead of `Optional[X]`
- All database operations must be `async` using SQLAlchemy 2.0 async API
- Use `structlog` for all logging — never use `print()` in production code
- Pydantic v2 — use `model_config = {"from_attributes": True}` not `class Config`
- Always use `select()` from SQLAlchemy 2.0, never `session.query()`
- Use `await session.execute(select(Model))` then `.scalars().all()`

### TypeScript / React
- Use Next.js 14 App Router — all pages are Server Components by default, add `"use client"` only when needed (hooks, event handlers, browser APIs)
- Use Tanstack Query v5 for all API data fetching
- No class components — only functional components with hooks
- Tailwind CSS only — no inline styles, no CSS modules, no styled-components
- Use `lucide-react` for all icons
- Format dates with `date-fns`

### Git hygiene
- `token.json` and `credentials.json` MUST be in `.gitignore` (already is)
- `.env` MUST be in `.gitignore` (already is)

---

## IMPORTANT NOTES FOR CURSOR

- **Do not ask questions.** Make decisions and implement.
- **Do not write placeholder comments.** Every function body must be real working code.
- **Do not skip files.** Go through every 🔧 file in the structure above.
- **Do not truncate.** Write complete files — never end a file with `# ... rest of implementation`.
- **Work in order.** Complete each phase fully before starting the next.
- When a file is complete, move to the next one immediately.
- If you reach a context limit, stop cleanly at the end of a complete file and wait for "continue".

---

## START COMMAND

Begin with Phase 1. Start implementing `backend/app/core/security.py` now.
