import asyncio
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.models.base import Base

ASYNC_SQLITE = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        ASYNC_SQLITE,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(async_engine):
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
    )
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_meeting(db_session):
    from datetime import datetime, timezone
    from app.models.meeting import Meeting
    from app.models.attendee import Attendee

    now = datetime.now(timezone.utc)
    meeting = Meeting(
        title="Test Meeting",
        start_time=now,
        end_time=now,
        calendar_id="primary",
        status="scheduled",
    )
    db_session.add(meeting)
    await db_session.flush()
    db_session.add(Attendee(meeting_id=meeting.id, email="test@example.com"))
    await db_session.commit()
    await db_session.refresh(meeting)
    return meeting


@pytest_asyncio.fixture
async def sample_attendee(db_session, sample_meeting):
    from sqlalchemy import select
    from app.models.attendee import Attendee
    stmt = select(Attendee).where(Attendee.meeting_id == sample_meeting.id).limit(1)
    result = await db_session.execute(stmt)
    return result.scalar_one()
