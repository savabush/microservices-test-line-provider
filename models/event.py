import datetime
import decimal
import enum
from pydantic import BaseModel, field_validator


class EventState(enum.Enum):
    NEW = "NEW"
    FINISHED_WIN = "FINISHED_WIN"
    FINISHED_LOSE = "FINISHED_LOSE"


class EventBase(BaseModel):
    coefficient: decimal.Decimal
    deadline: datetime.datetime
    state: EventState

    @field_validator('coefficient')
    @classmethod
    def check_validator(cls, v):
        if v.as_tuple().exponent < -2:
            raise ValueError('The sum field must have two digits after the point')
        if len(v.as_tuple().digits) + v.as_tuple().exponent > 4:
            raise ValueError('The sum field must have less or equal than 6 digits before the point')
        return v


class Event(EventBase):
    id: int

    class Config:
        from_attributes = True
