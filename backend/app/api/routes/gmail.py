"""
Gmail push webhook and watch setup. See GMAIL_SETUP.md.
"""
import base64
import json
from fastapi import APIRouter, Request, HTTPException, Query

from app.core.config import get_settings

router = APIRouter(prefix="/gmail", tags=["gmail"])


def _get_gmail_service():
    """Build Gmail API service from OAuth credentials."""
    from app.utils.google_auth import load_credentials
    from googleapiclient.discovery import build

    creds = load_credentials()
    if not creds:
        return None
    return build("gmail", "v1", credentials=creds)


@router.get("/status")
async def gmail_status():
    """Check OAuth + Gmail config status."""
    from app.utils.google_auth import get_credentials_path

    settings = get_settings()
    creds_path, token_path = get_credentials_path()
    has_creds = creds_path is not None and creds_path.exists()
    has_token = token_path is not None and token_path.exists()
    service = _get_gmail_service()
    return {
        "oauth_credentials": has_creds,
        "oauth_token": has_token,
        "gmail_api_ok": service is not None,
        "gmail_pubsub_topic_set": bool(settings.gmail_pubsub_topic),
        "gmail_webhook_secret_set": bool(settings.gmail_webhook_secret),
    }


@router.post("/webhook")
async def gmail_webhook(
    request: Request,
    token: str | None = Query(None, alias="token"),
):
    """
    Pub/Sub push endpoint. Google sends POST with JSON body.
    Verify ?token= matches GMAIL_WEBHOOK_SECRET, then enqueue Celery task.
    """
    settings = get_settings()
    if not settings.gmail_webhook_secret or token != settings.gmail_webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid or missing webhook token")

    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    message = body.get("message") or {}
    raw_data = message.get("data")
    if not raw_data:
        return {}  # acknowledge

    try:
        decoded = base64.b64decode(raw_data).decode("utf-8")
        data = json.loads(decoded)
    except Exception:
        return {}  # acknowledge but skip

    history_id = data.get("historyId")
    if history_id:
        from app.tasks.gmail_tasks import process_gmail_push

        process_gmail_push.delay(str(history_id))
    return {}


@router.post("/setup-watch")
async def setup_watch():
    """Register Gmail push watch. Watch expires in ~7 days; renew via Celery beat or call again."""
    settings = get_settings()
    if not settings.gmail_pubsub_topic:
        raise HTTPException(
            status_code=503,
            detail="GMAIL_PUBSUB_TOPIC not set. Run scripts/setup_gcp.sh and set it in backend/.env",
        )

    service = _get_gmail_service()
    if not service:
        raise HTTPException(
            status_code=503,
            detail="Gmail API not available. Run scripts/google_auth.py and ensure token.json has Gmail scopes.",
        )

    try:
        result = (
            service.users()
            .watch(
                userId="me",
                body={
                    "topicName": settings.gmail_pubsub_topic,
                    "labelIds": ["INBOX"],
                },
            )
            .execute()
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gmail watch failed: {str(e)[:200]}")

    return {
        "status": "watch_registered",
        "expiration_ms": str(result.get("expiration", "")),
        "history_id": str(result.get("historyId", "")),
        "topic": settings.gmail_pubsub_topic,
    }


@router.delete("/stop-watch")
async def stop_watch():
    """Unregister Gmail push watch."""
    service = _get_gmail_service()
    if not service:
        raise HTTPException(status_code=503, detail="Gmail API not available.")
    try:
        service.users().stop(userId="me").execute()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Gmail stop failed: {str(e)[:200]}")
    return {"status": "watch_stopped"}
