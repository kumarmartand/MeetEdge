#!/usr/bin/env bash
# MeetEdge — run backend + frontend (requires Postgres for full API)
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

echo "=== MeetEdge ==="

# 1. Check Postgres
if command -v docker &>/dev/null; then
  if ! docker ps 2>/dev/null | grep -q postgres; then
    echo "Starting Docker (Postgres, Redis)..."
    (docker compose up -d 2>/dev/null || docker-compose up -d 2>/dev/null) || true
    sleep 3
  fi
fi
if python3 -c "import socket; s=socket.socket(); s.settimeout(2); exit(0 if s.connect_ex(('127.0.0.1',5432))==0 else 1)" 2>/dev/null; then
  echo "Postgres: running"
  cd backend && source .venv/bin/activate 2>/dev/null || true
  if [ -d .venv ]; then
    alembic upgrade head 2>/dev/null && echo "Migrations: ok" || echo "Migrations: run manually (alembic upgrade head)"
  fi
  cd "$ROOT"
else
  echo "Postgres: not running (start with: docker compose up -d)"
  echo "  API routes that use the DB will return 500 until Postgres is up and migrations are run."
fi

# 2. Backend
echo ""
echo "Starting backend on http://localhost:8000 ..."
cd "$ROOT/backend"
if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt -q
fi
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

echo "Starting Celery worker and beat..."
.venv/bin/celery -A app.tasks.celery_app worker --loglevel=info &
CELERY_WORKER_PID=$!

.venv/bin/celery -A app.tasks.celery_app beat --loglevel=info &
CELERY_BEAT_PID=$!

cd "$ROOT"

# 3. Frontend
echo "Starting frontend on http://localhost:3000 ..."
cd "$ROOT/frontend"
[ -d node_modules ] || npm install -q
npm run dev &
FRONTEND_PID=$!
cd "$ROOT"

echo ""
echo "Backend:  http://localhost:8000  (docs: http://localhost:8000/docs)"
echo "Frontend: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop both."
wait $BACKEND_PID $CELERY_WORKER_PID $CELERY_BEAT_PID $FRONTEND_PID 2>/dev/null || true
