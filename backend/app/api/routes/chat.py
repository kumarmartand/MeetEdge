from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.core.deps import get_current_user, DbSession
from app.services.llm_service import LLMService
from app.services.meeting_service import MeetingService

router = APIRouter(prefix="/chat", tags=["chat"], dependencies=[Depends(get_current_user)])


class ChatQueryRequest(BaseModel):
    query: str
    history: list[dict] | None = None


class ChatQueryResponse(BaseModel):
    response: str
    sources: list[dict] | None = None


@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(payload: ChatQueryRequest, db: DbSession):
    llm = LLMService()
    
    if not llm.available:
        return ChatQueryResponse(
            response="Chat integration is not yet configured. Connect your OpenAI API key in the backend environment to enable Answers.",
            sources=[],
        )

    # 1. Fetch user's meeting context
    svc = MeetingService(db)
    # Get recent/all relevant meetings (capping at 20 for context length)
    meetings = await svc.get_all(limit=20)
    
    # 2. Build context string
    context_blocks = []
    for m in meetings:
        block = f"Meeting: {m.title} (Date: {m.start_time.strftime('%Y-%m-%d')})\n"
        if m.summary:
            block += f"Summary: {m.summary}\n"
        if m.summary_key_points and isinstance(m.summary_key_points, dict):
            kps = m.summary_key_points.get("key_points", [])
            if kps:
                block += f"Key Points: {', '.join(kps)}\n"
        elif m.summary_key_points and isinstance(m.summary_key_points, list):
            block += f"Key Points: {', '.join(m.summary_key_points)}\n"
        
        # Add action items
        if m.action_items:
            actions = [f"- {ai.text} (Assignee: {ai.assignee_email or 'Unassigned'})" for ai in m.action_items]
            block += "Action Items:\n" + "\n".join(actions) + "\n"
            
        context_blocks.append(block)

    full_context = "\n---\n".join(context_blocks) if context_blocks else "No past meetings found."

    # 3. Query LLM
    response_text = llm.answer_question(payload.query, payload.history, full_context)
    
    if not response_text:
        raise HTTPException(status_code=500, detail="Failed to generate AI response.")

    return ChatQueryResponse(
        response=response_text,
        sources=[],
    )
