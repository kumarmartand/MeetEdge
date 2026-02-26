import csv
import io
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from app.core.deps import DbSession
from app.models.action_item import ActionItem
from app.schemas.action_item import ActionItemResponse, ActionItemCreate, ActionItemUpdate

router = APIRouter(prefix="/action-items", tags=["action_items"])


@router.get("", response_model=list[ActionItemResponse])
async def list_action_items(
    db: DbSession,
    status: str | None = Query(None),
    assigned_to: str | None = Query(None),
    meeting_id: int | None = Query(None),
    priority: str | None = Query(None),
):
    stmt = select(ActionItem).order_by(ActionItem.due_date.asc().nullslast())
    if status:
        stmt = stmt.where(ActionItem.status == status)
    if assigned_to:
        stmt = stmt.where(ActionItem.assignee_email == assigned_to)
    if meeting_id is not None:
        stmt = stmt.where(ActionItem.meeting_id == meeting_id)
    if priority:
        stmt = stmt.where(ActionItem.priority == priority)
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items


@router.get("/export/csv")
async def export_action_items_csv(db: DbSession):
    stmt = select(ActionItem).order_by(ActionItem.meeting_id, ActionItem.due_date.asc().nullslast())
    result = await db.execute(stmt)
    items = result.scalars().all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "meeting_id", "text", "assignee_email", "due_date", "status", "priority", "completed", "created_at"])
    for row in items:
        writer.writerow([
            row.id,
            row.meeting_id,
            row.text,
            row.assignee_email or "",
            row.due_date.isoformat() if row.due_date else "",
            row.status,
            row.priority or "",
            row.completed,
            row.created_at.isoformat() if row.created_at else "",
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=action_items.csv"},
    )


@router.get("/{item_id}", response_model=ActionItemResponse)
async def get_action_item(item_id: int, db: DbSession):
    stmt = select(ActionItem).where(ActionItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    return item


@router.post("", response_model=ActionItemResponse, status_code=201)
async def create_action_item(payload: ActionItemCreate, db: DbSession):
    item = ActionItem(**payload.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    await db.commit()
    return item


@router.patch("/{item_id}", response_model=ActionItemResponse)
async def update_action_item(item_id: int, payload: ActionItemUpdate, db: DbSession):
    stmt = select(ActionItem).where(ActionItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(item, k, v)
    if payload.completed is True:
        item.status = "completed"
    elif payload.completed is False:
        item.status = "open"
    await db.flush()
    await db.refresh(item)
    await db.commit()
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_action_item(item_id: int, db: DbSession):
    stmt = select(ActionItem).where(ActionItem.id == item_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Action item not found")
    await db.delete(item)
    await db.commit()
    return None
