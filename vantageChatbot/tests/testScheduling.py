from datetime import datetime, timedelta

from src.domains.scheduling.availability import generate_slots, has_conflict


def test_generate_slots():
    slots = generate_slots(9, 10, 30)
    assert slots == ['09:00', '09:30']


def test_conflict():
    now = datetime.utcnow()
    existing = [(now, now + timedelta(minutes=30))]
    assert has_conflict(now + timedelta(minutes=10), now + timedelta(minutes=40), existing)
