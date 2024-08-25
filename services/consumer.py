import logging

import aiokafka
import asyncio


logger = logging.getLogger(__name__)


class KafkaConsumer:
    def __init__(self, topics: list[str], retries=3, sleep=3):
        self.retries = retries
        self.sleep = sleep
        self.consumer = aiokafka.AIOKafkaConsumer(
            *topics,
            bootstrap_servers='kafka:9092',
        )

    async def __aenter__(self) -> 'KafkaConsumer':
        for _ in range(self.retries):
            try:
                await self.consumer.start()
                break
            except Exception as e:
                logger.error(f'Error connecting to kafka: {e}')
                await asyncio.sleep(self.sleep)
        else:
            raise Exception('Can not connect to kafka')

        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.consumer.stop()

    async def get_messages(self):
        async for msg in self.consumer:
            yield msg.value.decode('utf-8')