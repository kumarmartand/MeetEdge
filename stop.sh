#!/usr/bin/env bash
# MeetEdge — stop backend, frontend, Celery, ngrok (free ports 8000, 3000, 3001, 3002)
set -e
for port in 8000 3000 3001 3002; do
  if command -v lsof &>/dev/null; then
    pids=$(lsof -ti :$port 2>/dev/null) || true
    if [ -n "$pids" ]; then
      echo "Stopping port $port (PIDs: $pids)"
      echo "$pids" | xargs kill -9 2>/dev/null || true
    else
      echo "Port $port: nothing running"
    fi
  fi
done
# Stop Celery workers/beat (by process name)
if command -v pkill &>/dev/null; then
  pkill -f "celery -A app.tasks.celery_app" 2>/dev/null && echo "Stopped Celery" || true
fi
# Stop ngrok
if command -v pkill &>/dev/null; then
  pkill -f "ngrok http" 2>/dev/null && echo "Stopped ngrok" || true
fi
echo "Done. Ports 8000, 3000, 3001, 3002 are free. Run ./run.sh to start the app."
