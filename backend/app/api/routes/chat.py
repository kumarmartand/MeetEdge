from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatQueryRequest(BaseModel):
    query: str
    history: list[dict] | None = None


class ChatQueryResponse(BaseModel):
    response: str
    sources: list[dict] | None = None


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(payload: ChatQueryRequest):
    return ChatQueryResponse(
        response="Chat integration is not yet configured. Connect your meeting data to get answers.",
        sources=[],
    )
