from src.core.router import route_intent


def test_route_schedule():
    assert route_intent('I need a haircut tomorrow') == 'scheduleAppointment'


def test_route_handoff():
    assert route_intent('I want a human') == 'humanHandoff'
