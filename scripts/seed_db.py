#!/usr/bin/env python3
"""
Seed the database with sample meetings for development.
Run from repo root: python scripts/seed_db.py
Requires: MeetEdge backend deps installed, Postgres running (e.g. docker-compose up -d postgres).
"""
import os
import sys
from datetime import datetime, timedelta

BACKEND = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, BACKEND)
os.chdir(BACKEND)

os.environ.setdefault("DATABASE_URL", "postgresql://meetedge:meetedge_dev@localhost:5432/meetedge")


def main():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.models.base import Base
    from app.models.meeting import Meeting
    from app.models.attendee import Attendee
    from app.models.action_item import ActionItem
    from app.models.user import User
    from app.core.security import get_password_hash
    from app.core.database import SessionLocal

    Session = SessionLocal
    session = Session()

    now = datetime.utcnow()
    if now.tzinfo is None:
        from datetime import timezone
        now = now.replace(tzinfo=timezone.utc)

    def td(days=0, hours=0, minutes=0):
        return timedelta(days=days, hours=hours, minutes=minutes)

    titles = [
        "Q3 Planning",
        "API Architecture Review",
        "Daily Standup",
        "Product Roadmap Sync",
        "Security Audit Kickoff",
        "Sprint Retrospective",
        "Customer Discovery Call",
        "Backend Performance Triage",
        "Design System Review",
        "Incident Post-Mortem",
    ]
    statuses = ["completed", "completed", "completed", "completed", "completed", "scheduled", "scheduled", "live", "completed", "completed"]
    meeting_times = [
        (now - td(days=3), now - td(days=3) + td(hours=1)),
        (now - td(days=2), now - td(days=2) + td(hours=2)),
        (now + td(hours=1), now + td(hours=1, minutes=15)),
        (now + td(hours=3), now + td(hours=4)),
        (now - td(days=1), now - td(days=1) + td(minutes=45)),
        (now + td(days=1), now + td(days=1) + td(hours=1)),
        (now + td(hours=2), now + td(hours=2, minutes=30)),
        (now - td(minutes=10), now + td(minutes=50)),
        (now - td(days=5), now - td(days=5) + td(hours=1)),
        (now - td(days=7), now - td(days=7) + td(minutes=30)),
    ]
    sample_attendees = [
        ["alice@example.com", "bob@example.com", "carol@example.com"],
        ["bob@example.com", "carol@example.com", "dave@example.com", "eve@example.com"],
        ["alice@example.com", "bob@example.com", "carol@example.com", "dave@example.com", "eve@example.com", "frank@example.com"],
        ["alice@example.com", "carol@example.com"],
        ["bob@example.com", "dave@example.com", "eve@example.com", "frank@example.com"],
        ["alice@example.com", "bob@example.com"],
        ["carol@example.com", "dave@example.com", "eve@example.com"],
        ["alice@example.com", "bob@example.com", "carol@example.com"],
        ["dave@example.com", "eve@example.com"],
        ["alice@example.com", "bob@example.com", "carol@example.com", "dave@example.com"],
    ]
    action_item_texts = [
        ["Finalize backlog", "Setup CI pipeline", "Update API docs"],
        ["Document architecture decision", "Create ADR", "Share with team"],
        ["Unblock deployment", "Review PRs"],
        ["Prioritize Q3 features", "Stakeholder review"],
        ["Remediation plan", "Security checklist", "Pen test schedule", "Compliance review", "Sign-off"],
        [],
        [],
        [],
        ["Update design tokens", "Component audit"],
        ["Root cause doc", "Action items", "Prevent recurrence"],
    ]
    assignees = ["alice@example.com", "bob@example.com", "carol@example.com", "dave@example.com"]

    print("Seeding Users...")
    for i in range(1, 6):
        email = f"user{i}@example.com"
        exists = session.query(User).filter(User.email == email).first()
        if not exists:
            user = User(
                email=email,
                hashed_password=get_password_hash("password123"),
                is_active=True
            )
            session.add(user)
    session.commit()
    print("Seeded 5 default users (password: password123).")

    for i, (title, status) in enumerate(zip(titles, statuses)):
        start_time, end_time = meeting_times[i]
        external_id = f"seed-event-{i+1}"
        meeting = Meeting(
            title=title,
            start_time=start_time,
            end_time=end_time,
            calendar_id="primary",
            external_id=external_id,
            google_event_id=external_id,
            status=status,
            meet_url=f"https://meet.google.com/abc-defg-hij" if status in ("scheduled", "live") else None,
        )
        session.add(meeting)
        session.flush()
        for email in sample_attendees[i]:
            session.add(Attendee(meeting_id=meeting.id, email=email))
        for j, text in enumerate(action_item_texts[i] if i < len(action_item_texts) else []):
            due = (now + td(days=3 + j)).replace(tzinfo=now.tzinfo) if now.tzinfo else now + td(days=3 + j)
            session.add(ActionItem(
                meeting_id=meeting.id,
                text=text,
                assignee_email=assignees[j % len(assignees)],
                due_date=due,
                status=["open", "in_progress", "completed"][j % 3],
                priority=["low", "medium", "high"][j % 3],
                completed=(j % 3 == 2),
            ))
    session.commit()
    print(f"Seeded {len(titles)} meetings with attendees and action items.")


if __name__ == "__main__":
    main()
