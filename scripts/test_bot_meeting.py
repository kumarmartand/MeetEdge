import os
import sys
from datetime import datetime, timedelta

BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)

os.environ.setdefault("DATABASE_URL", "postgresql://martandsingh@localhost:5432/meetedge")

def main():
    from app.models.meeting import Meeting
    from app.core.database import SessionLocal

    session = SessionLocal()

    now = datetime.utcnow()
    if now.tzinfo is None:
        from datetime import timezone
        now = now.replace(tzinfo=timezone.utc)

    # Starts in 1 minute, ends in 30 minutes
    start_time = now + timedelta(minutes=1)
    end_time = now + timedelta(minutes=30)
    
    external_id = "test-bot-meeting-1"
    
    meeting = Meeting(
        title="Bot Test Meeting",
        start_time=start_time,
        end_time=end_time,
        calendar_id="primary",
        external_id=external_id,
        google_event_id=external_id,
        status="scheduled",
        meet_url="https://meet.google.com/abc-defg-hij", # Valid meet link pattern
    )
    session.add(meeting)
    session.commit()
    print(f"Created Test Meeting: {meeting.id} starting at {meeting.start_time}")

if __name__ == "__main__":
    main()
