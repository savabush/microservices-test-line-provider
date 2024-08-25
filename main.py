import uvicorn
import asyncio
from fastapi import FastAPI

import logging.config

from config.logging import LOGGING_CONFIG
from repositories.outbox import OutboxEventService
from routers.event import event_router
from config.db import TortoiseDB
from services.db import DBHealthChecker
from services.producer import KafkaProducer

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(event_router)


@app.get('/health')
async def health_check():
    return 1


async def main():
    await TortoiseDB().connect()
    await DBHealthChecker().init()
    await KafkaProducer().start()
    await OutboxEventService().process_messages()

if __name__ == '__main__':
    logger.info("Start line-provider service")
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_config=LOGGING_CONFIG
    )
    server = uvicorn.Server(config)

    loop = asyncio.get_event_loop()
    loop.create_task(server.serve())
    loop.create_task(main())

    loop.run_forever()
