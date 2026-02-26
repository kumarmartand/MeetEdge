#!/usr/bin/env bash
# Start backend (creates venv + deps if needed). Postgres must be running for DB routes.
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/backend"

if [ ! -f .env ]; then
  cp .env.example .env 2>/dev/null || true
  echo "Created backend/.env from .env.example"
fi

if [ ! -d .venv ]; then
  python3 -m venv .venv
  .venv/bin/pip install -r requirements.txt -q
  echo "Created venv and installed dependencies"
fi

source .venv/bin/activate
echo "Backend: http://localhost:8000  |  Docs: http://localhost:8000/docs"
exec uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
