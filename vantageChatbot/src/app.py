from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from src.adminApi.routes import router as admin_router
from src.channelAdapters.messengerAdapter import parse_event, verify_signature
from src.channelAdapters.telegramAdapter import parse_update
from src.core.conversationManager import ConversationManager
from src.core.idempotency import seen_provider_message
from src.core.types import ConversationState
from src.domains.customerService.handler import handle as cs_handle
from src.domains.info.handler import handle as info_handle
from src.domains.orders.handler import handle as orders_handle
from src.domains.scheduling.handler import handle as sched_handle
from src.storage.db import Base, engine, get_db
from src.storage.models import Message
from src.storage.repo import get_or_create_user

Base.metadata.create_all(bind=engine)

app = FastAPI(title='Vantage Chatbot')
app.include_router(admin_router)
manager = ConversationManager()


@app.get('/healthz')
def healthz():
    return {'status': 'ok'}


@app.get('/readyz')
def readyz():
    return {'status': 'ready'}


def _process(inbound, db: Session):
    user = get_or_create_user(db, inbound.tenant_id, inbound.channel_type, inbound.channel_user_id)
    if seen_provider_message(db, inbound.tenant_id, inbound.channel_type, inbound.provider_message_id):
        return {'status': 'duplicate'}

    msg = Message(
        tenant_id=inbound.tenant_id,
        user_id=user.id,
        channel_type=inbound.channel_type,
        provider_message_id=inbound.provider_message_id,
        direction='inbound',
        text=inbound.text,
        payload_json=inbound.raw_payload,
    )
    db.add(msg)
    state = manager.next_state(ConversationState(), inbound.text)

    if state.last_intent in {'faqQuery', 'businessInfo'}:
        outbound = info_handle(inbound, db)
    elif state.last_intent in {'scheduleAppointment', 'rescheduleAppointment', 'cancelAppointment'}:
        outbound = sched_handle(inbound, db, user.id)
    elif state.last_intent in {'placeOrder', 'orderStatus'}:
        outbound = orders_handle(inbound, db, user.id)
    elif state.last_intent == 'humanHandoff':
        outbound = cs_handle(inbound, db, user.id)
    else:
        outbound = info_handle(inbound, db)

    db.add(
        Message(
            tenant_id=inbound.tenant_id,
            user_id=user.id,
            channel_type=inbound.channel_type,
            provider_message_id=f"out-{inbound.provider_message_id}",
            direction='outbound',
            text=outbound.text,
            payload_json={'quick_replies': outbound.quick_replies},
        )
    )
    db.commit()
    return {'status': 'processed', 'reply': outbound.text}


@app.post('/webhooks/telegram/{tenant_id}')
def telegram_webhook(tenant_id: int, payload: dict, db: Session = Depends(get_db)):
    inbound = parse_update(tenant_id, payload)
    return _process(inbound, db)


@app.get('/webhooks/messenger/{tenant_id}')
def messenger_verify(tenant_id: int, hub_mode: str = '', hub_challenge: str = '', hub_verify_token: str = ''):
    if hub_mode == 'subscribe' and hub_verify_token:
        return int(hub_challenge or 0)
    raise HTTPException(status_code=403, detail='Verification failed')


@app.post('/webhooks/messenger/{tenant_id}')
async def messenger_webhook(tenant_id: int, request: Request, db: Session = Depends(get_db)):
    body = await request.body()
    signature = request.headers.get('X-Hub-Signature-256')
    if signature and not verify_signature('app_secret', body, signature):
        raise HTTPException(status_code=401, detail='Bad signature')
    payload = await request.json()
    for entry in payload.get('entry', []):
        for event in entry.get('messaging', []):
            inbound = parse_event(tenant_id, event)
            _process(inbound, db)
    return {'status': 'ok'}
