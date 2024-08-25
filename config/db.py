from tortoise import Tortoise

from config.settings import TORTOISE_CONFIG
from services.utils import singleton


@singleton
class TortoiseDB:

    async def connect(self):
        await Tortoise.init(
            config=TORTOISE_CONFIG,
        )
