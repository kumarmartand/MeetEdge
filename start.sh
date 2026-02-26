#!/usr/bin/env bash
# MeetEdge — one-command start (backend + frontend). Same as run.sh.
# For full Gmail pipeline you still need: Celery worker, Celery beat, ngrok (see GMAIL_SETUP.md).
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec "$ROOT/run.sh"
