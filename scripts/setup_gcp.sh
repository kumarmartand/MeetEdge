#!/usr/bin/env bash
# MeetEdge — Create GCP Pub/Sub topic + push subscription for Gmail.
# Usage: bash scripts/setup_gcp.sh YOUR_PROJECT_ID https://your-ngrok-or-domain.io
# Prereqs: gcloud CLI installed and authenticated (gcloud auth login; gcloud auth application-default login)
set -e
PROJECT_ID="${1:?Usage: scripts/setup_gcp.sh PROJECT_ID BASE_URL}"
BASE_URL="${2:?Usage: scripts/setup_gcp.sh PROJECT_ID BASE_URL}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/backend/.env"
TOPIC_NAME="meetedge-gmail-push"
SUBSCRIPTION_NAME="meetedge-gmail-push-sub"

# Ensure base URL has no trailing slash
BASE_URL="${BASE_URL%/}"
WEBHOOK_PATH="/api/v1/gmail/webhook"

echo "=== MeetEdge GCP Gmail setup ==="
echo "Project: $PROJECT_ID"
echo "Base URL: $BASE_URL"
echo ""

# Use existing webhook secret from .env or generate one
if [ -f "$ENV_FILE" ]; then
  SECRET=$(grep "^GMAIL_WEBHOOK_SECRET=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '\r' | head -1)
fi
if [ -z "$SECRET" ]; then
  SECRET=$(openssl rand -hex 24 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(24))")
  echo "Generated new GMAIL_WEBHOOK_SECRET (will write to .env)"
else
  echo "Using existing GMAIL_WEBHOOK_SECRET from .env"
fi

PUSH_URL="${BASE_URL}${WEBHOOK_PATH}?token=${SECRET}"
echo "Push URL: $PUSH_URL"
echo ""

gcloud config set project "$PROJECT_ID"

echo "Enabling APIs..."
gcloud services enable pubsub.googleapis.com gmail.googleapis.com --quiet

echo "Creating Pub/Sub topic: $TOPIC_NAME"
gcloud pubsub topics create "$TOPIC_NAME" 2>/dev/null || true

echo "Granting Gmail publish permission on topic..."
gcloud pubsub topics add-iam-policy-binding "$TOPIC_NAME" \
  --member="serviceAccount:gmail-api-push@system.gserviceaccount.com" \
  --role="roles/pubsub.publisher" \
  --quiet

echo "Creating push subscription (subscription: $SUBSCRIPTION_NAME)..."
gcloud pubsub subscriptions delete "$SUBSCRIPTION_NAME" --quiet 2>/dev/null || true
gcloud pubsub subscriptions create "$SUBSCRIPTION_NAME" \
  --topic="$TOPIC_NAME" \
  --push-endpoint="$PUSH_URL" \
  --ack-deadline=30 \
  --quiet

TOPIC_FULL="projects/${PROJECT_ID}/topics/${TOPIC_NAME}"
echo ""
echo "Updating backend/.env..."
if [ ! -f "$ENV_FILE" ]; then
  cp "$ROOT/backend/.env.example" "$ENV_FILE" 2>/dev/null || touch "$ENV_FILE"
fi
for key in GMAIL_PUBSUB_TOPIC GMAIL_WEBHOOK_SECRET; do
  if [ "$key" = "GMAIL_PUBSUB_TOPIC" ]; then val="$TOPIC_FULL"; else val="$SECRET"; fi
  if grep -q "^${key}=" "$ENV_FILE" 2>/dev/null; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" "$ENV_FILE"
  else
    echo "${key}=${val}" >> "$ENV_FILE"
  fi
done
rm -f "${ENV_FILE}.bak" 2>/dev/null || true

echo ""
echo "Done. Next steps:"
echo "  1. Start backend and run: curl -X POST http://localhost:8000/api/v1/gmail/setup-watch"
echo "  2. Keep ngrok (or your URL) and backend running so Pub/Sub can reach the webhook."
echo "  3. Run Celery worker: celery -A app.tasks.celery_app worker --loglevel=info"
