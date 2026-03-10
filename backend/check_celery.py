import asyncio
from app.tasks.bot_tasks import check_upcoming_meetings_for_bot

if __name__ == "__main__":
    result = check_upcoming_meetings_for_bot()
    print("Result:", result)
