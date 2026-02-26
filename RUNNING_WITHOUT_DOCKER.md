# Running MeetEdge Without Docker

You can run the app using a **locally installed** Postgres (and optional Redis) instead of Docker.

---

## 1. Install PostgreSQL

### macOS (Homebrew)

```bash
brew install postgresql@16
brew services start postgresql@16
```

Create the database and user:

```bash
# Add to PATH if needed: export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
createuser -s postgres   # if not exists
createdb meetedge       # database name
psql -d meetedge -c "CREATE USER meetedge WITH PASSWORD 'meetedge_dev';"
psql -d meetedge -c "GRANT ALL PRIVILEGES ON DATABASE meetedge TO meetedge;"
psql -d meetedge -c "ALTER DATABASE meetedge OWNER TO meetedge;"
```

If your Mac uses the default `postgres` user with no password (local only), you can use:

```bash
createdb meetedge
# Then in backend/.env set:
# DATABASE_URL=postgresql://YOUR_MAC_USER@localhost:5432/meetedge
# (replace YOUR_MAC_USER with your macOS username, or use postgres if that user exists)
```

### Linux (Ubuntu / Debian)

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo -u postgres createuser --interactive   # create user meetedge
sudo -u postgres createdb meetedge
sudo -u postgres psql -c "ALTER USER meetedge WITH PASSWORD 'meetedge_dev';"
sudo -u postgres psql -d meetedge -c "GRANT ALL ON SCHEMA public TO meetedge;"
```

### Windows

1. Download installer from https://www.postgresql.org/download/windows/
2. Install and note the port (default 5432) and password you set for user `postgres`.
3. Create database: open pgAdmin or run `psql -U postgres` then `CREATE DATABASE meetedge;`
4. In `backend/.env` set:
   ```env
   DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/meetedge
   ```

---

## 2. Configure the backend

Create `backend/.env` (or copy from `.env.example`) and set the URL to your local Postgres:

```env
# Use the URL that matches how you created the DB (user, password, host, port, db name)
DATABASE_URL=postgresql://meetedge:meetedge_dev@localhost:5432/meetedge
```

If you used your macOS username and no password (common on Mac):

```env
DATABASE_URL=postgresql://YOUR_MAC_USERNAME@localhost:5432/meetedge
```

---

## 3. Run migrations and start the app

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

Then in another terminal, start the frontend:

```bash
cd frontend
npm install
npm run start:prod
```

Open http://localhost:3000 and http://localhost:8000/docs.

---

## 4. Optional: Redis (for Celery)

Only needed if you use background tasks (calendar sync, notifications).

### macOS

```bash
brew install redis
brew services start redis
```

### Linux

```bash
sudo apt install redis-server
sudo systemctl start redis
```

Keep the default in `.env`: `REDIS_URL=redis://localhost:6379/0`. If Redis is not installed, the app still runs; only Celery workers would fail.

---

## 5. Seed sample data (optional)

```bash
# From project root, with backend venv activated
cd backend && source .venv/bin/activate
python ../scripts/seed_db.py
```

---

## Quick reference

| Step              | Command |
|-------------------|--------|
| Install Postgres  | See section 1 for your OS |
| Create DB/user    | See section 1 |
| Set `.env`        | `DATABASE_URL=postgresql://user:pass@localhost:5432/meetedge` |
| Migrate           | `cd backend && source .venv/bin/activate && alembic upgrade head` |
| Start backend     | `uvicorn app.main:app --reload --port 8000` |
| Start frontend    | `cd frontend && npm run start:prod` |
