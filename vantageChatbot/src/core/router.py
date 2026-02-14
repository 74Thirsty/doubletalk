from __future__ import annotations

import re

INTENT_PATTERNS = {
    'greeting': [r'\b(hi|hello|hey)\b'],
    'faqQuery': [r'\b(hours|price|policy|refund)\b'],
    'businessInfo': [r'\b(address|location|phone|website|hours)\b'],
    'scheduleAppointment': [r'\b(book|appointment|schedule|haircut)\b'],
    'rescheduleAppointment': [r'\breschedule\b'],
    'cancelAppointment': [r'\bcancel appointment\b'],
    'appointmentStatus': [r'\bappointment status\b'],
    'setReminderPreference': [r'\breminder\b'],
    'placeOrder': [r'\b(order|buy|pizza)\b'],
    'orderStatus': [r'\border status\b'],
    'humanHandoff': [r'\b(person|human|agent)\b'],
}


def route_intent(text: str) -> str:
    lower = text.lower()
    for intent, patterns in INTENT_PATTERNS.items():
        if any(re.search(pattern, lower) for pattern in patterns):
            return intent
    return 'fallback'
