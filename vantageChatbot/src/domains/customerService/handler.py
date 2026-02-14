from sqlalchemy.orm import Session

from src.core.responseComposer import compose
from src.core.types import InboundMessage, OutboundMessage
from src.storage.models import Ticket


def handle(inbound: InboundMessage, db: Session, user_id: int) -> OutboundMessage:
    ticket = Ticket(tenant_id=inbound.tenant_id, user_id=user_id, status='open', transcript=inbound.text)
    db.add(ticket)
    db.commit()
    return compose(f'Sure — I’ve created ticket #{ticket.id}. A human will reach out.')
