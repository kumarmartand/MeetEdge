import asyncio
from app.tasks.calendar_tasks import poll_calendar

if __name__ == "__main__":
    result = poll_calendar()
    print("Result:", result)
