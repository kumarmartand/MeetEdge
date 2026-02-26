from datetime import datetime, timezone, timedelta
from dateutil import parser as dateutil_parser


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def parse_google_datetime(dt_str: str) -> datetime:
    if not dt_str:
        raise ValueError("Empty datetime string")
    parsed = dateutil_parser.isoparse(dt_str)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def minutes_until(dt: datetime) -> float:
    now = utcnow()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = dt - now
    return delta.total_seconds() / 60.0


def is_within_minutes(dt: datetime, minutes: int) -> bool:
    now = utcnow()
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    end = now + timedelta(minutes=minutes)
    return now <= dt <= end


def format_duration(start: datetime, end: datetime) -> str:
    if end.tzinfo is None:
        end = end.replace(tzinfo=timezone.utc)
    if start.tzinfo is None:
        start = start.replace(tzinfo=timezone.utc)
    delta = end - start
    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    parts = []
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}m")
    return " ".join(parts)
