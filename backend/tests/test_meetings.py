import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_ok(client: AsyncClient):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_meetings_list_empty(client: AsyncClient):
    r = await client.get("/api/v1/meetings")
    assert r.status_code == 200
    assert r.json() == []


@pytest.mark.asyncio
async def test_meetings_create_and_get(client: AsyncClient):
    payload = {
        "title": "New Meeting",
        "start_time": "2025-03-01T10:00:00Z",
        "end_time": "2025-03-01T11:00:00Z",
    }
    r = await client.post("/api/v1/meetings", json=payload)
    assert r.status_code == 201
    data = r.json()
    assert data["title"] == "New Meeting"
    assert "id" in data
    mid = data["id"]

    r2 = await client.get(f"/api/v1/meetings/{mid}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "New Meeting"


@pytest.mark.asyncio
async def test_meetings_get_404(client: AsyncClient):
    r = await client.get("/api/v1/meetings/99999")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_meetings_patch(client: AsyncClient, sample_meeting):
    r = await client.patch(
        f"/api/v1/meetings/{sample_meeting.id}",
        json={"title": "Updated Title"},
    )
    assert r.status_code == 200
    assert r.json()["title"] == "Updated Title"


@pytest.mark.asyncio
async def test_meetings_delete(client: AsyncClient, sample_meeting):
    r = await client.delete(f"/api/v1/meetings/{sample_meeting.id}")
    assert r.status_code == 204

    r2 = await client.get(f"/api/v1/meetings/{sample_meeting.id}")
    assert r2.status_code == 404


@pytest.mark.asyncio
async def test_action_items_export_csv(client: AsyncClient):
    r = await client.get("/api/v1/action-items/export/csv")
    assert r.status_code == 200
    assert "text/csv" in r.headers.get("content-type", "")
    assert "content-disposition" in [h.lower() for h in r.headers]
