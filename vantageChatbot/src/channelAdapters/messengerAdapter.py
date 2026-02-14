import hashlib
import hmac

import httpx

from src.core.types import InboundMessage, OutboundMessage


def verify_signature(app_secret: str, body: bytes, signature_header: str | None) -> bool:
    if not signature_header or '=' not in signature_header:
        return False
    _, signature = signature_header.split('=', 1)
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_event(tenant_id: int, event: dict) -> InboundMessage:
    return InboundMessage(
        tenant_id=tenant_id,
        channel_type='messenger',
        channel_user_id=event['sender']['id'],
        provider_message_id=event.get('message', {}).get('mid', event.get('timestamp', '')),
        text=event.get('message', {}).get('text', ''),
        raw_payload=event,
    )


async def send_message(page_token: str, psid: str, outbound: OutboundMessage) -> None:
    url = f'https://graph.facebook.com/v20.0/me/messages?access_token={page_token}'
    payload = {'recipient': {'id': psid}, 'message': {'text': outbound.text}}
    if outbound.quick_replies:
        payload['message']['quick_replies'] = [
            {'content_type': 'text', 'title': qr[:20], 'payload': qr} for qr in outbound.quick_replies
        ]
    async with httpx.AsyncClient(timeout=10) as client:
        await client.post(url, json=payload)
