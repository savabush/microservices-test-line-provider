from datetime import datetime, timedelta

import pytest

from models.event import Event, EventState
from tests.fixtures.fixtures import *


@pytest.mark.asyncio
async def test_create_event(in_memory_db, event_repository):
    event = Event(id=1, coefficient=1, deadline=datetime.now() + timedelta(minutes=1), state=EventState.NEW)
    created_bet = await event_repository.create_event(event)
    assert created_bet.id is not None
    assert created_bet.id == event.id
    assert created_bet.coefficient == event.coefficient


@pytest.mark.asyncio
async def test_get_all_events(in_memory_db, event_repository):
    event1 = Event(id=2, coefficient=1.5, deadline=datetime.now() + timedelta(days=1), state=EventState.NEW)
    event2 = Event(id=3, coefficient=1.12, deadline=datetime.now() - timedelta(days=1), state=EventState.NEW)
    await event_repository.create_event(event1)
    await event_repository.create_event(event2)
    bets = await event_repository.get_active_events()
    assert len(bets) == 2  # timedelta
    