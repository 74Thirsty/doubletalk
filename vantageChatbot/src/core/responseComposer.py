from src.core.types import OutboundMessage


def compose(text: str, quick_replies: list[str] | None = None) -> OutboundMessage:
    return OutboundMessage(text=text, quick_replies=quick_replies or [])
