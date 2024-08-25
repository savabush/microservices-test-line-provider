import datetime
import enum
from pydantic import BaseModel

from models.event import Event


class OutboxState(enum.Enum):
    UNHANDLED = "UNHANDLED"
    ACCESS = "ACCESS"
    ERROR = "ERROR"


class OutboxBase(BaseModel):
    old_message: Event
    message: Event
    status: OutboxState = OutboxState.UNHANDLED


class Outbox(OutboxBase):
    id: int
    timestamp: datetime.datetime

    class Config:
        from_attributes = True


class OutboxHandle(BaseModel):
    outbox_id: int
    state: OutboxState
