import asyncio
from app.core.database import AsyncSessionLocal
from sqlalchemy import select
from app.models.meeting import Meeting
from app.utils.datetime_utils import utcnow

async def run():
    now = utcnow()
    print("CURRENT TIME (UTC):", now)
    
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(Meeting))
        meetings = res.scalars().all()
        for m in (meetings or []):
            if not m.recall_bot_id:
                print(f"[{m.id}] {m.title} -> start: {m.start_time} (UTC)")

asyncio.run(run())
