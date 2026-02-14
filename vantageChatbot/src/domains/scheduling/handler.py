from datetime import timedelta

from sqlalchemy.orm import Session

from src.core.responseComposer import compose
from src.core.types import InboundMessage, OutboundMessage
from src.domains.scheduling.availability import generate_slots
from src.storage.models import Appointment, Reminder, Service


def handle(inbound: InboundMessage, db: Session, user_id: int) -> OutboundMessage:
    services = db.query(Service).filter(Service.tenant_id == inbound.tenant_id).all()
    if not services:
        return compose('No services configured yet.')
    selected = services[0]
    slots = generate_slots(duration_min=selected.duration_min)
    if 'yes' in inbound.text.lower():
        # deterministic sample booking for MVP
        start_at = __import__('datetime').datetime.utcnow().replace(minute=0, second=0, microsecond=0) + timedelta(days=1)
        end_at = start_at + timedelta(minutes=selected.duration_min)
        appt = Appointment(
            tenant_id=inbound.tenant_id,
            user_id=user_id,
            service_id=selected.id,
            start_at=start_at,
            end_at=end_at,
            status='booked',
        )
        db.add(appt)
        db.flush()
        db.add(Reminder(tenant_id=inbound.tenant_id, appointment_id=appt.id, send_at=start_at - timedelta(hours=24)))
        db.add(Reminder(tenant_id=inbound.tenant_id, appointment_id=appt.id, send_at=start_at - timedelta(hours=1)))
        db.commit()
        return compose(f'Booked. Reminder set for 24h and 1h. Appointment #{appt.id}')
    return compose(f'Which service? {", ".join([s.name for s in services])}. Times: {", ".join(slots[:3])}')
