from datetime import datetime
from zoneinfo import ZoneInfo


def to_utc(dt: datetime, timezone: str) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(timezone))
    return dt.astimezone(ZoneInfo('UTC'))


def from_utc(dt: datetime, timezone: str) -> datetime:
    return dt.astimezone(ZoneInfo(timezone))
