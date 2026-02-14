from src.core.idempotency import seen_provider_message
from src.storage.db import Base, SessionLocal, engine
from src.storage.models import Message, Tenant, User


def test_idempotency_check():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    tenant = Tenant(name='t1', timezone='UTC')
    db.add(tenant)
    db.flush()
    user = User(tenant_id=tenant.id, channel_type='telegram', channel_user_id='u1')
    db.add(user)
    db.flush()
    db.add(
        Message(
            tenant_id=tenant.id,
            user_id=user.id,
            channel_type='telegram',
            provider_message_id='abc',
            direction='inbound',
            text='hello',
            payload_json={},
        )
    )
    db.commit()
    assert seen_provider_message(db, tenant.id, 'telegram', 'abc') is True
    db.close()
