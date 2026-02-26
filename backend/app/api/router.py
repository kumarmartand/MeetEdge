from fastapi import APIRouter
from app.api.routes import health, meetings, calendar, action_items, chat, auth, gmail

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(meetings.router)
api_router.include_router(calendar.router)
api_router.include_router(action_items.router)
api_router.include_router(chat.router)
api_router.include_router(gmail.router)
