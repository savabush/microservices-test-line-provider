import datetime
import logging

from models.event import Event, EventBase
from schemas import EventModel

logger = logging.getLogger(__name__)


class EventRepository:

    @classmethod
    async def create_event(cls, event: Event) -> Event:
        instance = await EventModel.create(**event.dict())
        event_db = Event.from_orm(instance)
        return event_db

    @classmethod
    async def change_event(cls, instance: EventModel, event: EventBase) -> Event:
        for k, v in event.dict().items():
            setattr(instance, k, v)

        await instance.save()
        return Event.from_orm(instance)

    @classmethod
    async def get_event(cls, event_id: int) -> Event:
        instance = await EventModel.get(id=event_id)
        event_db = Event.from_orm(instance)
        return event_db

    @classmethod
    async def event_exists(cls, event_id: int) -> bool:
        return await EventModel.exists(id=event_id)

    @classmethod
    async def get_event_for_update(cls, event_id: int) -> EventModel:
        instance = await EventModel.select_for_update().get(id=event_id)
        return instance

    @classmethod
    async def get_all_events(cls) -> list[Event]:
        instances = await EventModel.all()
        events_db = [Event.from_orm(instance) for instance in instances]
        return events_db

    @classmethod
    async def get_active_events(cls) -> list[Event]:
        instances = await EventModel.filter(deadline__gte=datetime.datetime.now())
        events_db = [Event.from_orm(instance) for instance in instances]
        return events_db
