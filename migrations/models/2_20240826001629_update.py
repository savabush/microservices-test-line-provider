from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "outbox" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "old_message" JSONB NOT NULL,
    "message" JSONB NOT NULL,
    "timestamp" TIMESTAMPTZ NOT NULL  DEFAULT CURRENT_TIMESTAMP,
    "status" VARCHAR(9) NOT NULL  DEFAULT 'UNHANDLED'
);
COMMENT ON COLUMN "outbox"."status" IS 'UNHANDLED: UNHANDLED\nACCESS: ACCESS\nERROR: ERROR';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "outbox";"""
