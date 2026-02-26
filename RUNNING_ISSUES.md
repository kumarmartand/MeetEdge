# Issues in Running MeetEdge

**Quick start (after Postgres is up):**
- Backend: `./scripts/start-backend.sh` or `cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000`
- Frontend (avoids 404): `./scripts/start-frontend.sh` or `cd frontend && npm run start:prod`

---

## 1. **Postgres not running (backend 500s)**

**Symptom:** `/api/v1/meetings`, `/api/v1/calendar/events`, etc. return **500 Internal Server Error** or connection errors.

**Cause:** The app expects PostgreSQL at `localhost:5432`. If Docker isn’t running or Postgres isn’t started, the DB is unreachable.

**Fix:**
```bash
cd /Users/martandsingh/Documents/MeetEdge
docker compose up -d
# or: docker-compose up -d
```
Then run migrations once:
```bash
cd backend && source .venv/bin/activate && alembic upgrade head
```

---

## 2. **Migrations fail (Alembic)**

**Symptom:** `alembic upgrade head` fails with `connection refused` on port 5432.

**Cause:** Same as above — Postgres must be running before migrations.

**Fix:** Start Docker (step 1), wait a few seconds, then run `alembic upgrade head` again.

---

## 3. **Frontend shows 404 for all routes**

**Symptom:** Opening `http://localhost:3000/` or `/dashboard` shows “404 – This page could not be found” (sometimes with layout/sidebar still visible).

**Cause:** Next.js dev server can hit **“EMFILE: too many open files”** (Watchpack). When the file watcher fails, new routes may not be registered, so every path falls through to the 404 page.

**Fixes:**
- **Recommended:** Use production build (avoids file watcher entirely):
  ```bash
  cd frontend && npm run start:prod
  ```
  Or: `./scripts/start-frontend.sh`
- **Option B:** Increase file descriptor limit, then dev: `ulimit -n 10240` then `npm run dev`
- **Option C:** Close other apps/terminals and restart `npm run dev`.

---

## 4. **Port already in use**

**Symptom:**  
- `Error: listen EADDRINUSE: address already in use :::3000` (frontend)  
- `address already in use` when starting uvicorn on 8000 (backend)

**Cause:** Another process is already using that port (e.g. an old `npm run dev` or `uvicorn`).

**Fix:**
- Find and stop the process:
  ```bash
  lsof -i :3000   # or :8000
  kill <PID>
  ```
- Or use another port:
  - Frontend: `npm run dev -- -p 3001`
  - Backend: `uvicorn app.main:app --reload --port 8001`

---

## 5. **Docker / docker-compose not available**

**Symptom:** `docker compose` or `docker-compose` not found.

**Cause:** Docker isn’t installed or isn’t on your PATH.

**Fix:** You can run **without Docker**. Install Postgres (and optionally Redis) locally — see **[RUNNING_WITHOUT_DOCKER.md](RUNNING_WITHOUT_DOCKER.md)** for step-by-step (macOS, Linux, Windows).

---

## 6. **Backend venv or dependencies missing**

**Symptom:** `ModuleNotFoundError: No module named 'fastapi'` (or similar) when running uvicorn or tests.

**Cause:** Virtualenv not activated or dependencies not installed.

**Fix:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 7. **Frontend API calls fail (CORS or wrong URL)**

**Symptom:** Browser console shows CORS errors or 404 when the frontend calls the API.

**Cause:** Backend not running, or frontend not proxying to the correct host/port.

**Fix:**
- Ensure backend is running: `http://localhost:8000` and `http://localhost:8000/api/v1/health` return OK.
- Frontend rewrites `/api/v1/*` to `http://localhost:8000/api/v1/*` (see `frontend/next.config.js`). If the backend runs on another port, change the `destination` in `rewrites` to match (e.g. `http://localhost:8001/api/v1/:path*`).

---

## 8. **Security / JWT (optional)**

**Symptom:** You want to use JWT auth; keys or config may be missing.

**Cause:** `app/core/security.py` uses RS256. If `JWT_PRIVATE_KEY_PATH` and `JWT_PUBLIC_KEY_PATH` are not set in `.env`, it generates in-memory keys (fine for dev; not for production).

**Fix (production):** Generate an RSA key pair and set in `backend/.env`:
```bash
JWT_PRIVATE_KEY_PATH=/path/to/private.pem
JWT_PUBLIC_KEY_PATH=/path/to/public.pem
```

---

## Quick “everything works” checklist

| # | Check | Command / action |
|---|--------|-------------------|
| 1 | Postgres running | `docker compose up -d` then `nc -z localhost 5432` or check `docker ps` |
| 2 | Migrations applied | `cd backend && source .venv/bin/activate && alembic upgrade head` |
| 3 | Backend running | `curl -s http://localhost:8000/api/v1/health` → `{"status":"ok"}` |
| 4 | DB routes work | `curl -s http://localhost:8000/api/v1/meetings` → `[]` (not 500) |
| 5 | Frontend running | `cd frontend && npm run dev` (or `npm run build && npm run start`) |
| 6 | App loads | Open `http://localhost:3000` (or 3001 if dev picked that port) |

If all of the above pass, the project is running correctly.
