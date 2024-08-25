from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "eventmodel" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "coefficient" DECIMAL(4,2) NOT NULL,
    "deadline" TIMESTAMPTZ NOT NULL,
    "state" VARCHAR(13) NOT NULL  DEFAULT 'NEW'
);
COMMENT ON COLUMN "eventmodel"."coefficient" IS 'Коэффициент';
COMMENT ON COLUMN "eventmodel"."deadline" IS 'Дедлайн';
COMMENT ON COLUMN "eventmodel"."state" IS 'Состояние';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
