import json
import logging

from repositories.event import EventRepository

from models.event import EventBase
from models.outbox import Outbox, OutboxHandle, OutboxState, OutboxBase
from schemas import Outbox as OutboxModel
from services.consumer import KafkaConsumer
from services.utils import singleton, UniversalEncoder

logger = logging.getLogger(__name__)


class OutboxRepository:

    @classmethod
    async def create(cls, outbox: OutboxBase) -> Outbox:
        instance = await OutboxModel.create(
            **json.loads(
                json.dumps(
                    outbox.dict(), 
                    cls=UniversalEncoder
                )
            )
        )
        outbox_db = Outbox.from_orm(instance)
        return outbox_db

    @classmethod
    async def change_status(cls, instance: OutboxModel, status: OutboxState) -> Outbox:
        instance.status = status
        await instance.save()
        return Outbox.from_orm(instance)

    @classmethod
    async def get(cls, outbox_id: int) -> Outbox:
        instance = await OutboxModel.get(id=outbox_id)
        outbox_db = Outbox.from_orm(instance)
        return outbox_db

    @classmethod
    async def exists(cls, outbox_id: int) -> bool:
        return await OutboxModel.exists(id=outbox_id)

    @classmethod
    async def get_for_update(cls, outbox_id: int) -> OutboxModel:
        instance = await OutboxModel.select_for_update().get(id=outbox_id)
        return instance


@singleton
class OutboxEventService(OutboxRepository):

    async def process_messages(self):
        logger.info("Start handling event errors service")
        async with KafkaConsumer(topics=['outbox']) as consumer:
            async for message in consumer.get_messages():
                logger.info("Receive event: %s", message)
                try:
                    await self._handle_message(message)
                except Exception as e:
                    logger.error(e, exc_info=True)

    async def _handle_message(self, message: str):
        outbox = OutboxHandle.parse_raw(message)
        outbox_db = await self.change_status(instance=await self.get_for_update(outbox.outbox_id), status=outbox.state)
        logger.info("Success handle outbox: %s", outbox_db)

        # compensating transaction
        if outbox_db.status == OutboxState.ERROR.value:
            await self._handle_error(old_event=outbox_db.old_message.dict(), event_id=outbox.event_id)

    async def _handle_error(self, old_event: dict, event_id: int):
        logger.error("Compensating transaction for outbox: %s", event_id)
        await EventRepository.change_event(
            instance=await EventRepository.get_event_for_update(event_id),
            event=EventBase.parse_raw(old_event)
        )