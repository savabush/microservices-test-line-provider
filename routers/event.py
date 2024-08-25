import copy
import json
import logging

from fastapi import APIRouter, Path, Depends, HTTPException
from repositories.event import EventRepository
from tortoise.transactions import in_transaction
from models.event import Event, EventBase
from services.producer import KafkaProducer

from repositories.outbox import OutboxRepository

from models.outbox import OutboxBase

logger = logging.getLogger(__name__)
event_router = APIRouter()


@event_router.post(
    '/event',
)
async def create_event(event: Event) -> Event:
    if await EventRepository.event_exists(event.id):
        raise HTTPException(status_code=409, detail="Event already exists")

    event_obj = await EventRepository.create_event(event)
    return event_obj


@event_router.get(
    '/event/{event_id}'
)
async def get_event(event_id: int = Path(title="Event ID"),
                    event_exists: bool = Depends(EventRepository.event_exists)) -> Event:
    if event_exists:
        return await EventRepository.get_event(event_id)
    raise HTTPException(status_code=404, detail="Event not found")


@event_router.patch(
    '/event/{event_id}'
)
async def change_event(
        event: EventBase, event_id: int = Path(title="Event ID"),
        event_exists: bool = Depends(EventRepository.event_exists)) -> Event:
    if not event_exists:
        raise HTTPException(status_code=404, detail="Event not found")
    
    update_bets = False
    async with in_transaction():
        old_event = await EventRepository.get_event_for_update(event_id)
        copy_old_event = copy.deepcopy(Event.from_orm(old_event))
        updated_event = await EventRepository.change_event(instance=old_event, event=event)
        
        if copy_old_event.state != updated_event.state:
            outbox = OutboxBase(
                old_message=copy_old_event,
                message=updated_event,
            )
            outbox_obj = await OutboxRepository.create(outbox)
            update_bets = True

    if update_bets:
        logger.info(f"Send event to Kafka: {updated_event}")
        await KafkaProducer().send('event', json.dumps(
            {
                "outbox_id": outbox_obj.id,
                "event_id": updated_event.id, 
                "state": updated_event.state.value,
             }
        )) 
    
    return updated_event


@event_router.get('/events')
async def get_events() -> list[Event]:
    events = await EventRepository.get_active_events()
    return events
