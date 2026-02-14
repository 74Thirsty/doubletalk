from src.core.router import route_intent
from src.core.types import ConversationState


class ConversationManager:
    def next_state(self, state: ConversationState, text: str) -> ConversationState:
        intent = route_intent(text)
        state.last_intent = intent
        if intent in {'scheduleAppointment', 'placeOrder'} and state.name == 'idle':
            state.name = intent
            state.expected_inputs = ['details']
            return state

        if intent == 'fallback':
            state.failed_attempts += 1
            if state.failed_attempts >= 2:
                state.name = 'handoff_offer'
            return state

        state.name = 'idle'
        state.failed_attempts = 0
        state.expected_inputs = []
        return state
