from sqlalchemy.orm import Session

from src.core.responseComposer import compose
from src.core.types import InboundMessage, OutboundMessage
from src.storage.models import FAQ


def handle(inbound: InboundMessage, db: Session) -> OutboundMessage:
    faq = db.query(FAQ).filter(FAQ.tenant_id == inbound.tenant_id).first()
    if faq and faq.question.lower() in inbound.text.lower():
        return compose(faq.answer)
    return compose('Mon-Fri 9-5, Sat 10-2.')
