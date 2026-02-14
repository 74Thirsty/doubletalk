from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def generate_slots(start_hour: int = 9, end_hour: int = 17, duration_min: int = 30) -> list[str]:
    slots = []
    now = datetime.now(tz=ZoneInfo('UTC')).replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end = now.replace(hour=end_hour)
    while now < end:
        slots.append(now.strftime('%H:%M'))
        now += timedelta(minutes=duration_min)
    return slots


def has_conflict(start_at: datetime, end_at: datetime, existing: list[tuple[datetime, datetime]]) -> bool:
    return any(start_at < e and end_at > s for s, e in existing)
