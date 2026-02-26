#!/usr/bin/env bash
# MeetEdge — stop backend and frontend (free ports 8000, 3000, 3001, 3002)
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
echo "Done. Ports 8000, 3000, 3001, 3002 are free. Run ./run.sh to start the app."
