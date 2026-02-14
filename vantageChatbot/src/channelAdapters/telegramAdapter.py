import httpx

from src.core.types import InboundMessage, OutboundMessage


def parse_update(tenant_id: int, payload: dict) -> InboundMessage:
    message = payload.get('message', {})
    user = message.get('from', {})
    return InboundMessage(
        tenant_id=tenant_id,
        channel_type='telegram',
        channel_user_id=str(user.get('id')),
        provider_message_id=str(message.get('message_id')),
        text=message.get('text', ''),
        raw_payload=payload,
    )


async def send_message(token: str, chat_id: str, outbound: OutboundMessage) -> None:
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    payload = {'chat_id': chat_id, 'text': outbound.text}
    if outbound.quick_replies:
        payload['reply_markup'] = {'keyboard': [[x] for x in outbound.quick_replies], 'resize_keyboard': True}
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json=payload)
