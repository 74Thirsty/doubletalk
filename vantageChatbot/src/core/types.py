from dataclasses import dataclass, field
from typing import Any


@dataclass
class ConversationState:
    name: str = 'idle'
    context: dict[str, Any] = field(default_factory=dict)
    expected_inputs: list[str] = field(default_factory=list)
    last_intent: str | None = None
    failed_attempts: int = 0


@dataclass
class InboundMessage:
    tenant_id: int
    channel_type: str
    channel_user_id: str
    provider_message_id: str
    text: str
    raw_payload: dict[str, Any] = field(default_factory=dict)


@dataclass
class OutboundMessage:
    text: str
    quick_replies: list[str] = field(default_factory=list)
