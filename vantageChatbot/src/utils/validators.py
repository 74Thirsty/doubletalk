from pydantic import BaseModel, Field


class InboundPayload(BaseModel):
    tenant_id: int
    channel_type: str
    channel_user_id: str
    provider_message_id: str
    text: str = Field(default='')
