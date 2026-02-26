from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging
from app.api.router import api_router

setup_logging()
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.core.database import engine
    try:
        from sqlalchemy import text
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        print("MeetEdge: Database connected.")
    except Exception as e:
        print("MeetEdge: Database not reachable. Start Postgres (e.g. docker compose up -d) and run: alembic upgrade head")
        print("  Error:", str(e)[:80])
    yield
    await engine.dispose()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"app": settings.app_name, "docs": "/docs"}
