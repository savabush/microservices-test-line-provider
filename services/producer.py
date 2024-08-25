import asyncio
import logging

import aiokafka

from services.utils import singleton


logger = logging.getLogger(__name__)


@singleton
class KafkaProducer:
    def __init__(self, retries=3, sleep=3):
        self.producer = None 
        self.retries = retries
        self.sleep = sleep
        
    async def start(self):
        self.producer = aiokafka.AIOKafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: v.encode('utf-8'),
        )

        for _ in range(self.retries):
            try:
                await self.producer.start()
                break
            except Exception as e:
                logger.error(f'Error connecting to kafka: {e}')
                await asyncio.sleep(self.sleep)
        else:
            raise Exception('Can not connect to kafka') 
        
        logger.info("Kafka producer started")

    async def send(self, topic: str, value: str):
        await self.producer.send_and_wait(topic, value=value)

    async def close(self):
        await self.producer.stop()
