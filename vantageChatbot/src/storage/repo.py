from sqlalchemy import select
from sqlalchemy.orm import Session

from src.storage import models


def get_or_create_user(session: Session, tenant_id: int, channel_type: str, channel_user_id: str) -> models.User:
    stmt = select(models.User).where(
        models.User.tenant_id == tenant_id,
        models.User.channel_type == channel_type,
        models.User.channel_user_id == channel_user_id,
    )
    user = session.execute(stmt).scalar_one_or_none()
    if user:
        return user
    user = models.User(tenant_id=tenant_id, channel_type=channel_type, channel_user_id=channel_user_id)
    session.add(user)
    session.flush()
    return user
