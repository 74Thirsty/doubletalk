from sqlalchemy import select
from sqlalchemy.orm import Session

from src.storage.models import Message


def seen_provider_message(session: Session, tenant_id: int, channel_type: str, provider_message_id: str) -> bool:
    stmt = select(Message.id).where(
        Message.tenant_id == tenant_id,
        Message.channel_type == channel_type,
        Message.provider_message_id == provider_message_id,
    )
    return session.execute(stmt).scalar_one_or_none() is not None
