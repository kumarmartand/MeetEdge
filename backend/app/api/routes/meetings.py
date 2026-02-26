from fastapi import APIRouter, Depends, HTTPException, Query
from app.core.deps import DbSession
from app.schemas.meeting import (
    MeetingResponse,
    MeetingCreate,
    MeetingUpdate,
    SummaryStorePayload,
)
from app.schemas.attendee import AttendeeSchema
from app.schemas.action_item import ActionItemResponse
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/meetings", tags=["meetings"])


@router.get("", response_model=list[MeetingResponse])
async def list_meetings(
    db: DbSession,
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str | None = Query(None),
):
    svc = MeetingService(db)
    if search:
        meetings = await svc.search(search, limit=limit)
    else:
        meetings = await svc.get_all(status=status, limit=limit, offset=offset)
    return meetings


@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(meeting_id: int, db: DbSession):
    svc = MeetingService(db)
    meeting = await svc.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting


@router.post("", response_model=MeetingResponse, status_code=201)
async def create_meeting(payload: MeetingCreate, db: DbSession):
    svc = MeetingService(db)
    meeting = await svc.create(payload)
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.patch("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(meeting_id: int, payload: MeetingUpdate, db: DbSession):
    svc = MeetingService(db)
    meeting = await svc.update(meeting_id, payload)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: int, db: DbSession):
    svc = MeetingService(db)
    ok = await svc.delete(meeting_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Meeting not found")
    await db.commit()
    return None


@router.get("/{meeting_id}/attendees", response_model=list[AttendeeSchema])
async def get_meeting_attendees(meeting_id: int, db: DbSession):
    svc = MeetingService(db)
    meeting = await svc.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting.attendees


@router.get("/{meeting_id}/action-items", response_model=list[ActionItemResponse])
async def get_meeting_action_items(meeting_id: int, db: DbSession):
    svc = MeetingService(db)
    meeting = await svc.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting.action_items


@router.post("/{meeting_id}/summary")
async def store_summary(meeting_id: int, payload: SummaryStorePayload, db: DbSession):
    svc = MeetingService(db)
    meeting = await svc.get_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    meeting.summary = payload.summary
    meeting.summary_key_points = {
        "key_points": payload.key_points or [],
        "decisions": payload.decisions or [],
        "action_items_summary": payload.action_items_summary or [],
        "follow_ups": payload.follow_ups or [],
    }
    await db.commit()
    await db.refresh(meeting)
    return {"ok": True}
