import asyncio
import sys

from tortoise import connections

import logging
from services.utils import singleton


logger = logging.getLogger(__name__)


@singleton
class DBHealthChecker:
    def __init__(self):
        self.heath_checker = None
        self.conn = None
        self.heath_check_task = None
        
    async def init(self):
        self.conn = connections.get('default')
        self.heath_check_task = asyncio.create_task(self._health_check())
        logger.info("Запущен Postgres health check")

    async def _health_check(self):
        while True:
            await asyncio.sleep(30)
            try:
                await self.conn.execute_query("SELECT 1")
            except Exception as e:
                logger.critical(f"Произошел разрыв соединения с базой данных Postgres {e}")
                sys.exit(1)
