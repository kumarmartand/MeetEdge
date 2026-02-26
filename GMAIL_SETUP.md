# Connecting MeetEdge to Gmail

This guide connects your Gmail inbox so MeetEdge automatically:
1. Detects a Google Meet invite the moment it arrives
2. Stores the meeting and notifies attendees
3. Joins the meeting with a headless bot at start time
4. Records audio, generates a transcript + AI summary
5. Emails the summary to all attendees

---

## How it works (the full flow)

```
Your inbox receives a Meet invite
        │
        ▼
Gmail Pub/Sub pushes a notification to your server
        │
        ▼
POST /api/v1/gmail/webhook
        │
        ▼
Celery task: parse email → extract .ics → find Meet URL
        │
        ▼
Upsert meeting + attendees into PostgreSQL
        │
        ▼
Email attendees: "MeetEdge Bot will join your meeting"
        │
        ▼  (countdown to start_time)
Celery task: headless Chromium joins the Meet
        │
        ▼
Email attendees: "Recording has started"
        │
        ▼  (meeting ends)
Audio saved → (transcription service) → summary in DB
        │
        ▼
Email attendees: "Summary is ready" + link to dashboard
```

---

## Step 1 — Google Cloud Console setup (one-time)

### 1a. Create a GCP Project (skip if you have one)
1. Go to https://console.cloud.google.com
2. Click **Select a project → New Project**
3. Name it `meetedge` → Create
4. Copy your **Project ID** (e.g. `meetedge-123456`)

### 1b. Enable APIs
In the GCP Console, go to **APIs & Services → Library** and enable:
- **Gmail API**
- **Google Calendar API**
- **Cloud Pub/Sub API**

### 1c. Create OAuth credentials
1. **APIs & Services → Credentials → + Create Credentials → OAuth Client ID**
2. Application type: **Desktop App**
3. Name: `MeetEdge Local`
4. Download the JSON file
5. Rename it to `credentials.json`
6. Place it in `backend/credentials.json` (project root = MeetEdge)

### 1d. Create a Pub/Sub topic + subscription
Run the helper script (requires `gcloud` CLI):

```bash
# Install gcloud if needed:
# macOS: brew install google-cloud-sdk
# Linux: apt-get install google-cloud-cli

# Authenticate
gcloud auth login
gcloud auth application-default login

# For local dev, use ngrok to expose localhost:
brew install ngrok
ngrok http 8000
# Copy the https URL (e.g. https://abc123.ngrok.io)

# Run setup script
bash scripts/setup_gcp.sh YOUR_PROJECT_ID https://abc123.ngrok.io
```

What the script does automatically:
- Enables Pub/Sub + Gmail APIs
- Creates topic `meetedge-gmail-push`
- Grants Gmail's service account publish permission on that topic
- Creates a push subscription pointing at `https://your-domain/api/v1/gmail/webhook?token=SECRET`
- Updates `backend/.env` with `GMAIL_PUBSUB_TOPIC`

---

## Step 2 — Configure backend/.env

Open `backend/.env` and fill in these values:

```bash
# Your GCP project (auto-filled by setup script)
GMAIL_PUBSUB_TOPIC=projects/YOUR_PROJECT_ID/topics/meetedge-gmail-push

# Random string — must match the ?token= in your push subscription URL
GMAIL_WEBHOOK_SECRET=pick-a-long-random-string

# The bot Google account that joins meetings
GOOGLE_BOT_EMAIL=your-bot@gmail.com
GOOGLE_BOT_PASSWORD=your-app-password   # NOT your real password
                                         # Generate at: myaccount.google.com/apppasswords

# Email notifications (use your Gmail + an App Password)
SMTP_USERNAME=your@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM_EMAIL=your@gmail.com

# Slack (optional — leave blank to skip)
SLACK_BOT_TOKEN=xoxb-...
SLACK_DEFAULT_CHANNEL=#meetings
```

**About App Passwords:** Gmail requires you to use an App Password (not your real password) when 2FA is enabled. Generate one at https://myaccount.google.com/apppasswords for both `GOOGLE_BOT_PASSWORD` and `SMTP_PASSWORD`.

---

## Step 3 — Generate OAuth token (one-time per machine)

```bash
cd backend
source .venv/bin/activate
python ../scripts/google_auth.py
```

This opens a browser window. Sign in with the **Gmail account you want to watch** (the account that receives meeting invites — not the bot account).

Grant access to:
- View your calendar
- View and manage your Gmail

This creates `backend/token.json` which the app uses on every request.

---

## Step 4 — Install Playwright (bot browser)

```bash
cd backend
source .venv/bin/activate
pip install playwright
playwright install chromium
```

---

## Step 5 — Audio recording setup (optional)

Without this, the bot joins the meeting silently but doesn't record.

**macOS:**
```bash
brew install blackhole-2ch    # Virtual audio device
brew install ffmpeg

# In backend/.env:
AUDIO_DEVICE=BlackHole 2ch
```
Then in **System Preferences → Sound → Output**, set output to "BlackHole 2ch" when the meeting is running. (The bot captures whatever audio plays through that device.)

**Linux:**
```bash
apt-get install pulseaudio-utils ffmpeg

# In backend/.env:
AUDIO_DEVICE=default.monitor
```

---

## Step 6 — Start everything

```bash
# Terminal 1 — Docker (Postgres + Redis)
docker compose up -d

# Terminal 2 — FastAPI backend
cd backend && source .venv/bin/activate
alembic upgrade head
uvicorn app.main:app --reload --port 8000

# Terminal 3 — Celery worker (processes the Gmail pipeline tasks)
cd backend && source .venv/bin/activate
celery -A app.tasks.celery_app worker --loglevel=info

# Terminal 4 — Celery beat (schedules reminders + watch renewal)
cd backend && source .venv/bin/activate
celery -A app.tasks.celery_app beat --loglevel=info

# Terminal 5 — Frontend
cd frontend && npm run dev

# Terminal 6 — ngrok (exposes localhost for Pub/Sub webhooks)
ngrok http 8000
```

Or use the one-command starter:
```bash
./start.sh
```
(Note: you still need to run ngrok and Celery worker/beat manually if using start.sh)

---

## Step 7 — Register Gmail watch

With the backend running, call:
```bash
curl -X POST http://localhost:8000/api/v1/gmail/setup-watch
```

Expected response:
```json
{
  "status": "watch_registered",
  "expiration_ms": "1736000000000",
  "history_id": "12345",
  "topic": "projects/YOUR_PROJECT/topics/meetedge-gmail-push"
}
```

**The watch expires every 7 days.** The Celery beat task `renew_gmail_watch` re-registers it every 6 days automatically. If you restart from scratch, just call the endpoint again.

---

## Step 8 — Test it end-to-end

1. Send yourself a Google Calendar invite that includes a Google Meet link
2. Watch the Celery worker logs:
   ```
   [INFO] Gmail push received  history_id=12345
   [INFO] Calendar invite found  title="Team Standup"
   [INFO] Meeting upserted  meeting_id=abc-123
   [INFO] Email sent  to=['you@company.com']
   [INFO] Bot join scheduled in 900s for Team Standup
   ```
3. Check your email — you should receive "MeetEdge Bot will join your meeting"
4. At meeting start time, the bot joins and you'll get "Recording has started"
5. After the meeting: "Summary is ready" email with link to dashboard

---

## Troubleshooting

### No webhook calls arriving
- Check ngrok is running: `ngrok http 8000` — copy the HTTPS URL
- Verify the Pub/Sub subscription push URL matches: `https://YOUR_NGROK_URL/api/v1/gmail/webhook?token=YOUR_SECRET`
- Check GCP Console → Pub/Sub → Subscriptions → your subscription → Messages → view

### "Gmail credentials missing" error
- Run `python scripts/google_auth.py` again
- Make sure `backend/token.json` exists
- Check scopes include gmail.readonly and gmail.modify

### Bot can't sign in
- Enable 2FA on the bot Google account
- Generate an App Password at myaccount.google.com/apppasswords
- Use that as `GOOGLE_BOT_PASSWORD` (not the real password)

### Bot joins but doesn't record
- Check ffmpeg is installed: `ffmpeg -version`
- macOS: verify BlackHole is installed and set as audio output
- Try without recording first (leave `AUDIO_DEVICE=` blank)

### Watch expired / stopped receiving emails
```bash
curl -X POST http://localhost:8000/api/v1/gmail/setup-watch
```

### Check system status
```bash
curl http://localhost:8000/api/v1/gmail/status
curl http://localhost:8000/api/v1/health/
```

---

## API reference for the Gmail pipeline

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/gmail/webhook` | Pub/Sub push entry point (called by Google) |
| `POST` | `/api/v1/gmail/setup-watch` | Register Gmail push (call once, or on redeploy) |
| `DELETE` | `/api/v1/gmail/stop-watch` | Unregister Gmail push |
| `GET` | `/api/v1/gmail/status` | Check OAuth + config status |
| `GET` | `/api/v1/health/` | Overall system health |

