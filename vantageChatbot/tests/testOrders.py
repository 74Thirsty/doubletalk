from src.core.conversationManager import ConversationManager
from src.core.types import ConversationState


def test_order_state_transition():
    manager = ConversationManager()
    state = manager.next_state(ConversationState(), 'I want to order pizza')
    assert state.name == 'placeOrder'
