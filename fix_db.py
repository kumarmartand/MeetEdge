import asyncio
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "backend"))

async def run_init():
    from app.core.database import init_db, engine
    try:
        await init_db()
        print("init_db completed")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(run_init())
