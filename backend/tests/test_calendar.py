import pytest
from unittest.mock import patch, MagicMock
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_calendar_auth_status_authenticated(client: AsyncClient):
    with patch("app.api.routes.calendar.CalendarService") as MockCal:
        MockCal.return_value.check_auth.return_value = True
        r = await client.get("/api/v1/calendar/auth/status")
        assert r.status_code == 200
        assert r.json()["authenticated"] is True


@pytest.mark.asyncio
async def test_calendar_auth_status_not_authenticated(client: AsyncClient):
    with patch("app.api.routes.calendar.CalendarService") as MockCal:
        MockCal.return_value.check_auth.return_value = False
        r = await client.get("/api/v1/calendar/auth/status")
        assert r.status_code == 200
        assert r.json()["authenticated"] is False


@pytest.mark.asyncio
async def test_calendar_sync_success(client: AsyncClient):
    async def mock_sync():
        return {"synced": 2, "skipped": 0}

    with patch("app.api.routes.calendar.CalendarService") as MockCal:
        mock_svc = MagicMock()
        mock_svc.sync_upcoming_meetings = mock_sync
        MockCal.return_value = mock_svc
        r = await client.post("/api/v1/calendar/sync")
        assert r.status_code == 200
        data = r.json()
        assert data.get("synced") == 2 and data.get("skipped") == 0
