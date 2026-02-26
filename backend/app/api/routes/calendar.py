from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import DbSession
from app.core.database import AsyncSessionLocal
from app.services.calendar_service import CalendarService
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.post("/sync")
async def trigger_calendar_sync(db: DbSession):
    svc = CalendarService(db=db)
    try:
        result = await svc.sync_upcoming_meetings()
        await db.commit()
        return result
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/upcoming")
async def get_upcoming_meetings(db: DbSession):
    cal_svc = CalendarService(db=db)
    try:
        events = cal_svc.fetch_upcoming_events(hours_ahead=24)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/auth/status")
async def google_auth_status():
    svc = CalendarService(db=None)
    ok = svc.check_auth()
    return {"authenticated": ok}


@router.get("/events")
async def list_synced_meetings(db: DbSession):
    svc = MeetingService(db)
    meetings = await svc.get_all(limit=100, offset=0)
    return {
        "events": [
            {
                "id": m.id,
                "external_id": m.external_id,
                "title": m.title,
                "start": m.start_time.isoformat(),
                "end": m.end_time.isoformat(),
                "status": m.status,
                "meet_url": m.meet_url,
            }
            for m in meetings
        ]
    }
