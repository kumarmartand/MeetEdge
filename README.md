# MeetEdge

Meeting notes and action items with Google Calendar sync.

## One-time: start Postgres and migrations

**If you use Docker:**
```bash
docker compose up -d
cd backend && source .venv/bin/activate && alembic upgrade head
```

**If you don’t have Docker:** install Postgres locally and run migrations. See **[RUNNING_WITHOUT_DOCKER.md](RUNNING_WITHOUT_DOCKER.md)** for step-by-step (macOS, Linux, Windows).

## Run checklist

| Step | Command | Purpose |
|------|--------|--------|
| 1 | `docker compose up -d` | Start Postgres (port 5432), Redis (6379), pgAdmin (5050) |
| 2 | `cd backend && source .venv/bin/activate && alembic upgrade head` | Create DB tables (run once) |
| 3 | `uvicorn app.main:app --reload --port 8000` | Start API → http://localhost:8000, docs → http://localhost:8000/docs |
| 4 | `cd frontend && npm run dev` | Start app → http://localhost:3000 |
| 5 | `python scripts/seed_db.py` (from repo root) | Optional: seed sample meetings |

**Without Docker:** The backend will start and `/api/v1/health` will work, but any route that uses the database (e.g. `/api/v1/meetings`) will return 500 until Postgres is running and migrations have been applied.

**Frontend 404s:** Run `cd frontend && npm run start:prod` (or `./scripts/start-frontend.sh`) instead of `npm run dev`.

### 1. Docker (Postgres + Redis + pgAdmin)

```bash
docker-compose up -d
# Postgres: localhost:5432, Redis: localhost:6379, pgAdmin: http://localhost:5050
```

### 2. Backend

```bash
cd backend
cp .env.example .env   # edit if needed
python3 -m venv .venv && source .venv/bin/activate  # or Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head   # run migrations (creates tenants, meetings, attendees, action_items)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
# API: http://localhost:8000, API v1: http://localhost:8000/api/v1, docs: http://localhost:8000/docs
```

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
# App: http://localhost:3000
```

### 4. Optional: Google Calendar OAuth (run once)

```bash
# Place Google OAuth client credentials at backend/credentials.json
python scripts/google_auth.py
# Then set GOOGLE_TOKEN_PATH in backend/.env if needed
```

### 5. Seed sample data

```bash
python scripts/seed_db.py
```

### 6. Celery (optional, for background sync/notifications)

```bash
cd backend && celery -A app.tasks.celery_app worker --loglevel=info
```

## Project structure

- `docker-compose.yml` — Postgres, Redis, pgAdmin
- `scripts/google_auth.py` — OAuth token for Google Calendar
- `scripts/seed_db.py` — Sample meetings for dev
- `backend/` — FastAPI app, Alembic, Celery tasks
- `frontend/` — Next.js 14 App Router, API client, components
