import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

async def manual_sync():
    from app.core.database import AsyncSessionLocal
    from app.services.calendar_service import CalendarService
    
    # We use a new engine to avoid asyncpg loop issues
    from app.core.database import engine
    
    try:
        async with AsyncSessionLocal() as session:
            svc = CalendarService(db=session)
            print("Starting manual sync...")
            res = await svc.sync_upcoming_meetings()
            await session.commit()
            print("Sync result:", res)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(manual_sync())
